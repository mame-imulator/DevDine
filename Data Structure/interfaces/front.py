import tkinter as tk
from tkinter import ttk, messagebox


# KitchenOrderManager reused from above
class KitchenOrderManager:
    def __init__(self):
        self.menu_orders = {}

    def add_order(self, dish_name, table_number, remarks=""):
        order = {"table": table_number, "remarks": remarks}
        if dish_name not in self.menu_orders:
            self.menu_orders[dish_name] = []

        if not self.menu_orders[dish_name] or self.menu_orders[dish_name][-1]["locked"]:
            self.menu_orders[dish_name].append({"locked": False, "orders": []})

        self.menu_orders[dish_name][-1]["orders"].append(order)

    def print_all_orders(self):
        for dish, batches in self.menu_orders.items():
            print(f"\n{dish}:")
            for i, batch in enumerate(batches):
                status = "🔒" if batch["locked"] else "🔓"
                print(f"  Batch {i} {status}")
                for order in batch["orders"]:
                    remarks = f" ({order['remarks']})" if order["remarks"] else ""
                    print(f"    - Table {order['table']}{remarks}")


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

# Main program
if __name__ == "__main__":
    kitchen_manager = KitchenOrderManager()

    root = tk.Tk()
    app = CustomerOrderUI(root, kitchen_manager)
    root.mainloop()

    # Debug print after GUI closes
    print("\n--- All Orders Submitted ---")
    kitchen_manager.print_all_orders()
