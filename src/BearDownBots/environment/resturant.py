from collections import deque

class Restaurant:
    def __init__(self):
        # Each entry is a tuple: (building, order)
        self.order_queue = deque()

    def receive_order(self, building, order):
        """Add a new order to the queue."""
        self.order_queue.append((building, order))
        building_name = building.get("name", "UNKNOWN")
        print(f"[Restaurant] Received order for {building_name}: {order}")

    def send_next_order(self):
        """Send (and remove) the next order in the queue."""
        if not self.order_queue:
            print("[Restaurant] No orders to send.")
            return None
        building, order = self.order_queue.popleft()
        building_name = building.get("name", "UNKNOWN")
        print(f"[Restaurant] Sending order to {building_name}: {order}")
        return building, order

    def has_orders(self):
        """Check if there are orders waiting."""
        return bool(self.order_queue)

    def __len__(self):
        return len(self.order_queue)
