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
        # Instead of dict of dishes, store all orders in a list
        self.orders = []  # each entry: {"dish": str, "table": int, "remarks": str, "locked": bool, "batch": int}
        self.batch_counter = 0  # track batches

    def add_order(self, dish_name, table_number, remarks=""):
        """Add a new order for a dish."""
        # Find any unlocked batch for this dish
        unlocked_batches = [o["batch"] for o in self.orders if o["dish"] == dish_name and not o["locked"]]
        if unlocked_batches:
            batch_id = unlocked_batches[-1]
        else:
            self.batch_counter += 1
            batch_id = self.batch_counter

        self.orders.append({
            "dish": dish_name,
            "table": table_number,
            "remarks": remarks,
            "locked": False,
            "batch": batch_id
        })

    def lock_batch(self, dish_name):
        """Lock the most recent unlocked batch for this dish."""
        # Find latest unlocked batch for this dish
        batches = sorted(
            {o["batch"] for o in self.orders if o["dish"] == dish_name},
            reverse=True
        )
        for b in batches:
            if any(o["dish"] == dish_name and o["batch"] == b and not o["locked"] for o in self.orders):
                for o in self.orders:
                    if o["dish"] == dish_name and o["batch"] == b:
                        o["locked"] = True
                return True
        return False

    def get_unlocked_batches(self):
        """Return dict of dish -> latest unlocked batch info (in insertion order)."""
        unlocked = {}
        seen = set()

        for o in self.orders:
            dish = o["dish"]
            if dish in seen:
                continue
            seen.add(dish)
            # Get latest unlocked batch for this dish
            batches = sorted({x["batch"] for x in self.orders if x["dish"] == dish and not x["locked"]})
            if batches:
                batch = batches[-1]
                unlocked[dish] = {
                    "locked": False,
                    "orders": [x for x in self.orders if x["dish"] == dish and x["batch"] == batch]
                }
        return unlocked

    def get_locked_batches(self):
        """Return dict of dish -> list of (batch_index, batch_info), preserving order."""
        locked = {}
        seen = set()

        for o in self.orders:
            dish = o["dish"]
            if dish not in seen:
                seen.add(dish)
                dish_batches = sorted({x["batch"] for x in self.orders if x["dish"] == dish and x["locked"]})
                for b in dish_batches:
                    if dish not in locked:
                        locked[dish] = []
                    locked[dish].append((
                        b, {
                            "locked": True,
                            "orders": [x for x in self.orders if x["dish"] == dish and x["batch"] == b]
                        }
                    ))
        return locked

    def confirm_batch_done(self, dish_name, batch_index):
        """Remove a completed (locked) batch."""
        before = len(self.orders)
        self.orders = [o for o in self.orders if not (o["dish"] == dish_name and o["batch"] == batch_index)]
        return len(self.orders) < before

    def print_all_orders(self):
        """Debug printout of all orders."""
        dishes = sorted({o["dish"] for o in self.orders})
        for dish in dishes:
            print(f"\n{dish}:")
            batches = sorted({o["batch"] for o in self.orders if o["dish"] == dish})
            for b in batches:
                locked = any(o["locked"] for o in self.orders if o["dish"] == dish and o["batch"] == b)
                status = "🔒" if locked else "🔓"
                print(f"  Batch {b} {status}")
                for o in [o for o in self.orders if o["dish"] == dish and o["batch"] == b]:
                    remarks = f" ({o['remarks']})" if o["remarks"] else ""
                    print(f"    - Table {o['table']}{remarks}")



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
    #kitchen_manager.add_order("Tom Yum Kung", 1, "xxxxxx")
    kitchen_window.refresh_interface()
    kitchen_root.after(5000, refresh_kitchen_window)
    
#=================
            
# Main program
if __name__ == "__main__":
    kitchen_manager = KitchenManager()  # shared object
    '''
    # Simulating customer orders
    kitchen_manager.add_order("Margherita Pizza", 1, "no olives")
    kitchen_manager.add_order("Margherita Pizza", 2)
    kitchen_manager.add_order("Spaghetti Bolognese", 3, "extra cheese")
    kitchen_manager.add_order("Spaghetti Bolognese", 4, "")
    kitchen_manager.add_order("Caesar Salad", 5, "no dressing")
    '''
    
    order_root = tk.Tk()
    kitchen_root = tk.Tk()

    # BOTH use the same manager
    order_window = CustomerOrderUI(order_root, kitchen_manager)
    kitchen_window = ChefInterface(kitchen_root, kitchen_manager)

    refresh_kitchen_window()
    order_root.mainloop()
    kitchen_root.mainloop()

