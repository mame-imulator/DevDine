import tkinter as tk
from tkinter import ttk, messagebox

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

        self.kitchen.add_order(dish, int(table_number), remarks)
        messagebox.showinfo("Order Placed", f"Order for '{dish}' placed successfully!")
        
        # Clear form
        self.table_entry.delete(0, tk.END)
        self.remarks_entry.delete(0, tk.END)

#Kitchen interface
class KitchenManager:
    def __init__(self):
        self.menu_orders = {}

    def add_order(self, dish_name, table_number, remarks=""):
        order = {"table": table_number, "remarks": remarks}
        if dish_name not in self.menu_orders:
            self.menu_orders[dish_name] = []

        if not self.menu_orders[dish_name] or self.menu_orders[dish_name][-1]["locked"]:
            self.menu_orders[dish_name].append({"locked": False, "orders": []})

        self.menu_orders[dish_name][-1]["orders"].append(order)

    def lock_batch(self, dish_name):
        if dish_name in self.menu_orders:
            for batch in reversed(self.menu_orders[dish_name]):
                if not batch["locked"]:
                    batch["locked"] = True
                    return True
        return False

    def get_unlocked_batches(self):
        """Return dict of dish -> unlocked batch (only latest if multiple)."""
        unlocked = {}
        for dish, batches in self.menu_orders.items():
            for batch in batches:
                if not batch["locked"]:
                    unlocked[dish] = batch
                    break
        return unlocked

    def get_locked_batches(self):
        locked = {}
        for dish, batches in self.menu_orders.items():
            for i, batch in enumerate(batches):
                if batch["locked"]:
                    if dish not in locked:
                        locked[dish] = []
                    locked[dish].append((i, batch))
        return locked

    def confirm_batch_done(self, dish_name, batch_index):
        if dish_name in self.menu_orders:
            if 0 <= batch_index < len(self.menu_orders[dish_name]):
                batch = self.menu_orders[dish_name][batch_index]
                if batch["locked"]:
                    self.menu_orders[dish_name].pop(batch_index)
                    if not self.menu_orders[dish_name]:
                        del self.menu_orders[dish_name]
                    return True
        return False

    def print_all_orders(self):
        for dish, batches in self.menu_orders.items():
            print(f"\n{dish}:")
            for i, batch in enumerate(batches):
                status = "🔒" if batch["locked"] else "🔓"
                print(f"  Batch {i} {status}")
                for order in batch["orders"]:
                    remarks = f" ({order['remarks']})" if order["remarks"] else ""
                    print(f"    - Table {order['table']}{remarks}")


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

    def refresh_interface(self):
        for widget in self.pending_frame.winfo_children():
            widget.destroy()
        for widget in self.preparing_frame.winfo_children():
            widget.destroy()

        # Pending Orders (unlocked)
        unlocked = self.kitchen.get_unlocked_batches()
        for dish, batch in unlocked.items():
            remarks_list = [f"Table {o['table']}: {o['remarks'] or '-'}" for o in batch["orders"]]
            total = len(batch["orders"])

            dish_label = ttk.Label(self.pending_frame, text=f"{dish} x{total}", font=("Arial", 12, "bold"))
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
        for dish, batches in locked.items():
            for index, batch in batches:
                remarks_list = [f"Table {o['table']}: {o['remarks'] or '-'}" for o in batch["orders"]]
                total = len(batch["orders"])

                batch_label = ttk.Label(self.preparing_frame, text=f"{dish} x{total}", font=("Arial", 12, "bold"))
                batch_label.pack(anchor="w")

                for remark in remarks_list:
                    ttk.Label(self.preparing_frame, text=f"  - {remark}").pack(anchor="w")

                done_btn = ttk.Button(
                    self.preparing_frame,
                    text="Done",
                    command=lambda d=dish, i=index: self.mark_done(d, i)
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

def refresh_kitchen_window():
    kitchen_manager.add_order("Tom Yum Kung", 1, "xxxxxx")
    kitchen_window.refresh_interface()
    kitchen_root.after(5000, refresh_kitchen_window)
    
#=================
            
# Main program
if __name__ == "__main__":
    order_manager = KitchenManager()
    kitchen_manager = KitchenManager()

    # Simulating customer orders
    kitchen_manager.add_order("Margherita Pizza", 1, "no olives")
    kitchen_manager.add_order("Margherita Pizza", 2)
    kitchen_manager.add_order("Spaghetti Bolognese", 3, "extra cheese")
    kitchen_manager.add_order("Spaghetti Bolognese", 4, "")
    kitchen_manager.add_order("Caesar Salad", 5, "no dressing")

    order_root = tk.Tk()
    kitchen_root = tk.Tk()
    order_window = CustomerOrderUI(order_root, order_manager)
    kitchen_window = ChefInterface(kitchen_root, kitchen_manager)
    refresh_kitchen_window()
    order_root.mainloop()
    kitchen_root.mainloop()

    # Debug print after GUI closes
    print("\n--- All Orders Submitted ---")
    order_manager.print_all_orders()
