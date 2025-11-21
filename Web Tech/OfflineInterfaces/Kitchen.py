import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import time
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB (update the URI and database/collection as needed)
client = MongoClient('mongodb://localhost:27017/')
db = client['dev']  # change database name here
collection = db['order']  # change collection name here
limit_collection = db['dish limit']  # collection holding dish limits
menu_collection = db['menu']   # collection that stores available menu items

# Debugging helper
try:
    for doc in collection.find({}, {'order_type': 1, 'order_number': 1}):
        print("Loaded:", doc)
except Exception as e:
    print("Mongo debug print failed:", e)


# -----------------------
# Kitchen Manager (with order_type + order_number)
# -----------------------
class KitchenManager:
    def __init__(self):
        # index constants for order structure (10 fields)
        # [dish, order_number, order_type, remarks, locked, ready, batch_id, timestamp, completed, mongo_id]
        self.IDX_DISH = 0
        self.IDX_ORDER_NO = 1
        self.IDX_TYPE = 2
        self.IDX_REMARK = 3
        self.IDX_LOCKED = 4
        self.IDX_READY = 5
        self.IDX_BATCH = 6
        self.IDX_TIMESTAMP = 7
        self.IDX_COMPLETED = 8
        self.IDX_MONGO_ID = 9

        self.orders = []   # all orders
        self.batches = []  # [dish, batch_id, locked, timestamp]
        self.batch_counter = 0

        # queue for delivery bills
        self.bill_queue = deque()

        # dish limits loaded from Mongo: dish -> max items per batch
        self.dish_limits = {}

    # -------------------------------------------------
    # Dish limits loader + helper
    # -------------------------------------------------
    def load_dish_limits(self, limit_records):
        """
        Accepts an iterable of records (dict-like) with keys:
          - 'dish'
          - 'maximum_number_of_dishes_per_batch' (int)
        Populates self.dish_limits.
        """
        for rec in limit_records:
            dish = rec.get("dish")
            size = rec.get("maximum_number_of_dishes_per_batch")
            try:
                size_int = int(size)
            except Exception:
                size_int = None

            if dish and isinstance(size_int, int) and size_int > 0:
                self.dish_limits[dish] = size_int

    # -------------------------------------------------
    # Load available menu from MongoDB
    # -------------------------------------------------
    def load_menu_items(self, records):
        menu = []
        for r in records:
            # Use your actual MongoDB field names:
            dish_name = r.get("dish")
            is_available = r.get("avalable", False)

            if dish_name and is_available:
                menu.append(dish_name)

        return menu

    def get_limit(self, dish):
        """
        Return the maximum number of dishes per batch for `dish`.
        If none is defined, return a very large number (effectively no limit).
        """
        return self.dish_limits.get(dish, 10**9)

    # -------------------------------------------------
    # Find or create an available unlocked batch for dish
    # -------------------------------------------------
    def get_available_batch(self, dish):
        """
        Returns an existing unlocked batch_id for the dish if it is not full.
        Otherwise creates a new batch and returns its id.
        """
        max_size = self.get_limit(dish)

        # Try to find an unlocked batch for this dish that isn't full.
        for b in self.batches:
            if b[0] == dish and not b[2]:  # matching dish and not locked
                batch_id = b[1]
                # count current (not completed) items in that batch
                count = sum(
                    1 for o in self.orders
                    if o[self.IDX_DISH] == dish and o[self.IDX_BATCH] == batch_id and not o[self.IDX_COMPLETED]
                )
                if count < max_size:
                    return batch_id

        # No suitable batch found — create a new unlocked batch
        self.batch_counter += 1
        new_id = self.batch_counter
        self.batches.append([dish, new_id, False, time.time()])
        return new_id

    # -------------------------------------------------
    # Load from MongoDB (handles legacy bill_number)
    # -------------------------------------------------
    def load_orders_from_mongodb(self, mongo_records):
        """
        Loads existing orders from Mongo. For records without batch_id,
        it will allocate an available batch (respecting dish limits).
        If a record already has batch_id, we keep it (legacy data).
        """
        for rec in mongo_records:
            dish = rec.get("dish", "")

            # legacy bill_number support
            order_number = rec.get("order_number", rec.get("bill_number"))

            # infer or read order_type
            order_type = rec.get("order_type")
            if not order_type:
                if isinstance(order_number, str) and str(order_number).startswith("Table:"):
                    order_type = "dine-in"
                else:
                    order_type = "delivery"

            remarks = rec.get("remarks", "")
            locked = bool(rec.get("locked", False))
            ready = bool(rec.get("ready", False))
            batch_id = rec.get("batch_id")
            timestamp = rec.get("timestamp", time.time())
            completed = bool(rec.get("completed", False))
            mongo_id = rec.get("_id")

            # validate timestamp
            if not isinstance(timestamp, (float, int)):
                timestamp = time.time()

            # ensure batch ID: if record had none, allocate according to limits
            if batch_id is None:
                batch_id = self.get_available_batch(dish)
            else:
                # try to coerce to int and update batch_counter
                try:
                    bid = int(batch_id)
                    batch_id = bid
                    if bid > self.batch_counter:
                        self.batch_counter = bid
                except Exception:
                    # leave batch_id as-is if it isn't an int
                    pass

            # keep batch list clean
            if not any(b[1] == batch_id for b in self.batches):
                self.batches.append([dish, batch_id, locked, timestamp])

            # store order
            self.orders.append([
                dish,
                order_number,
                order_type,
                remarks,
                locked,
                ready,
                batch_id,
                timestamp,
                completed,
                mongo_id
            ])

    # -------------------------------------------------
    # Delivery queue
    # -------------------------------------------------
    def add_bill_to_queue(self, order_number, items):
        # Normalize bill number label used internally
        self.bill_queue.append([str(order_number), items])


    def feed_next_item_to_kitchen(self):
        if not self.bill_queue:
            return None

        bill_entry = self.bill_queue[0]
        bill_number, items = bill_entry

        if not items:
            self.bill_queue.popleft()
            return None

        dish, remarks = items.pop(0)

        # attach to latest unlocked batch that isn't full OR create new
        batch_id = self.get_available_batch(dish)

        self.orders.append([
            dish,
            bill_number,
            "delivery",
            remarks,
            False,
            False,
            batch_id,
            time.time(),
            False,
            None
        ])

        if not items:
            self.bill_queue.popleft()

        return dish

    # -------------------------------------------------
    # Add dine-in order directly
    # -------------------------------------------------
    def add_order(self, dish, order_number, remarks=""):
        """
        Adds a dine-in order and returns the batch_id it was assigned to.
        """
        batch_id = self.get_available_batch(dish)

        self.orders.append([
            dish,
            order_number,
            "dine-in",
            remarks,
            False,
            False,
            batch_id,
            time.time(),
            False,
            None
        ])

        return batch_id

    # -------------------------------------------------
    # Batch controls
    # -------------------------------------------------
    def lock_specific_batch(self, dish, batch_id):
        for b in self.batches:
            if b[0] == dish and b[1] == batch_id and not b[2]:
                b[2] = True
                for o in self.orders:
                    if o[self.IDX_DISH] == dish and o[self.IDX_BATCH] == batch_id:
                        o[self.IDX_LOCKED] = True
                return True
        return False

    def confirm_batch_done(self, dish, batch_id):
        updated = False
        for o in self.orders:
            if (
                o[self.IDX_DISH] == dish and
                o[self.IDX_BATCH] == batch_id and
                o[self.IDX_LOCKED] and
                not o[self.IDX_COMPLETED]
            ):
                o[self.IDX_READY] = True
                updated = True

                if o[self.IDX_MONGO_ID]:
                    try:
                        collection.update_one(
                            {"_id": ObjectId(o[self.IDX_MONGO_ID])},
                            {"$set": {"ready": True}}
                        )
                    except Exception:
                        pass

        return updated

    # -------------------------------------------------
    # Getters for dashboard
    # -------------------------------------------------
    def get_unlocked_batches(self):
        """
        Return a list of (dish, batch_id, orders_in_batch) for ALL unlocked batches
        that still have at least one incomplete order.
        """
        result = []

        # Organize orders by (dish, batch_id)
        orders_by_batch = {}
        for o in self.orders:
            dish = o[self.IDX_DISH]
            batch = o[self.IDX_BATCH]
            completed = o[self.IDX_COMPLETED]

            if completed:
                continue  # ignore completed orders

            orders_by_batch.setdefault((dish, batch), []).append(o)

        # Filter by batches table (must exist + unlocked)
        for (dish, batch), orders in orders_by_batch.items():

            # Find batch info
            batch_info = next(
                (b for b in self.batches if b[0] == dish and b[1] == batch),
                None
            )
            if not batch_info:
                continue

            locked = batch_info[2]
            if locked:
                continue  # skip locked batches

            result.append((dish, batch, orders))

        return result


    def get_locked_batches(self):
        """
        Return a list of (dish, batch_id, orders_in_batch) for ALL locked batches,
        whether orders are complete or not. (Your UI may filter further if needed.)
        """
        result = []

        # Organize orders by (dish, batch_id)
        orders_by_batch = {}
        for o in self.orders:
            dish = o[self.IDX_DISH]
            batch = o[self.IDX_BATCH]
            orders_by_batch.setdefault((dish, batch), []).append(o)

        # Filter batches: must exist + locked
        for (dish, batch), orders in orders_by_batch.items():
            batch_info = next(
                (b for b in self.batches if b[0] == dish and b[1] == batch),
                None
            )
            if not batch_info:
                continue

            locked = batch_info[2]
            if not locked:
                continue  # skip unlocked batches

            result.append((dish, batch, orders))

        return result

    # -------------------------------------------------
    # Order type–aware ready bill detection
    # -------------------------------------------------
    def get_ready_bills(self):
        dine = []
        delivery = []

        # normalize order numbers to strings to avoid type mismatch between ints and "Bill:xxx"
        order_numbers = {
            str(o[self.IDX_ORDER_NO])
            for o in self.orders
            if not o[self.IDX_COMPLETED]
        }

        for order_no in order_numbers:
            group = [
                o for o in self.orders
                if str(o[self.IDX_ORDER_NO]) == order_no and not o[self.IDX_COMPLETED]
            ]

            if group and all(o[self.IDX_READY] for o in group):
                order_type = group[0][self.IDX_TYPE]
                if order_type == "dine-in":
                    dine.append(order_no)
                else:
                    delivery.append(order_no)

        # nice sorting for tables
        def table_key(x):
            try:
                return int(x)
            except:
                return float("inf")

        dine.sort(key=table_key)
        delivery.sort()

        return dine, delivery

    # -------------------------------------------------
    # UI App
    # -------------------------------------------------
class KitchenApp(tk.Tk):
    def __init__(self, kitchen):
        super().__init__()

        # FIX: assign kitchen BEFORE using it
        self.kitchen = kitchen

        # Load menu items from Mongo
        try:
            menu_records = list(menu_collection.find({}))
            self.menu_items = self.kitchen.load_menu_items(menu_records)
            if not self.menu_items:
                self.menu_items = ["(No items available)"]
        except Exception as e:
            print("Menu load failed:", e)
            self.menu_items = ["(Menu load error)"]

        self.title("Kitchen Dashboard")
        self.geometry("1100x650")

        # holds (label_widget, batch_id, status, created_timestamp)
        self.timestamp_labels = []

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.header_font = ("Helvetica", 14, "bold")
        self.big_font = ("Helvetica", 12)
        self.card_font = ("Helvetica", 11)

        # Sidebar + content
        self.sidebar = ttk.Frame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        self.content = ttk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self.pages = {}
        self._build_pages()

        self.show_page("Orders")

        # set up periodic feed and timestamp refresher
        self.after(1500, self._periodic_feed_and_refresh)
        self.after(1000, self._start_timestamp_refresher)


    def _build_sidebar(self):
        ttk.Label(self.sidebar, text="Kitchen Hub", font=("Helvetica", 18, "bold")).pack(
            pady=(20, 10), padx=12
        )

        # ---- Page navigation buttons ----
        ttk.Button(self.sidebar, text="Orders", command=self.show_orders_page).pack(
            fill="x", padx=12, pady=6, ipady=8
        )
        ttk.Button(self.sidebar, text="Chef", command=self.show_chef_page).pack(
            fill="x", padx=12, pady=6, ipady=8
        )
        ttk.Button(self.sidebar, text="Dine-In", command=self.show_dinein_page).pack(
            fill="x", padx=12, pady=6, ipady=8
        )
        ttk.Button(self.sidebar, text="Delivery", command=self.show_delivery_page).pack(
            fill="x", padx=12, pady=6, ipady=8
        )

        ttk.Separator(self.sidebar).pack(fill="x", padx=12, pady=8)

        ttk.Label(self.sidebar, text="Quick Actions", font=self.big_font).pack(
            anchor="w", padx=12
        )

        ttk.Button(
            self.sidebar,
            text="Add sample delivery bills",
            command=self._add_sample_bills,
        ).pack(fill="x", padx=12, pady=(6, 4))

        ttk.Button(
            self.sidebar,
            text="Clear all completed orders",
            command=self._clear_all_ready,
        ).pack(fill="x", padx=12, pady=(0, 6))


    # ---- Page Switchers (fixes AttributeError) ----

    def show_orders_page(self):
        self.show_page("Orders")

    def show_chef_page(self):
        self.show_page("Chef")

    def show_dinein_page(self):
        self.show_page("Dine-In")

    def show_delivery_page(self):
        self.show_page("Delivery")


    def _build_pages(self):
        self.pages["Orders"] = ttk.Frame(self.content, padding=12)
        self._build_orders_page(self.pages["Orders"])

        self.pages["Chef"] = ttk.Frame(self.content, padding=12)
        self._build_chef_page(self.pages["Chef"])

        self.pages["Dine-In"] = ttk.Frame(self.content, padding=12)
        self._build_dinein_page(self.pages["Dine-In"])

        self.pages["Delivery"] = ttk.Frame(self.content, padding=12)
        self._build_delivery_page(self.pages["Delivery"])

    def show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        self._refresh_all_pages()

    # ORDER PAGE (unchanged except naming)
    def _build_orders_page(self, parent):
        frame = parent
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Place Order", font=self.header_font).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        form = ttk.Frame(frame)
        form.grid(row=1, column=0, sticky="nw")

        # -------- ORDER TYPE RADIO BUTTONS --------
        ttk.Label(form, text="Order Type:", font=self.big_font).grid(row=0, column=0, sticky="w")

        self.order_type_var = tk.StringVar(value="dine-in")
        ttk.Radiobutton(form, text="Dine-In", value="dine-in",
                        variable=self.order_type_var,
                        command=self._toggle_order_type_inputs).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(form, text="Delivery", value="delivery",
                        variable=self.order_type_var,
                        command=self._toggle_order_type_inputs).grid(row=0, column=2, padx=10)

        # -------- TABLE / BILL INPUT (dynamic) --------
        ttk.Label(form, text="Table / Bill Number:", font=self.big_font).grid(row=1, column=0, sticky="w")
        self.order_number_entry = ttk.Entry(form, width=12, font=self.big_font)
        self.order_number_entry.grid(row=1, column=1, padx=8, sticky="w")

        # -------- DISH SELECT --------
        ttk.Label(form, text="Dish:", font=self.big_font).grid(row=2, column=0, sticky="w")

        self.dish_var = tk.StringVar()

        dish_box = ttk.Combobox(
            form,
            textvariable=self.dish_var,
            values=self.menu_items,     # <-- comes from DB now
            state="readonly",
            font=self.big_font,
            width=22
        )

        dish_box.grid(row=2, column=1, padx=8, sticky="w")
        self.dish_var.set(self.menu_items[0])

        # -------- REMARKS --------
        ttk.Label(form, text="Remarks:", font=self.big_font).grid(row=3, column=0, sticky="w")
        self.remarks_entry = ttk.Entry(form, width=40, font=self.big_font)
        self.remarks_entry.grid(row=3, column=1, padx=8, sticky="w")

        # -------- SUBMIT BUTTON --------
        ttk.Button(form, text="Place Order",
                command=self._place_single_order).grid(
            row=4, column=0, columnspan=2, pady=12
        )


    # -------------------------------------------------
    # CHEF PAGE — with ORDER TYPE ADDED
    # -------------------------------------------------
    def _build_chef_page(self, parent):
        frame = parent
        ttk.Label(frame, text="Chef Dashboard", font=self.header_font).pack(anchor="w")

        wrapper = ttk.Frame(frame)
        wrapper.pack(fill="both", expand=True)

        # PENDING COLUMN
        left = ttk.Frame(wrapper)
        left.pack(side="left", fill="both", expand=True, padx=6)
        ttk.Label(left, text="Pending", font=self.big_font).pack(anchor="w")

        self.pending_canvas = tk.Canvas(left, highlightthickness=0)
        self.pending_inner = ttk.Frame(self.pending_canvas)
        self.pending_canvas.create_window((0, 0), window=self.pending_inner,
                                          anchor="nw")
        self.pending_canvas.pack(side="left", fill="both", expand=True)
        pending_scrollbar = ttk.Scrollbar(left, orient="vertical",
                      command=self.pending_canvas.yview)
        pending_scrollbar.pack(side="right", fill="y")
        self.pending_canvas.configure(yscrollcommand=pending_scrollbar.set)
        self.pending_inner.bind(
            "<Configure>",
            lambda e: self.pending_canvas.configure(scrollregion=self.pending_canvas.bbox("all"))
        )

        # PREPARING COLUMN
        right = ttk.Frame(wrapper)
        right.pack(side="left", fill="both", expand=True, padx=6)
        ttk.Label(right, text="Preparing", font=self.big_font).pack(anchor="w")

        self.prep_canvas = tk.Canvas(right, highlightthickness=0)
        self.prep_inner = ttk.Frame(self.prep_canvas)
        self.prep_canvas.create_window((0, 0), window=self.prep_inner,
                                       anchor="nw")
        self.prep_canvas.pack(side="left", fill="both", expand=True)
        prep_scrollbar = ttk.Scrollbar(right, orient="vertical",
                      command=self.prep_canvas.yview)
        prep_scrollbar.pack(side="right", fill="y")
        self.prep_canvas.configure(yscrollcommand=prep_scrollbar.set)
        self.prep_inner.bind(
            "<Configure>",
            lambda e: self.prep_canvas.configure(scrollregion=self.prep_canvas.bbox("all"))
        )

    # -------------------------------------------------
    # Populate Chef panels (FIXED to show ORDER TYPE)
    # -------------------------------------------------
    def _populate_chef_panels(self):
        # Clear old cards
        for w in self.pending_inner.winfo_children():
            w.destroy()
        for w in self.prep_inner.winfo_children():
            w.destroy()

        # reset timestamp label tracking (we'll repopulate)
        self.timestamp_labels = []

        pending = self.kitchen.get_unlocked_batches()
        preparing = self.kitchen.get_locked_batches()

        # Reusable function
        # Patched version of add_batch_cards() for your _populate_chef_panels()
        def add_batch_cards(container, batches, status_label):
            # If empty → show placeholder
            if not batches:
                placeholder = ttk.Label(
                    container,
                    text=f"No {status_label.lower()} batches.",
                    font=("Helvetica", 10, "italic")
                )
                placeholder.pack(anchor="w", pady=6, padx=6)
                return

            # Otherwise render normal cards
            for dish, batch_id, orders in batches:
                card = ttk.Frame(container, relief="raised", padding=10)
                card.pack(fill="x", pady=6, padx=6)

                ttk.Label(
                    card, text=f"{dish} — x{len(orders)}", font=self.card_font
                ).pack(anchor="w")

                # find timestamp
                created = None
                for b in self.kitchen.batches:
                    if b[1] == batch_id:
                        created = b[3]
                        break

                if created:
                    sec = int(time.time() - created)
                    m, s = divmod(sec, 60)
                    lbl = ttk.Label(
                        card,
                        text=f"Batch #{batch_id}  •  {status_label}  •  {m:02d}:{s:02d}",
                        font=("Helvetica", 9),
                    )
                    lbl.pack(anchor="w", pady=(2, 6))
                    self.timestamp_labels.append((lbl, batch_id, status_label, created))
                else:
                    ttk.Label(
                        card,
                        text=f"Batch #{batch_id}  •  {status_label}",
                        font=("Helvetica", 9),
                    ).pack(anchor="w", pady=(2, 6))

                for o in orders:
                    order_no = o[self.kitchen.IDX_ORDER_NO]
                    order_type = o[self.kitchen.IDX_TYPE]
                    remark = o[self.kitchen.IDX_REMARK]

                    type_str = " (dine-in)" if order_type == "dine-in" else " (delivery)"
                    remark_str = f" — {remark}" if remark else ""

                    ttk.Label(
                        card,
                        text=f"{order_no}{type_str}{remark_str}",
                        font=("Helvetica", 9),
                    ).pack(anchor="w")

                if status_label == "Pending":
                    ttk.Button(
                        card,
                        text="Confirm (Start)",
                        command=lambda d=dish, b=batch_id: self._lock_batch(d, b),
                    ).pack(anchor="e", pady=4)
                else:
                    ttk.Button(
                        card,
                        text="Mark Ready",
                        command=lambda d=dish, b=batch_id: self._mark_batch_done(d, b),
                    ).pack(anchor="e", pady=4)

        # Fill panels
        add_batch_cards(self.pending_inner, pending, "Pending")
        add_batch_cards(self.prep_inner, preparing, "Preparing")

    # -------------------------------------------------
    # DINE-IN PAGE
    # -------------------------------------------------
    def _build_dinein_page(self, parent):
        ttk.Label(parent, text="Dine-In Ready Dishes",
                  font=self.header_font).pack(anchor="w")
        self.dinein_list = ttk.Frame(parent)
        self.dinein_list.pack(fill="both", expand=True, pady=8)

    def _populate_dinein(self):
        for w in self.dinein_list.winfo_children():
            w.destroy()

        ready = [
            o for o in self.kitchen.orders
            if o[self.kitchen.IDX_READY] and
               not o[self.kitchen.IDX_COMPLETED] and
               o[self.kitchen.IDX_TYPE] == "dine-in"
        ]

        if not ready:
            ttk.Label(self.dinein_list, text="No dishes ready.",
                      font=self.big_font).pack(anchor="w")
            return

        groups = {}
        for o in ready:
            groups.setdefault(str(o[self.kitchen.IDX_ORDER_NO]), []).append(o)

        def tkey(x):
            try:
                return int(x.split(":")[1])
            except:
                return float("inf")

        for table in sorted(groups.keys(), key=tkey):
            card = ttk.Frame(self.dinein_list, relief="raised", padding=8)
            card.pack(fill="x", pady=6)

            label = table.split(":")[1] if ":" in table else table
            ttk.Label(card, text=f"Table {label}", font=self.card_font).pack(
                anchor="w"
            )

            for item in groups[table]:
                remark = f" ({item[self.kitchen.IDX_REMARK]})" if item[self.kitchen.IDX_REMARK] else ""
                row = ttk.Frame(card)
                row.pack(fill="x", pady=2)

                ttk.Label(row,
                          text=f"{item[self.kitchen.IDX_DISH]}{remark}",
                          font=("Helvetica", 10)).pack(side="left")

                ttk.Button(
                    row,
                    text="Mark Completed",
                    command=lambda it=item: self._serve_item(it),
                ).pack(side="right")

    # serve item
    def _serve_item(self, item):
        for o in self.kitchen.orders:
            if o is item and o[self.kitchen.IDX_READY] and not o[self.kitchen.IDX_COMPLETED]:
                o[self.kitchen.IDX_COMPLETED] = True

                if o[self.kitchen.IDX_MONGO_ID]:
                    try:
                        collection.update_one(
                            {"_id": ObjectId(o[self.kitchen.IDX_MONGO_ID])},
                            {"$set": {"completed": True}},
                        )
                    except Exception:
                        pass

                messagebox.showinfo(
                    "Served",
                    f"{o[self.kitchen.IDX_DISH]} for {o[self.kitchen.IDX_ORDER_NO]} completed.",
                )
                break

        self._refresh_all_pages()

    # -------------------------------------------------
    # DELIVERY PAGE
    # -------------------------------------------------
    def _build_delivery_page(self, parent):
        ttk.Label(parent, text="Delivery Ready Bills",
                  font=self.header_font).pack(anchor="w")
        self.delivery_list = ttk.Frame(parent)
        self.delivery_list.pack(fill="both", expand=True, pady=8)

    def _populate_delivery(self):
        for w in self.delivery_list.winfo_children():
            w.destroy()

        _, delivery = self.kitchen.get_ready_bills()

        if not delivery:
            ttk.Label(self.delivery_list, text="No delivery bills ready.",
                      font=self.big_font).pack(anchor="w")
            return

        for bill in delivery:
            card = ttk.Frame(self.delivery_list, relief="raised", padding=8)
            card.pack(fill="x", pady=6)

            ttk.Label(card, text=bill, font=self.card_font).pack(anchor="w")

            for o in [
                x for x in self.kitchen.orders
                if str(x[self.kitchen.IDX_ORDER_NO]) == bill and not x[self.kitchen.IDX_COMPLETED]
            ]:
                r = f" ({o[self.kitchen.IDX_REMARK]})" if o[self.kitchen.IDX_REMARK] else ""
                ttk.Label(card,
                          text=f" - {o[self.kitchen.IDX_DISH]}{r}",
                          font=("Helvetica", 10)).pack(anchor="w")

            ttk.Button(
                card, text="Mark Completed",
                command=lambda b=bill: self._pack_delivery(b)
            ).pack(anchor="e", pady=6)

    def _pack_delivery(self, bill):
        for o in self.kitchen.orders:
            if str(o[self.kitchen.IDX_ORDER_NO]) == bill and o[self.kitchen.IDX_READY] and not o[self.kitchen.IDX_COMPLETED]:
                o[self.kitchen.IDX_COMPLETED] = True

                if o[self.kitchen.IDX_MONGO_ID]:
                    try:
                        collection.update_one(
                            {"_id": ObjectId(o[self.kitchen.IDX_MONGO_ID])},
                            {"$set": {"completed": True}},
                        )
                    except Exception:
                        pass

        messagebox.showinfo("Packed", f"{bill} marked completed.")
        self._refresh_all_pages()

    # -------------------------------------------------
    # GLOBAL REFRESH
    # -------------------------------------------------
    def _refresh_all_pages(self):
        self._populate_chef_panels()
        self._populate_dinein()
        self._populate_delivery()

    # periodic feed
    def _periodic_feed_and_refresh(self):
        fed = self.kitchen.feed_next_item_to_kitchen()
        if fed:
            print("Fed:", fed)
            self._refresh_all_pages()
        self.after(2500, self._periodic_feed_and_refresh)

    # timestamp updater
    def _start_timestamp_refresher(self):
        now = time.time()
        new_list = []
        for entry in list(self.timestamp_labels):
            try:
                lbl, batch_id, status, created = entry
                sec = int(now - created)
                m, s = divmod(sec, 60)
                lbl.config(text=f"Batch #{batch_id} • {status} • {m:02d}:{s:02d}")
                new_list.append(entry)
            except Exception:
                # skip problematic entries
                pass
        # replace list to keep references accurate
        self.timestamp_labels = new_list
        self.after(1000, self._start_timestamp_refresher)

    # samples
    def _add_sample_bills(self):
        self.kitchen.add_bill_to_queue(
            1001,
            [["Margherita Pizza", "extra cheese"], ["Caesar Salad", ""]],
        )
        self.kitchen.add_bill_to_queue(
            1002,
            [["Tomato Soup", ""], ["Grilled Chicken", "no sauce"],
             ["Spaghetti Bolognese", "extra meat"]],
        )
        messagebox.showinfo("Added", "Sample bills added.")
        self._refresh_all_pages()

    def _clear_all_ready(self):
        self.kitchen.orders = [
            o for o in self.kitchen.orders if not o[self.kitchen.IDX_COMPLETED]
        ]
        messagebox.showinfo("Cleared", "Completed cleared.")
        self._refresh_all_pages()

    # -------------------------------------------------
    # New / Fixed helper methods for missing functionality
    # -------------------------------------------------
    def _place_single_order(self):
        order_type = self.order_type_var.get()
        order_no = self.order_number_entry.get().strip()
        dish = self.dish_var.get()
        remarks = self.remarks_entry.get().strip()

        if not order_no:
            messagebox.showwarning("Missing", "Please enter table/bill number.")
            return

        # Add to kitchen system
        batch_id = self.kitchen.add_order(dish, order_no, remarks)
        print("Assigned batch:", batch_id)

        # Save to Mongo
        try:
            collection.insert_one({
                "dish": dish,
                "order_number": order_no,
                "order_type": order_type,
                "remarks": remarks,
                "locked": False,
                "ready": False,
                "batch_id": int(batch_id) if batch_id is not None else None,
                "timestamp": time.time(),
                "completed": False,
            })
        except Exception:
            pass

        if order_type == "dine-in":
            msg = f"{dish} for Table {order_no} placed."
        else:
            msg = f"{dish} for Delivery Bill {order_no} placed."

        messagebox.showinfo("Placed", msg)
        self._refresh_all_pages()

    def _toggle_order_type_inputs(self):
        """Updates the label depending on Dine-In vs Delivery"""
        if self.order_type_var.get() == "dine-in":
            self.order_number_entry.configure()
        else:
            self.order_number_entry.configure()

    def _lock_batch(self, dish, batch_id):
        ok = self.kitchen.lock_specific_batch(dish, batch_id)
        if ok:
            messagebox.showinfo("Locked", f"Batch {batch_id} of {dish} locked (preparing).")
        else:
            messagebox.showwarning("Failed", f"Could not lock batch {batch_id} for {dish}.")
        self._refresh_all_pages()

    def _mark_batch_done(self, dish, batch_id):
        updated = self.kitchen.confirm_batch_done(dish, batch_id)
        if updated:
            messagebox.showinfo("Ready", f"Batch {batch_id} of {dish} marked ready.")
        else:
            messagebox.showwarning("Nothing", f"No items updated for {dish} batch {batch_id}.")
        self._refresh_all_pages()

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
if __name__ == "__main__":
    km = KitchenManager()

    # Load dish limits from MongoDB (if collection exists)
    try:
        limits = list(limit_collection.find({}))
        km.load_dish_limits(limits)
        print("Loaded dish limits:", km.dish_limits)
    except Exception as e:
        print("Failed loading dish limits:", e)

    try:
        data = list(collection.find({}))
        km.load_orders_from_mongodb(data)
    except Exception as e:
        print("MongoDB load failed:", e)

    app = KitchenApp(km)
    app.mainloop()
