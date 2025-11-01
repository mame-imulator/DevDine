# Application Flow: Restaurant Order Management System

```mermaid
graph TD


```


This document outlines the operational flow of the restaurant order management system, detailing how customer orders are placed, processed in the kitchen, and eventually served or packed. The system is built around a central `KitchenManager` and several user interface components.

## 1. System Initialization

1.  **`KitchenManager`&#32;Instantiation**: A single `KitchenManager` instance is created. This object holds the state for all orders, batches, and the delivery queue.
2.  **Delivery Queue Seeding**: Initial delivery orders are added to the `KitchenManager`'s internal `bill_queue` for demonstration.
3.  **UI Window Creation**: Separate Tkinter root windows are created for each interface: `CustomerOrderUI`, `ChefInterface`, `DineInInterface`, and `DeliveryInterface`.
4.  **Interface Instantiation**: Instances of `CustomerOrderUI`, `ChefInterface`, `DineInInterface`, and `DeliveryInterface` are created, each linked to its dedicated Tkinter root window and all sharing the *same* `KitchenManager` instance.
5.  **Main Loop Start**: The `update_kitchen_ui` function is called once to start the periodic updates, and `mainloop()` is invoked for all Tkinter windows to begin their event loops.

## 2. Customer Order Placement (CustomerOrderUI)

1.  **Input Collection**: The `CustomerOrderUI` captures the table number, selected dish from a dropdown, and any special remarks.
2.  **Validation**: It validates that the table number is numeric.
3.  **Order Submission**: Upon clicking "Place Order", the `submit_order` method calls `kitchen_manager.add_order(dish, "Table:" + table_number, remarks)`.
4.  **UI Feedback**: A confirmation message is displayed, and the input fields are cleared.

## 3. Order Management in KitchenManager

### Adding Orders

-   **`add_order(dish, bill_number, remarks)`**: (Used by `CustomerOrderUI` for dine-in orders)
    -   Finds an existing *unlocked* batch for the `dish` or creates a new one if none exist or all are locked.
    -   Adds the order `[dish, bill_number, remarks, locked=False, ready=False, batch_id]` to the `self.orders` list.
-   **`add_bill_to_queue(bill_number, items)`**: (Used for delivery orders at initialization)
    -   Adds a complete bill (containing multiple `[dish, remarks]` items) to the `self.bill_queue` (a `deque`).

### Feeding Delivery Items (via `update_kitchen_ui`)

-   **`feed_next_item_to_kitchen()`**: (Called periodically by `update_kitchen_ui`)
    -   If `self.bill_queue` is not empty, it takes the first item from the first bill.
    -   Finds an existing *unlocked* batch for the `dish` or creates a new one.
    -   Adds the order `[dish, bill_number, remarks, locked=False, ready=False, batch_id]` to `self.orders`.
    -   If all items from a bill are processed, the bill is removed from `self.bill_queue`.

## 4. Chef Interface Operations (ChefInterface)

1.  **Display Refresh (`refresh_interface`)**: (Called periodically by `update_timers` and `update_kitchen_ui`)

    -   Clears existing displays.
    -   Calls `kitchen_manager.get_unlocked_batches()` to retrieve pending orders (grouped by dish and batch) and displays them under "Pending Orders" with "Confirm" buttons.
    -   Calls `kitchen_manager.get_locked_batches()` to retrieve orders currently being prepared and displays them under "Preparing Menu" with "Done" buttons.

2.  **Confirming a Batch (`lock_menu`)**: 

    -   Triggered by the "Confirm" button for a pending order.
    -   Calls `kitchen_manager.lock_batch(dish_name)`, which sets the `locked` status to `True` for all orders in the specified batch within `self.orders`.
    -   Refreshes the interface to move the batch from "Pending Orders" to "Preparing Menu".

3.  **Marking a Batch Done (`mark_done`)**: 

    -   Triggered by the "Done" button for a preparing order.
    -   Calls `kitchen_manager.confirm_batch_done(dish_name, batch_id)`, which sets the `ready` status to `True` for all orders in the specified batch within `self.orders`.
    -   Refreshes the interface to remove the batch from "Preparing Menu".
    -   Checks `kitchen_manager.get_ready_bills()` and shows a message box if any complete bills are ready.

## 5. Waiter Interface Operations

### Dine-In Interface (DineInInterface)

1.  **Display Refresh (`refresh_interface`)**: (Called periodically by `update_kitchen_ui`)

    -   Clears existing displays.
    -   Filters `kitchen_manager.orders` to find individual dishes that are `ready` and belong to "Table:" bills.
    -   Groups these ready dishes by table number and displays them with "Mark Served" buttons.

2.  **Marking Served (`mark_served`)**: 

    -   Triggered by the "Mark Served" button for a dish.
    -   Removes the specific `dish` for the given `table` from `kitchen_manager.orders` where it was `ready`.
    -   Refreshes the interface.

### Delivery Interface (DeliveryInterface)

1.  **Display Refresh (`refresh_interface`)**: (Called periodically by `update_kitchen_ui`)

    -   Clears existing displays.
    -   Calls `kitchen_manager.get_ready_bills()` to get a list of fully ready delivery bills.
    -   Displays these bills, listing their constituent dishes, with "Mark as Packed" buttons.

2.  **Marking Packed (`mark_packed`)**: 

    -   Triggered by the "Mark as Packed" button for a bill.
    -   Removes all orders associated with the `bill_number` from `kitchen_manager.orders`.
    -   Refreshes the interface and triggers a refresh of the `ChefInterface` to ensure consistency.

## 6. Main Application Loop (`update_kitchen_ui`)

1.  **Delivery Item Feed**: Calls `kitchen_manager.feed_next_item_to_kitchen()` to continuously move items from the delivery queue into the active kitchen orders.
2.  **UI Synchronization**: Calls `refresh_interface()` on `ChefInterface`, `DineInInterface`, and `DeliveryInterface` instances to ensure all displays reflect the latest state of `KitchenManager`.
3.  **Scheduling**: Schedules itself to run again after a 3-second delay, maintaining a periodic update cycle for the entire system.

This interconnected architecture allows for real-time order processing, status updates, and management across different operational roles within a restaurant setting.

---
*Generated by [CodeViz.ai](https://codeviz.ai) on 11/2/2025, 12:00:43 AM*
