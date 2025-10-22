import tkinter as tk
from tkinter import ttk


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


# Demo / Test Orders
if __name__ == "__main__":
    kitchen = KitchenManager()

    # Simulating customer orders
    kitchen.add_order("Margherita Pizza", 1, "no olives")
    kitchen.add_order("Margherita Pizza", 2)
    kitchen.add_order("Spaghetti Bolognese", 3, "extra cheese")
    kitchen.add_order("Spaghetti Bolognese", 4, "")
    kitchen.add_order("Caesar Salad", 5, "no dressing")

    root = tk.Tk()
    app2 = ChefInterface(root, kitchen)
    root.mainloop()
