# Application Flow: Restaurant Order Management System

**Input Collection**

```mermaid
graph TD

    subgraph 90df74f5-group["**Diagram**<br>[External]"]
        subgraph 90df74f5-ChefUI["**4. Chef Interface**<br>ChefInterface<br>[External]"]
            90df74f5-H1["**ChefInterface**<br>Chef's view of orders<br>[External]"]
            90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-H3["**Pending Orders Display**<br>From get\_unlocked\_batches()<br>[External]"]
            90df74f5-H4["**Preparing Menu Display**<br>From get\_locked\_batches()<br>[External]"]
            90df74f5-H5["**lock\_menu()**<br>User clicks 'Confirm'<br>[External]"]
            90df74f5-H6["**mark\_done()**<br>User clicks 'Done'<br>[External]"]
            90df74f5-H7["**Delivery Ready Message**<br>messagebox.showinfo()<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-H1["**ChefInterface**<br>Chef's view of orders<br>[External]"] -->|"Triggers"| 90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-H3["**Pending Orders Display**<br>From get\_unlocked\_batches()<br>[External]"] -->|"User action"| 90df74f5-H5["**lock\_menu()**<br>User clicks 'Confirm'<br>[External]"]
            90df74f5-H4["**Preparing Menu Display**<br>From get\_locked\_batches()<br>[External]"] -->|"User action"| 90df74f5-H6["**mark\_done()**<br>User clicks 'Done'<br>[External]"]
        end
        subgraph 90df74f5-CustomerOrder["**2. Customer Order Placement**<br>CustomerOrderUI<br>[External]"]
            90df74f5-C1["**CustomerOrderUI**<br>Customer-facing interface<br>[External]"]
            90df74f5-C2["**Input Collection**<br>Table #, Dish, Remarks<br>[External]"]
            90df74f5-C3["**Input Validation**<br>table\_number.isdigit()<br>[External]"]
            90df74f5-C4["**submit\_order()**<br>Place Order button click<br>[External]"]
            90df74f5-C5["**kitchen\_manager.add\_order()**<br>Adds dine-in order to KitchenManager<br>[External]"]
            90df74f5-C6["**UI Feedback**<br>messagebox.showinfo(), clear form<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-C1["**CustomerOrderUI**<br>Customer-facing interface<br>[External]"] -->|"Builds"| 90df74f5-C2["**Input Collection**<br>Table #, Dish, Remarks<br>[External]"]
            90df74f5-C2["**Input Collection**<br>Table #, Dish, Remarks<br>[External]"] -->|"Triggers"| 90df74f5-C4["**submit\_order()**<br>Place Order button click<br>[External]"]
            90df74f5-C4["**submit\_order()**<br>Place Order button click<br>[External]"] -->|"Performs"| 90df74f5-C3["**Input Validation**<br>table\_number.isdigit()<br>[External]"]
            90df74f5-C4["**submit\_order()**<br>Place Order button click<br>[External]"] -->|"Invalid"| 90df74f5-C6["**UI Feedback**<br>messagebox.showinfo(), clear form<br>[External]"]
            90df74f5-C3["**Input Validation**<br>table\_number.isdigit()<br>[External]"] -->|"Valid"| 90df74f5-C5["**kitchen\_manager.add\_order()**<br>Adds dine-in order to KitchenManager<br>[External]"]
            90df74f5-C5["**kitchen\_manager.add\_order()**<br>Adds dine-in order to KitchenManager<br>[External]"] -->|"Provides"| 90df74f5-C6["**UI Feedback**<br>messagebox.showinfo(), clear form<br>[External]"]
        end
        subgraph 90df74f5-Init["**1. System Initialization**<br>Application Startup<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"]
            90df74f5-A2["**KitchenManager Instance**<br>Manages all orders/batches<br>[External]"]
            90df74f5-A3["**Delivery Queue Seeding**<br>kitchen\_manager.add\_bill\_to\_queue()<br>[External]"]
            90df74f5-A4["**Tkinter Root Windows**<br>tk.Tk() for each UI<br>[External]"]
            90df74f5-A5["**UI Instances Created**<br>CustomerOrderUI, ChefInterface, etc.<br>[External]"]
            90df74f5-A6["**Initial update\_kitchen\_ui() Call**<br>Starts periodic updates<br>[External]"]
            90df74f5-A7["**Tkinter mainloop()**<br>Starts UI event loops<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Creates"| 90df74f5-A2["**KitchenManager Instance**<br>Manages all orders/batches<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Adds initial orders to"| 90df74f5-A3["**Delivery Queue Seeding**<br>kitchen\_manager.add\_bill\_to\_queue()<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Creates"| 90df74f5-A4["**Tkinter Root Windows**<br>tk.Tk() for each UI<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Instantiates UIs with"| 90df74f5-A5["**UI Instances Created**<br>CustomerOrderUI, ChefInterface, etc.<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Invokes"| 90df74f5-A6["**Initial update\_kitchen\_ui() Call**<br>Starts periodic updates<br>[External]"]
            90df74f5-A1["**Main Program**<br>if **name** == '**main**'<br>[External]"] -->|"Starts"| 90df74f5-A7["**Tkinter mainloop()**<br>Starts UI event loops<br>[External]"]
            90df74f5-A5["**UI Instances Created**<br>CustomerOrderUI, ChefInterface, etc.<br>[External]"] -->|"References"| 90df74f5-A2["**KitchenManager Instance**<br>Manages all orders/batches<br>[External]"]
        end
        subgraph 90df74f5-KitchenCore["**3. Kitchen Management Core**<br>KitchenManager Logic<br>[External]"]
            90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
            90df74f5-K10["**get\_unlocked\_batches()**<br>Query for ChefInterface<br>[External]"]
            90df74f5-K11["**get\_locked\_batches()**<br>Query for ChefInterface<br>[External]"]
            90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"]
            90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K4["**self.bill\_queue deque**<br>Delivery bills [bill#, [[dish, remarks],...]]<br>[External]"]
            90df74f5-K5["**add\_order()**<br>For dine-in/direct add<br>[External]"]
            90df74f5-K6["**add\_bill\_to\_queue()**<br>For initial delivery setup<br>[External]"]
            90df74f5-K7["**feed\_next\_item\_to\_kitchen()**<br>Periodically moves delivery items to orders<br>[External]"]
            90df74f5-K8["**lock\_batch()**<br>Marks orders in a batch as locked<br>[External]"]
            90df74f5-K9["**confirm\_batch\_done()**<br>Marks orders in a batch as ready<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"] -->|"Manages"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"] -->|"Manages"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"] -->|"Manages"| 90df74f5-K4["**self.bill\_queue deque**<br>Delivery bills [bill#, [[dish, remarks],...]]<br>[External]"]
            90df74f5-K5["**add\_order()**<br>For dine-in/direct add<br>[External]"] -->|"Modifies"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K5["**add\_order()**<br>For dine-in/direct add<br>[External]"] -->|"Modifies"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K6["**add\_bill\_to\_queue()**<br>For initial delivery setup<br>[External]"] -->|"Modifies"| 90df74f5-K4["**self.bill\_queue deque**<br>Delivery bills [bill#, [[dish, remarks],...]]<br>[External]"]
            90df74f5-K7["**feed\_next\_item\_to\_kitchen()**<br>Periodically moves delivery items to orders<br>[External]"] -->|"Reads from"| 90df74f5-K4["**self.bill\_queue deque**<br>Delivery bills [bill#, [[dish, remarks],...]]<br>[External]"]
            90df74f5-K7["**feed\_next\_item\_to\_kitchen()**<br>Periodically moves delivery items to orders<br>[External]"] -->|"Modifies"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K7["**feed\_next\_item\_to\_kitchen()**<br>Periodically moves delivery items to orders<br>[External]"] -->|"Modifies"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K8["**lock\_batch()**<br>Marks orders in a batch as locked<br>[External]"] -->|"Modifies"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K8["**lock\_batch()**<br>Marks orders in a batch as locked<br>[External]"] -->|"Modifies"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K9["**confirm\_batch\_done()**<br>Marks orders in a batch as ready<br>[External]"] -->|"Modifies"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K10["**get\_unlocked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Reads from"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K10["**get\_unlocked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Reads from"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K11["**get\_locked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Reads from"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
            90df74f5-K11["**get\_locked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Reads from"| 90df74f5-K3["**self.batches list**<br>[dish, batch\_id, locked, timestamp]<br>[External]"]
            90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"] -->|"Reads from"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
        end
        subgraph 90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"]
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"]
            90df74f5-M2["**kitchen\_manager.feed\_next\_item\_to\_kitchen()**<br>Moves delivery items<br>[External]"]
            90df74f5-M3["**kitchen\_window.refresh\_interface()**<br>Updates Chef UI<br>[External]"]
            90df74f5-M4["**dinein\_window.refresh\_interface()**<br>Updates Dine-In UI<br>[External]"]
            90df74f5-M5["**delivery\_window.refresh\_interface()**<br>Updates Delivery UI<br>[External]"]
            90df74f5-M6["**root.after(3000, update\_kitchen\_ui)**<br>Schedules next run<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"] -->|"Calls"| 90df74f5-M2["**kitchen\_manager.feed\_next\_item\_to\_kitchen()**<br>Moves delivery items<br>[External]"]
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"] -->|"Calls"| 90df74f5-M3["**kitchen\_window.refresh\_interface()**<br>Updates Chef UI<br>[External]"]
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"] -->|"Calls"| 90df74f5-M4["**dinein\_window.refresh\_interface()**<br>Updates Dine-In UI<br>[External]"]
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"] -->|"Calls"| 90df74f5-M5["**delivery\_window.refresh\_interface()**<br>Updates Delivery UI<br>[External]"]
            90df74f5-M1["**update\_kitchen\_ui()**<br>Periodic scheduler<br>[External]"] -->|"Schedules"| 90df74f5-M6["**root.after(3000, update\_kitchen\_ui)**<br>Schedules next run<br>[External]"]
        end
        subgraph 90df74f5-WaiterUIs["**5. Waiter Interfaces**<br>DineInInterface and DeliveryInterface<br>[External]"]
            90df74f5-D1["**DineInInterface**<br>Waiter's view for dine-in<br>[External]"]
            90df74f5-D2["**DineIn refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-D3["**Ready Dine-In Dishes Display**<br>From filtered kitchen.orders<br>[External]"]
            90df74f5-D4["**mark\_served()**<br>User clicks 'Mark Served'<br>[External]"]
            90df74f5-E1["**DeliveryInterface**<br>Waiter's view for delivery<br>[External]"]
            90df74f5-E2["**Delivery refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-E3["**Ready Delivery Orders Display**<br>From get\_ready\_bills()<br>[External]"]
            90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"]
            %% Edges at this level (grouped by source)
            90df74f5-D1["**DineInInterface**<br>Waiter's view for dine-in<br>[External]"] -->|"Triggers"| 90df74f5-D2["**DineIn refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-D3["**Ready Dine-In Dishes Display**<br>From filtered kitchen.orders<br>[External]"] -->|"User action"| 90df74f5-D4["**mark\_served()**<br>User clicks 'Mark Served'<br>[External]"]
            90df74f5-D4["**mark\_served()**<br>User clicks 'Mark Served'<br>[External]"] -->|"Triggers"| 90df74f5-D2["**DineIn refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-E1["**DeliveryInterface**<br>Waiter's view for delivery<br>[External]"] -->|"Triggers"| 90df74f5-E2["**Delivery refresh\_interface()**<br>Updates display<br>[External]"]
            90df74f5-E3["**Ready Delivery Orders Display**<br>From get\_ready\_bills()<br>[External]"] -->|"User action"| 90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"]
            90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"] -->|"Triggers"| 90df74f5-E2["**Delivery refresh\_interface()**<br>Updates display<br>[External]"]
        end
        %% Edges at this level (grouped by source)
        90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"] -->|"Calls"| 90df74f5-K10["**get\_unlocked\_batches()**<br>Query for ChefInterface<br>[External]"]
        90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"] -->|"Calls"| 90df74f5-K11["**get\_locked\_batches()**<br>Query for ChefInterface<br>[External]"]
        90df74f5-K10["**get\_unlocked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Populates"| 90df74f5-H3["**Pending Orders Display**<br>From get\_unlocked\_batches()<br>[External]"]
        90df74f5-K11["**get\_locked\_batches()**<br>Query for ChefInterface<br>[External]"] -->|"Populates"| 90df74f5-H4["**Preparing Menu Display**<br>From get\_locked\_batches()<br>[External]"]
        90df74f5-H5["**lock\_menu()**<br>User clicks 'Confirm'<br>[External]"] -->|"Calls"| 90df74f5-K8["**lock\_batch()**<br>Marks orders in a batch as locked<br>[External]"]
        90df74f5-H5["**lock\_menu()**<br>User clicks 'Confirm'<br>[External]"] -->|"Acts on"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-K8["**lock\_batch()**<br>Marks orders in a batch as locked<br>[External]"] -->|"Updates status, triggers"| 90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"]
        90df74f5-H6["**mark\_done()**<br>User clicks 'Done'<br>[External]"] -->|"Calls"| 90df74f5-K9["**confirm\_batch\_done()**<br>Marks orders in a batch as ready<br>[External]"]
        90df74f5-H6["**mark\_done()**<br>User clicks 'Done'<br>[External]"] -->|"Checks"| 90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"]
        90df74f5-H6["**mark\_done()**<br>User clicks 'Done'<br>[External]"] -->|"Acts on"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-K9["**confirm\_batch\_done()**<br>Marks orders in a batch as ready<br>[External]"] -->|"Updates status, triggers"| 90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"]
        90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"] -->|"If ready, triggers"| 90df74f5-H7["**Delivery Ready Message**<br>messagebox.showinfo()<br>[External]"]
        90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"] -->|"Populates"| 90df74f5-E3["**Ready Delivery Orders Display**<br>From get\_ready\_bills()<br>[External]"]
        90df74f5-D2["**DineIn refresh\_interface()**<br>Updates display<br>[External]"] -->|"Filters"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
        90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"] -->|"Populates"| 90df74f5-D3["**Ready Dine-In Dishes Display**<br>From filtered kitchen.orders<br>[External]"]
        90df74f5-D4["**mark\_served()**<br>User clicks 'Mark Served'<br>[External]"] -->|"Removes specific order from"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
        90df74f5-D4["**mark\_served()**<br>User clicks 'Mark Served'<br>[External]"] -->|"Acts on"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-E2["**Delivery refresh\_interface()**<br>Updates display<br>[External]"] -->|"Calls"| 90df74f5-K12["**get\_ready\_bills()**<br>Query for Waiter Interfaces<br>[External]"]
        90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"] -->|"Removes all orders for bill from"| 90df74f5-K2["**self.orders list**<br>[dish, bill#, remarks, locked, ready, batch\_id]<br>[External]"]
        90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"] -->|"Also triggers"| 90df74f5-H2["**refresh\_interface()**<br>Updates display<br>[External]"]
        90df74f5-E4["**mark\_packed()**<br>User clicks 'Mark as Packed'<br>[External]"] -->|"Acts on"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-M2["**kitchen\_manager.feed\_next\_item\_to\_kitchen()**<br>Moves delivery items<br>[External]"] -->|"Interacts with"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-M3["**kitchen\_window.refresh\_interface()**<br>Updates Chef UI<br>[External]"] -->|"Interacts with"| 90df74f5-H1["**ChefInterface**<br>Chef's view of orders<br>[External]"]
        90df74f5-M4["**dinein\_window.refresh\_interface()**<br>Updates Dine-In UI<br>[External]"] -->|"Interacts with"| 90df74f5-D1["**DineInInterface**<br>Waiter's view for dine-in<br>[External]"]
        90df74f5-M5["**delivery\_window.refresh\_interface()**<br>Updates Delivery UI<br>[External]"] -->|"Interacts with"| 90df74f5-E1["**DeliveryInterface**<br>Waiter's view for delivery<br>[External]"]
        90df74f5-C5["**kitchen\_manager.add\_order()**<br>Adds dine-in order to KitchenManager<br>[External]"] -->|"Adds orders to"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-A3["**Delivery Queue Seeding**<br>kitchen\_manager.add\_bill\_to\_queue()<br>[External]"] -->|"Initializes"| 90df74f5-K1["**KitchenManager**<br>Central order state management<br>[External]"]
        90df74f5-Init["**1. System Initialization**<br>Application Startup<br>[External]"] --> 90df74f5-CustomerOrder["**2. Customer Order Placement**<br>CustomerOrderUI<br>[External]"]
        90df74f5-Init["**1. System Initialization**<br>Application Startup<br>[External]"] --> 90df74f5-ChefUI["**4. Chef Interface**<br>ChefInterface<br>[External]"]
        90df74f5-Init["**1. System Initialization**<br>Application Startup<br>[External]"] --> 90df74f5-WaiterUIs["**5. Waiter Interfaces**<br>DineInInterface and DeliveryInterface<br>[External]"]
        90df74f5-Init["**1. System Initialization**<br>Application Startup<br>[External]"] --> 90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"]
        90df74f5-CustomerOrder["**2. Customer Order Placement**<br>CustomerOrderUI<br>[External]"] --> 90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"]
        90df74f5-ChefUI["**4. Chef Interface**<br>ChefInterface<br>[External]"] --> 90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"]
        90df74f5-WaiterUIs["**5. Waiter Interfaces**<br>DineInInterface and DeliveryInterface<br>[External]"] --> 90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"]
        90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"] --> 90df74f5-ChefUI["**4. Chef Interface**<br>ChefInterface<br>[External]"]
        90df74f5-MainLoop["**6. Main Application Loop**<br>update\_kitchen\_ui() Function<br>[External]"] --> 90df74f5-WaiterUIs["**5. Waiter Interfaces**<br>DineInInterface and DeliveryInterface<br>[External]"]
    end

```

Table #, Dish, Remarks
---
**self.orders list**
[dish, bill#, remarks, locked, ready, batch\_id]
---
**self.bill\_queue deque**
Delivery bills [bill#, [[dish, remarks],...]]

---
*Generated by [CodeViz.ai](https://codeviz.ai) on 11/2/2025, 12:02:22 AM*


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
