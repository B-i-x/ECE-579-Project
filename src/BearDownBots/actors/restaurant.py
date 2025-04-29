from collections import deque

class Restaurant:
    def __init__(self):
        # Each entry is a tuple: (building, order)
        self.order_queue = deque()

    @staticmethod
    def _building_name(b) -> str:
        """
        Works whether `b` is a dict or a Building instance.
        """
        if isinstance(b, dict):
            return b.get("name", "UNKNOWN")
        return getattr(b, "name", "UNKNOWN")

    def receive_order(self, building, order):
        self.order_queue.append((building, order))
        print(f"[Restaurant] Received order for {self._building_name(building)}: {order}")

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

    def place_order(self, building, order):
        """
        Adapter so RandomOrderScheduler can call .place_order().
        """
        self.receive_order(building, order)

    def __len__(self):
        return len(self.order_queue)