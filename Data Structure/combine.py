import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import time  # For batch timers

# Customer-facing UI
class CustomerOrderUI:
    def __init__(self, root, kitchen_manager):
        self.root = root
        self.kitchen = kitchen_manager
        self.root.title("Customer Order Interface")

        # Sample menu items
        self.menu_items = [
            "Margherita Pizza",
            "Spaghetti Bolognese",
            "Caesar Salad",
            "Grilled Chicken",
            "Tomato Soup"
        ]

        # UI layout
        self.build_interface()

    def build_interface(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()

        # Table number
        ttk.Label(frame, text="Table Number:").grid(column=0, row=0, sticky="w")
        self.table_entry = ttk.Entry(frame, width=10)
        self.table_entry.grid(column=1, row=0)

        # Dish selection
        ttk.Label(frame, text="Select Dish:").grid(column=0, row=1, sticky="w")
        self.dish_var = tk.StringVar()
        self.dish_dropdown = ttk.Combobox(frame, textvariable=self.dish_var, values=self.menu_items, state="readonly")
        self.dish_dropdown.grid(column=1, row=1)
        self.dish_dropdown.current(0)

        # Remarks
        ttk.Label(frame, text="Remarks:").grid(column=0, row=2, sticky="w")
        self.remarks_entry = ttk.Entry(frame, width=30)
        self.remarks_entry.grid(column=1, row=2)

        # Submit button
        self.submit_btn = ttk.Button(frame, text="Place Order", command=self.submit_order)
        self.submit_btn.grid(column=0, row=3, columnspan=2, pady=10)

    def submit_order(self):
        table_number = self.table_entry.get().strip()
        dish = self.dish_var.get()
        remarks = self.remarks_entry.get().strip()

        if not table_number.isdigit():
            messagebox.showerror("Input Error", "Table number must be a number.")
            return

        self.kitchen.add_order(dish, "Table:" + table_number, remarks)
        messagebox.showinfo("Order Placed", f"Order for '{dish}' placed successfully!")
        
        # Clear form
        self.table_entry.delete(0, tk.END)
        self.remarks_entry.delete(0, tk.END)

# Kitchen interface
class KitchenManager:
    def __init__(self):
        # list of [dish, bill_number, remarks, locked, ready, batch, timestamp]
        self.orders = []
        # list of [dish, batch_id, locked, timestamp]
        self.batches = []
        self.batch_counter = 0

        # Queue of bills: each = [bill_number, [ [dish, remarks], ... ]]
        self.bill_queue = deque()

    # ---------------------
    # Queue-related methods
    # ---------------------
    def add_bill_to_queue(self, bill_number, items):
        """Add a bill (delivery order) to the queue."""
        self.bill_queue.append(["Bill:"+str(bill_number), items])

    def feed_next_item_to_kitchen(self):
        """Take one item from the first bill in the queue and add to kitchen."""
        if not self.bill_queue:
            return None

        bill = self.bill_queue[0]
        bill_number, items = bill[0], bill[1]

        if not items:
            self.bill_queue.popleft()
            return None

        dish, remarks = items.pop(0)

        # Find unlocked batch for this dish
        unlocked_batches = [b[1] for b in self.batches if b[0] == dish and not b[2]]
        if unlocked_batches:
            batch_id = unlocked_batches[-1]
        else:
            self.batch_counter += 1
            batch_id = self.batch_counter
            self.batches.append([dish, batch_id, False, time.time()])  # unlocked, with timestamp

        # Add order
        self.orders.append([dish, bill_number, remarks, False, False, batch_id])

        # Remove bill if all items sent
        if not items:
            self.bill_queue.popleft()

        return dish

    # ---------------------
    # Batch and status logic
    # ---------------------
    def lock_batch(self, dish):
        """Lock the latest batch for a dish."""
        for i in range(len(self.batches) - 1, -1, -1):
            b = self.batches[i]
            if b[0] == dish and not b[2]:
                b[2] = True
                for o in self.orders:
                    if o[0] == dish and o[5] == b[1]:
                        o[3] = True
                return True
        return False

    def confirm_batch_done(self, dish, batch_index):
        """Mark batch as ready."""
        updated = False
        for o in self.orders:
            if o[0] == dish and o[5] == batch_index and o[3]:
                o[4] = True
                updated = True
        return updated

    def get_unlocked_batches(self):
        """Return unlocked batches as list of [dish, orders]."""
        unlocked = []
        seen = []

        for o in self.orders:
            dish = o[0]
            if dish not in seen:
                seen.append(dish)
                batch_ids = []
                for x in self.orders:
                    if x[0] == dish and not x[3]:
                        batch_ids.append(x[5])
                if batch_ids:
                    latest_batch = max(batch_ids)
                    orders = [x for x in self.orders if x[0] == dish and x[5] == latest_batch]
                    unlocked.append([dish, orders])
        return unlocked

    def get_locked_batches(self):
        """Return locked batches as list of [dish, batch_id, orders]."""
        locked = []
        added = []

        for o in self.orders:
            dish = o[0]
            if dish not in added:
                added.append(dish)
                for b in self.batches:
                    if b[0] == dish and b[2]:
                        batch_id = b[1]
                        orders = [x for x in self.orders if x[0] == dish and x[5] == batch_id and not x[4]]
                        if orders:
                            locked.append([dish, batch_id, orders])
        return locked

    def add_order(self, dish, bill_number, remarks=""):
        """Directly add a customer order (table order) to kitchen orders."""
        # Find unlocked batch for this dish
        unlocked_batches = [b[1] for b in self.batches if b[0] == dish and not b[2]]
        if unlocked_batches:
            batch_id = unlocked_batches[-1]
        else:
            self.batch_counter += 1
            batch_id = self.batch_counter
            self.batches.append([dish, batch_id, False, time.time()])  # unlocked with timestamp

        self.orders.append([dish, bill_number, remarks, False, False, batch_id])

    def get_ready_bills(self):
        """Return sorted lists: ready dine-in bills and ready delivery bills."""
        dine_in = []
        delivery = []

        all_bills = set(o[1] for o in self.orders)

        for bill in all_bills:
            bill_orders = [o for o in self.orders if o[1] == bill]
            if bill_orders and all(o[4] for o in bill_orders):
                # Check if it's dine-in (bill number starts with "Table: ") or delivery
                if any(str(o[1]).startswith("Table:") for o in bill_orders):
                    dine_in.append(bill)
                else:
                    delivery.append(bill)

        # Sort dine-in bills numerically by table number
        def table_number_key(bill):
            for o in self.orders:
                if o[1] == bill and str(o[1]).startswith("Table:"):
                    return int(str(o[1]).split(":")[1])
            return float('inf')

        dine_in.sort(key=table_number_key)
        delivery.sort()
        return dine_in, delivery

# Chef interface
class ChefInterface:
    def __init__(self, root, kitchen_manager):
        self.root = root
        self.kitchen = kitchen_manager
        self.root.title("Chef Interface")

        # Layout
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.grid()

        self.pending_label = ttk.Label(self.frame, text="Pending Orders", font=("Arial", 14, "bold"))
        self.pending_label.grid(row=0, column=0, sticky="w")

        self.pending_frame = ttk.Frame(self.frame)
        self.pending_frame.grid(row=1, column=0, sticky="nw")

        self.preparing_label = ttk.Label(self.frame, text="Preparing Menu", font=("Arial", 14, "bold"))
        self.preparing_label.grid(row=0, column=1, sticky="w", padx=(40, 0))

        self.preparing_frame = ttk.Frame(self.frame)
        self.preparing_frame.grid(row=1, column=1, sticky="nw", padx=(40, 0))

        self.refresh_interface()
        self.update_timers()  # start the timers

    def refresh_interface(self):
        for widget in self.pending_frame.winfo_children():
            widget.destroy()
        for widget in self.preparing_frame.winfo_children():
            widget.destroy()

        # Pending Orders (unlocked)
        unlocked = self.kitchen.get_unlocked_batches()
        for dish, batch_orders in unlocked:
            remarks_list = [f"{o[1]}: {o[2] or '-'}" for o in batch_orders]
            total = len(batch_orders)

            # Get batch timestamp
            batch_id = batch_orders[0][5]
            batch_time = 0
            for b in self.kitchen.batches:
                if b[1] == batch_id:
                    batch_time = time.time() - b[3]  # timestamp at index 3
                    break
            minutes, seconds = divmod(int(batch_time), 60)
            elapsed_str = f"{minutes:02d}:{seconds:02d}"

            dish_label = ttk.Label(self.pending_frame, text=f"{dish} x{total} [ {elapsed_str} ]", font=("Arial", 12, "bold"))
            dish_label.pack(anchor="w")

            for remark in remarks_list:
                ttk.Label(self.pending_frame, text=f"  - {remark}").pack(anchor="w")

            confirm_btn = ttk.Button(
                self.pending_frame,
                text="Confirm",
                command=lambda d=dish: self.lock_menu(d)
            )
            confirm_btn.pack(anchor="w", pady=(0, 10))

        # Preparing Orders (locked)
        locked = self.kitchen.get_locked_batches()
        for dish, batch_id, batch_orders in locked:
            remarks_list = [f"{o[1]}: {o[2] or '-'}" for o in batch_orders]
            total = len(batch_orders)

            batch_label = ttk.Label(self.preparing_frame, text=f"{dish} x{total}", font=("Arial", 12, "bold"))
            batch_label.pack(anchor="w")

            for remark in remarks_list:
                ttk.Label(self.preparing_frame, text=f"  - {remark}").pack(anchor="w")

            done_btn = ttk.Button(
                self.preparing_frame,
                text="Done",
                command=lambda d=dish, i=batch_id: self.mark_done(d, i)
            )
            done_btn.pack(anchor="w", pady=(0, 10))

    def lock_menu(self, dish_name):
        success = self.kitchen.lock_batch(dish_name)
        if success:
            self.refresh_interface()

    def mark_done(self, dish_name, batch_index):
        success = self.kitchen.confirm_batch_done(dish_name, batch_index)
        if success:
            self.refresh_interface()
            ready_bills = self.kitchen.get_ready_bills()
            if ready_bills:
                messagebox.showinfo("Delivery Ready", f"Bills ready for packing: {', '.join(map(str, ready_bills))}")

    def update_timers(self):
        self.refresh_interface()
        self.root.after(1000, self.update_timers)  # refresh every second

# --- Dine-In Interface for Waiters ---
class DineInInterface:
    def __init__(self, root, kitchen_manager):
        self.root = root
        self.kitchen = kitchen_manager
        self.root.title("Dine-In Orders")

        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.grid()

        ttk.Label(self.frame, text="Ready Dine-In Dishes", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.ready_frame = ttk.Frame(self.frame)
        self.ready_frame.grid(row=1, column=0, sticky="nw")

        self.refresh_interface()

    def refresh_interface(self):
        for widget in self.ready_frame.winfo_children():
            widget.destroy()

        # Only ready dine-in orders (even if partial bill)
        ready_dishes = [o for o in self.kitchen.orders if o[4] and str(o[1]).startswith("Table:")]

        if not ready_dishes:
            ttk.Label(self.ready_frame, text="No dishes ready yet.").pack(anchor="w")
            return

        table_groups = {}
        for dish, table, remarks, _, _, _ in ready_dishes:
            table_groups.setdefault(table, []).append((dish, remarks))

        for table, dishes in sorted(table_groups.items(), key=lambda x: int(x[0].split(":")[1])):
            ttk.Label(self.ready_frame, text=f"Table {table.split(':')[1]}", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5,0))
            for dish, remarks in dishes:
                remark_text = f" ({remarks})" if remarks else ""
                ttk.Label(self.ready_frame, text=f"  - {dish}{remark_text}").pack(anchor="w")
                ttk.Button(
                    self.ready_frame,
                    text="Mark Served",
                    command=lambda d=dish, t=table: self.mark_served(d, t)
                ).pack(anchor="w", pady=(0,5))

    def mark_served(self, dish, table):
        # Remove only this dish from orders
        self.kitchen.orders = [o for o in self.kitchen.orders if not (o[0]==dish and o[1]==table and o[4])]
        messagebox.showinfo("Served", f"{dish} for {table} marked as served.")
        self.refresh_interface()


# --- Delivery Interface for Waiters ---
class DeliveryInterface:
    def __init__(self, root, kitchen_manager):
        self.root = root
        self.kitchen = kitchen_manager
        self.root.title("Delivery Orders")

        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.grid()

        ttk.Label(self.frame, text="Ready Delivery Orders", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.ready_frame = ttk.Frame(self.frame)
        self.ready_frame.grid(row=1, column=0, sticky="nw")

        self.refresh_interface()

    def refresh_interface(self):
        for widget in self.ready_frame.winfo_children():
            widget.destroy()

        _, delivery_bills = self.kitchen.get_ready_bills()

        if not delivery_bills:
            ttk.Label(self.ready_frame, text="No delivery bills ready yet.").pack(anchor="w")
            return

        for bill_number in delivery_bills:
            bill_label = tk.Label(self.ready_frame, text=f"Delivery {bill_number}", font=("Arial", 12, "bold"), bg="#ccffcc")
            bill_label.pack(anchor="w", fill="x", pady=(0,5))

            bill_orders = [o for o in self.kitchen.orders if o[1]==bill_number]
            for dish, _, remarks, _, _, _ in bill_orders:
                remark_text = f" ({remarks})" if remarks else ""
                ttk.Label(self.ready_frame, text=f"  - {dish}{remark_text}").pack(anchor="w")

            ttk.Button(
                self.ready_frame,
                text="Mark as Packed",
                command=lambda b=bill_number: self.mark_packed(b)
            ).pack(anchor="w", pady=(0,10))

    def mark_packed(self, bill_number):
        self.kitchen.orders = [o for o in self.kitchen.orders if o[1]!=bill_number]
        messagebox.showinfo("Packed", f"Delivery {bill_number} marked as packed.")
        self.refresh_interface()
        kitchen_window.refresh_interface()


# ============================
# Main program
# ============================
if __name__ == "__main__":
    kitchen_manager = KitchenManager()

    # Example delivery queue
    kitchen_manager.add_bill_to_queue(1001, [["Margherita Pizza", "extra cheese"], ["Caesar Salad", ""]])
    kitchen_manager.add_bill_to_queue(1002, [["Tomato Soup", ""], ["Grilled Chicken", "no sauce"], ["Spaghetti Bolognese", "extra meat"]])

    order_root = tk.Tk()
    kitchen_root = tk.Tk()
    dinein_root = tk.Tk()
    delivery_root = tk.Tk()

    order_window = CustomerOrderUI(order_root, kitchen_manager)
    kitchen_window = ChefInterface(kitchen_root, kitchen_manager)
    dinein_window = DineInInterface(dinein_root, kitchen_manager)
    delivery_window = DeliveryInterface(delivery_root, kitchen_manager)

    def update_kitchen_ui():
        fed = kitchen_manager.feed_next_item_to_kitchen()
        if fed:
            print(f"---> Sent '{fed}' to kitchen")

        kitchen_window.refresh_interface()
        dinein_window.refresh_interface()
        delivery_window.refresh_interface()

        kitchen_root.after(3000, update_kitchen_ui)

    update_kitchen_ui()

    order_root.mainloop()
    kitchen_root.mainloop()
    dinein_root.mainloop()
    delivery_root.mainloop()