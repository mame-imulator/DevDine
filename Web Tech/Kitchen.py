import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import time

# -----------------------
# Kitchen Manager (keeps your original logic, lightly adapted)
# -----------------------
class KitchenManager:
    def __init__(self):
        # orders: [dish, bill_number, remarks, locked(bool), ready(bool), batch_id, timestamp_added]
        self.orders = []
        # batches: [dish, batch_id, locked(bool), timestamp_created]
        self.batches = []
        self.batch_counter = 0
        # delivery queue: each = [ "Bill:1001", [ [dish, remarks], ... ] ]
        self.bill_queue = deque()

    # Delivery queue helpers
    def add_bill_to_queue(self, bill_number, items):
        self.bill_queue.append(["Bill:" + str(bill_number), items])

    def feed_next_item_to_kitchen(self):
        if not self.bill_queue:
            return None
        bill = self.bill_queue[0]
        bill_number, items = bill[0], bill[1]
        if not items:
            self.bill_queue.popleft()
            return None
        dish, remarks = items.pop(0)
        # reuse or create unlocked batch
        unlocked_batches = [b[1] for b in self.batches if b[0] == dish and not b[2]]
        if unlocked_batches:
            batch_id = unlocked_batches[-1]
        else:
            self.batch_counter += 1
            batch_id = self.batch_counter
            self.batches.append([dish, batch_id, False, time.time()])
        self.orders.append([dish, bill_number, remarks, False, False, batch_id, time.time()])
        if not items:
            self.bill_queue.popleft()
        return dish

    # Direct dine-in/table order
    def add_order(self, dish, bill_number, remarks=""):
        unlocked_batches = [b[1] for b in self.batches if b[0] == dish and not b[2]]
        if unlocked_batches:
            batch_id = unlocked_batches[-1]
        else:
            self.batch_counter += 1
            batch_id = self.batch_counter
            self.batches.append([dish, batch_id, False, time.time()])
        self.orders.append([dish, bill_number, remarks, False, False, batch_id, time.time()])

    # Lock latest unlocked batch for dish (kept for compatibility)
    def lock_batch(self, dish):
        for i in range(len(self.batches) - 1, -1, -1):
            b = self.batches[i]
            if b[0] == dish and not b[2]:
                b[2] = True
                for o in self.orders:
                    if o[0] == dish and o[5] == b[1]:
                        o[3] = True
                return True
        return False

    # Lock a specific batch (fixes the UI "Confirm" targeting bug)
    def lock_specific_batch(self, dish, batch_id):
        for b in self.batches:
            if b[0] == dish and b[1] == batch_id and not b[2]:
                b[2] = True
                for o in self.orders:
                    if o[0] == dish and o[5] == batch_id:
                        o[3] = True
                return True
        return False

    # Confirm/mark items in a locked batch as ready
    def confirm_batch_done(self, dish, batch_index):
        updated = False
        for o in self.orders:
            if o[0] == dish and o[5] == batch_index and o[3]:
                o[4] = True
                updated = True
        return updated

    # Remove specific ready order (used for "serve" or "pack" or delete)
    def remove_order(self, dish, bill_number, batch_id=None, remove_all_in_same=False):
        if remove_all_in_same:
            self.orders = [o for o in self.orders if not (o[0] == dish and o[1] == bill_number and o[4])]
        else:
            removed = False
            new_orders = []
            for o in self.orders:
                if not removed and o[0] == dish and o[1] == bill_number and o[4]:
                    removed = True
                    continue
                new_orders.append(o)
            self.orders = new_orders

    def get_unlocked_batches(self):
        unlocked = []
        seen = set()
        for o in self.orders:
            dish = o[0]
            if dish in seen:
                continue
            # find orders for the latest unlocked batch for this dish
            batch_ids = [x[5] for x in self.orders if x[0] == dish and not x[3]]
            if not batch_ids:
                continue
            latest_batch = max(batch_ids)
            orders = [x for x in self.orders if x[0] == dish and x[5] == latest_batch]
            if orders:
                unlocked.append((dish, latest_batch, orders))
            seen.add(dish)
        return unlocked

    def get_locked_batches(self):
        locked = []
        added = set()
        for b in self.batches:
            if b[2]:
                dish = b[0]
                if dish in added:
                    pass
                orders = [x for x in self.orders if x[0] == dish and x[5] == b[1] and not x[4]]
                if orders:
                    locked.append((dish, b[1], orders))
                added.add(dish)
        return locked

    def get_ready_bills(self):
        dine_in = []
        delivery = []
        all_bills = set(o[1] for o in self.orders)
        for bill in all_bills:
            bill_orders = [o for o in self.orders if o[1] == bill]
            if bill_orders and all(o[4] for o in bill_orders):
                if any(str(o[1]).startswith("Table:") for o in bill_orders):
                    dine_in.append(bill)
                else:
                    delivery.append(bill)
        # sort dine-in by numeric table
        def table_key(bill):
            for o in self.orders:
                if o[1] == bill and str(o[1]).startswith("Table:"):
                    try:
                        return int(str(o[1]).split(":")[1])
                    except:
                        return float('inf')
            return float('inf')
        dine_in.sort(key=table_key)
        delivery.sort()
        return dine_in, delivery

# -----------------------
# UI / App
# -----------------------
class KitchenApp(tk.Tk):
    def __init__(self, kitchen_manager: KitchenManager):
        super().__init__()
        self.title("Kitchen Dashboard")
        self.geometry("1100x650")
        self.minsize(900, 600)
        self.kitchen = kitchen_manager

        # Set a style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # fonts / sizes
        self.header_font = ("Helvetica", 14, "bold")
        self.card_font = ("Helvetica", 11)
        self.big_font = ("Helvetica", 12)

        # layout: left sidebar + main area
        self.sidebar = ttk.Frame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        self.content = ttk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self.pages = {}
        self._build_pages()

        self.show_page("Orders")

        self.after(1500, self._periodic_feed_and_refresh)

    def _build_sidebar(self):
        title = ttk.Label(self.sidebar, text="Kitchen Hub", font=("Helvetica", 18, "bold"))
        title.pack(pady=(20, 10), padx=12)

        buttons = [
            ("Orders", self.show_orders_page),
            ("Chef", self.show_chef_page),
            ("Dine-In", self.show_dinein_page),
            ("Delivery", self.show_delivery_page),
        ]
        for (txt, cmd) in buttons:
            b = ttk.Button(self.sidebar, text=txt, command=cmd)
            b.pack(fill="x", padx=12, pady=6, ipady=8)

        ttk.Separator(self.sidebar).pack(fill="x", padx=12, pady=8)
        ttk.Label(self.sidebar, text="Quick Actions", font=self.big_font).pack(padx=12, anchor="w")
        add_sample = ttk.Button(self.sidebar, text="Add sample delivery bills", command=self._add_sample_bills)
        add_sample.pack(fill="x", padx=12, pady=(6,4))
        clear_all = ttk.Button(self.sidebar, text="Clear all ready orders", command=self._clear_all_ready)
        clear_all.pack(fill="x", padx=12, pady=(0,6))

    def _build_pages(self):
        orders_page = ttk.Frame(self.content, padding=12)
        self.pages["Orders"] = orders_page
        self._build_orders_page(orders_page)

        chef_page = ttk.Frame(self.content, padding=12)
        self.pages["Chef"] = chef_page
        self._build_chef_page(chef_page)

        dinein_page = ttk.Frame(self.content, padding=12)
        self.pages["Dine-In"] = dinein_page
        self._build_dinein_page(dinein_page)

        delivery_page = ttk.Frame(self.content, padding=12)
        self.pages["Delivery"] = delivery_page
        self._build_delivery_page(delivery_page)

    def show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        page = self.pages.get(name)
        if page:
            page.pack(fill="both", expand=True)
        self._refresh_all_pages()

    def show_orders_page(self):
        self.show_page("Orders")

    def show_chef_page(self):
        self.show_page("Chef")

    def show_dinein_page(self):
        self.show_page("Dine-In")

    def show_delivery_page(self):
        self.show_page("Delivery")

    # ----------------------
    # Orders Page
    # ----------------------
    def _build_orders_page(self, parent):
        frame = parent
        frame.columnconfigure(0, weight=1)
        header = ttk.Label(frame, text="Place Table Order", font=self.header_font)
        header.grid(row=0, column=0, sticky="w", pady=(0,10))

        form = ttk.Frame(frame)
        form.grid(row=1, column=0, sticky="nw")

        ttk.Label(form, text="Table Number:", font=self.big_font).grid(row=0, column=0, sticky="w")
        self.table_entry = ttk.Entry(form, width=10, font=self.big_font)
        self.table_entry.grid(row=0, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(form, text="Dish:", font=self.big_font).grid(row=1, column=0, sticky="w")
        self.menu_items = ["Margherita Pizza", "Spaghetti Bolognese", "Caesar Salad", "Grilled Chicken", "Tomato Soup"]
        self.dish_var = tk.StringVar()
        self.dish_combo = ttk.Combobox(form, textvariable=self.dish_var, values=self.menu_items, state="readonly", font=self.big_font, width=22)
        self.dish_combo.grid(row=1, column=1, padx=8, pady=6, sticky="w")
        self.dish_combo.current(0)

        ttk.Label(form, text="Remarks:", font=self.big_font).grid(row=2, column=0, sticky="w")
        self.remarks_entry = ttk.Entry(form, width=40, font=self.big_font)
        self.remarks_entry.grid(row=2, column=1, padx=8, pady=6, sticky="w")

        place_btn = ttk.Button(form, text="Place Order (Table)", command=self._place_table_order)
        place_btn.grid(row=3, column=0, columnspan=2, pady=(10, 4), sticky="w")

        ttk.Separator(frame).grid(row=4, column=0, sticky="ew", pady=12)

        header2 = ttk.Label(frame, text="Add Delivery Bill to Queue", font=self.header_font)
        header2.grid(row=5, column=0, sticky="w", pady=(0,8))
        delivery_frame = ttk.Frame(frame)
        delivery_frame.grid(row=6, column=0, sticky="nw")

        ttk.Label(delivery_frame, text="Bill #:", font=self.big_font).grid(row=0, column=0, sticky="w")
        self.delivery_bill_entry = ttk.Entry(delivery_frame, width=10, font=self.big_font)
        self.delivery_bill_entry.grid(row=0, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(delivery_frame, text="Items (comma separated):", font=self.big_font).grid(row=1, column=0, sticky="w")
        self.delivery_items_entry = ttk.Entry(delivery_frame, width=45, font=self.big_font)
        self.delivery_items_entry.grid(row=1, column=1, padx=8, pady=6, sticky="w")
        ttk.Label(delivery_frame, text="Format: Dish|remark, Dish2|remark2 (remark optional)", font=("Helvetica", 9)).grid(row=2, column=0, columnspan=2, sticky="w")

        add_delivery_btn = ttk.Button(delivery_frame, text="Add Bill", command=self._add_delivery_bill_from_form)
        add_delivery_btn.grid(row=3, column=0, columnspan=2, pady=(8,0), sticky="w")

    def _place_table_order(self):
        table = self.table_entry.get().strip()
        dish = self.dish_var.get()
        remarks = self.remarks_entry.get().strip()
        if not table.isdigit():
            messagebox.showerror("Input error", "Table number must be numeric.")
            return
        bill = "Table:" + table
        self.kitchen.add_order(dish, bill, remarks)
        messagebox.showinfo("Order placed", f"{dish} for table {table} added.")
        self.table_entry.delete(0, tk.END)
        self.remarks_entry.delete(0, tk.END)
        self._refresh_all_pages()

    def _add_delivery_bill_from_form(self):
        bill_no = self.delivery_bill_entry.get().strip()
        raw_items = self.delivery_items_entry.get().strip()
        if not bill_no:
            messagebox.showerror("Input error", "Please enter a bill number.")
            return
        if not raw_items:
            messagebox.showerror("Input error", "Please enter at least one item.")
            return
        items = []
        for part in raw_items.split(","):
            part = part.strip()
            if not part:
                continue
            if "|" in part:
                dish, remark = [p.strip() for p in part.split("|", 1)]
            else:
                dish, remark = part, ""
            items.append([dish, remark])
        self.kitchen.add_bill_to_queue(bill_no, items)
        messagebox.showinfo("Added", f"Bill {bill_no} added to delivery queue.")
        self.delivery_bill_entry.delete(0, tk.END)
        self.delivery_items_entry.delete(0, tk.END)
        self._refresh_all_pages()

    # ----------------------
    # Chef page
    # ----------------------
    def _build_chef_page(self, parent):
        frame = parent
        header = ttk.Label(frame, text="Chef Dashboard", font=self.header_font)
        header.pack(anchor="w")

        panels = ttk.Frame(frame)
        panels.pack(fill="both", expand=True, pady=8)

        pending_wrap = ttk.Frame(panels)
        pending_wrap.pack(side="left", fill="both", expand=True, padx=(0,8))
        ttk.Label(pending_wrap, text="Pending", font=self.big_font).pack(anchor="w")
        self.pending_canvas = tk.Canvas(pending_wrap, highlightthickness=0)
        self.pending_scroll = ttk.Scrollbar(pending_wrap, orient="vertical", command=self.pending_canvas.yview)
        self.pending_inner = ttk.Frame(self.pending_canvas)
        self.pending_inner.bind("<Configure>", lambda e: self.pending_canvas.configure(scrollregion=self.pending_canvas.bbox("all")))
        self.pending_canvas.create_window((0,0), window=self.pending_inner, anchor="nw")
        self.pending_canvas.configure(yscrollcommand=self.pending_scroll.set)
        self.pending_canvas.pack(side="left", fill="both", expand=True)
        self.pending_scroll.pack(side="right", fill="y")

        preparing_wrap = ttk.Frame(panels)
        preparing_wrap.pack(side="left", fill="both", expand=True, padx=8)
        ttk.Label(preparing_wrap, text="Preparing", font=self.big_font).pack(anchor="w")
        self.prep_canvas = tk.Canvas(preparing_wrap, highlightthickness=0)
        self.prep_scroll = ttk.Scrollbar(preparing_wrap, orient="vertical", command=self.prep_canvas.yview)
        self.prep_inner = ttk.Frame(self.prep_canvas)
        self.prep_inner.bind("<Configure>", lambda e: self.prep_canvas.configure(scrollregion=self.prep_canvas.bbox("all")))
        self.prep_canvas.create_window((0,0), window=self.prep_inner, anchor="nw")
        self.prep_canvas.configure(yscrollcommand=self.prep_scroll.set)
        self.prep_canvas.pack(side="left", fill="both", expand=True)
        self.prep_scroll.pack(side="right", fill="y")

    # ----------------------
    # FIXED FUNCTION
    # ----------------------
    def _populate_chef_panels(self):
        # Clear previous
        for w in self.pending_inner.winfo_children():
            w.destroy()
        for w in self.prep_inner.winfo_children():
            w.destroy()

        # Helper: add placeholder if empty
        def check_empty(container, message):
            if not container.winfo_children():
                lbl = ttk.Label(container, text=message,
                                font=("Helvetica", 10, "italic"))
                lbl.pack(anchor="center", pady=20)

        # ---------------------
        # Pending batches
        # ---------------------
        pending_batches = self.kitchen.get_unlocked_batches()

        for dish, batch_id, orders in pending_batches:
            card = ttk.Frame(self.pending_inner, relief="raised", padding=10)
            card.pack(fill="x", pady=6, padx=6)

            header = ttk.Label(card, text=f"{dish}  —  x{len(orders)}", font=self.card_font)
            header.pack(anchor="w")

            created_ts = None
            for b in self.kitchen.batches:
                if b[1] == batch_id:
                    created_ts = b[3]
                    break
            elapsed = ""
            if created_ts:
                secs = int(time.time() - created_ts)
                m, s = divmod(secs, 60)
                elapsed = f"{m:02d}:{s:02d}"

            ttk.Label(card, text=f"Batch #{batch_id}  •  Pending  •  {elapsed}",
                      font=("Helvetica", 9)).pack(anchor="w", pady=(2,6))

            for o in orders:
                bill, remark = o[1], o[2]
                rtxt = f" — {remark}" if remark else ""
                ttk.Label(card, text=f"{bill}{rtxt}", font=("Helvetica", 9)).pack(anchor="w")

            btn_frame = ttk.Frame(card)
            btn_frame.pack(anchor="e", pady=(6,0))
            confirm_btn = ttk.Button(btn_frame, text="Confirm (Start)",
                                     command=lambda d=dish, b=batch_id: self._lock_batch(d, b))
            confirm_btn.pack(side="left", padx=4)

        check_empty(self.pending_inner, "No pending dishes.")

        # ---------------------
        # Preparing batches
        # ---------------------
        preparing_batches = self.kitchen.get_locked_batches()

        for dish, batch_id, orders in preparing_batches:
            card = ttk.Frame(self.prep_inner, relief="raised", padding=10)
            card.pack(fill="x", pady=6, padx=6)

            header = ttk.Label(card, text=f"{dish}  —  x{len(orders)}", font=self.card_font)
            header.pack(anchor="w")

            ttk.Label(card, text=f"Batch #{batch_id}  •  Preparing",
                      font=("Helvetica", 9)).pack(anchor="w", pady=(2,6))

            for o in orders:
                bill, remark = o[1], o[2]
                rtxt = f" — {remark}" if remark else ""
                ttk.Label(card, text=f"{bill}{rtxt}", font=("Helvetica", 9)).pack(anchor="w")

            btn_frame = ttk.Frame(card)
            btn_frame.pack(anchor="e", pady=(6,0))
            done_btn = ttk.Button(btn_frame, text="Mark Ready",
                                  command=lambda d=dish, i=batch_id: self._mark_batch_done(d, i))
            done_btn.pack(side="left", padx=4)

        check_empty(self.prep_inner, "No dishes being prepared.")

    # ----------------------
    def _lock_batch(self, dish, batch_id):
        ok = self.kitchen.lock_specific_batch(dish, batch_id)
        if ok:
            self._populate_chef_panels()
        else:
            messagebox.showwarning("Lock failed", "Could not lock batch (maybe already locked).")

    def _mark_batch_done(self, dish, batch_index):
        ok = self.kitchen.confirm_batch_done(dish, batch_index)
        if ok:
            messagebox.showinfo("Batch ready", f"{dish} batch {batch_index} marked ready.")
        else:
            messagebox.showwarning("No change", "No items updated.")
        self._populate_chef_panels()
        self._populate_dinein()
        self._populate_delivery()

    # ----------------------
    # Dine-In page
    # ----------------------
    def _build_dinein_page(self, parent):
        frame = parent
        header = ttk.Label(frame, text="Dine-In Ready Dishes", font=self.header_font)
        header.pack(anchor="w")
        self.dinein_list_frame = ttk.Frame(frame)
        self.dinein_list_frame.pack(fill="both", expand=True, pady=8)

    def _populate_dinein(self):
        for w in self.dinein_list_frame.winfo_children():
            w.destroy()
        ready_dishes = [o for o in self.kitchen.orders if o[4] and str(o[1]).startswith("Table:")]
        if not ready_dishes:
            ttk.Label(self.dinein_list_frame, text="No dishes ready.", font=self.big_font).pack(anchor="w", pady=8)
            return
        grouped = {}
        for o in ready_dishes:
            grouped.setdefault(o[1], []).append(o)
        for table in sorted(grouped.keys(), key=lambda x: int(x.split(":")[1])):
            card = ttk.Frame(self.dinein_list_frame, relief="raised", padding=8)
            card.pack(fill="x", pady=6)
            ttk.Label(card, text=f"Table {table.split(':')[1]}", font=self.card_font).pack(anchor="w")
            for item in grouped[table]:
                remark = f" ({item[2]})" if item[2] else ""
                row = ttk.Frame(card)
                row.pack(fill="x", pady=2)
                ttk.Label(row, text=f"{item[0]}{remark}", font=("Helvetica", 10)).pack(side="left")
                served_btn = ttk.Button(row, text="Mark Served",
                                        command=lambda d=item[0], t=item[1]: self._serve_item(d, t))
                served_btn.pack(side="right")

    def _serve_item(self, dish, table):
        removed = False
        new_orders = []
        for o in self.kitchen.orders:
            if not removed and o[0] == dish and o[1] == table and o[4]:
                removed = True
                continue
            new_orders.append(o)
        self.kitchen.orders = new_orders
        messagebox.showinfo("Served", f"{dish} for {table} served.")
        self._refresh_all_pages()

    # ----------------------
    # Delivery page
    # ----------------------
    def _build_delivery_page(self, parent):
        frame = parent
        header = ttk.Label(frame, text="Delivery Ready Bills", font=self.header_font)
        header.pack(anchor="w")
        self.delivery_list_frame = ttk.Frame(frame)
        self.delivery_list_frame.pack(fill="both", expand=True, pady=8)

    def _populate_delivery(self):
        for w in self.delivery_list_frame.winfo_children():
            w.destroy()
        _, delivery_bills = self.kitchen.get_ready_bills()
        if not delivery_bills:
            ttk.Label(self.delivery_list_frame, text="No delivery bills ready.", font=self.big_font).pack(anchor="w", pady=8)
            return
        for bill in delivery_bills:
            card = ttk.Frame(self.delivery_list_frame, relief="raised", padding=8)
            card.pack(fill="x", pady=6)
            ttk.Label(card, text=f"{bill}", font=self.card_font).pack(anchor="w")
            for o in [x for x in self.kitchen.orders if x[1] == bill]:
                remark = f" ({o[2]})" if o[2] else ""
                ttk.Label(card, text=f" - {o[0]}{remark}", font=("Helvetica", 10)).pack(anchor="w")
            btn = ttk.Button(card, text="Mark Packed & Remove", command=lambda b=bill: self._pack_delivery(b))
            btn.pack(anchor="e", pady=6)

    def _pack_delivery(self, bill):
        self.kitchen.orders = [o for o in self.kitchen.orders if o[1] != bill]
        messagebox.showinfo("Packed", f"{bill} marked as packed.")
        self._refresh_all_pages()

    # Universal refresh
    def _refresh_all_pages(self):
        self._populate_chef_panels()
        self._populate_dinein()
        self._populate_delivery()

    def _periodic_feed_and_refresh(self):
        fed = self.kitchen.feed_next_item_to_kitchen()
        if fed:
            print(f">>> Fed {fed} into kitchen")
            self._populate_chef_panels()
        self.after(2500, self._periodic_feed_and_refresh)

    # Quick helpers
    def _add_sample_bills(self):
        self.kitchen.add_bill_to_queue(1001, [["Margherita Pizza", "extra cheese"], ["Caesar Salad", ""]])
        self.kitchen.add_bill_to_queue(1002, [["Tomato Soup", ""], ["Grilled Chicken", "no sauce"], ["Spaghetti Bolognese", "extra meat"]])
        messagebox.showinfo("Added", "Sample bills added to delivery queue.")
        self._refresh_all_pages()

    def _clear_all_ready(self):
        self.kitchen.orders = [o for o in self.kitchen.orders if not o[4]]
        messagebox.showinfo("Cleared", "All ready orders removed.")
        self._refresh_all_pages()

# -----------------------
# Run the app
# -----------------------
if __name__ == "__main__":
    kitchen_manager = KitchenManager()
    kitchen_manager.add_bill_to_queue(2001, [["Margherita Pizza", "extra cheese"], ["Tomato Soup", ""]])
    app = KitchenApp(kitchen_manager)
    app.mainloop()
