import random
from collections import deque
from BearDownBots.config import Config

from BearDownBots.dynamic.randOrders import (
    Order, OrderStatus
)

class OrderPlacer:
    """
    Owns the life-cycle of every ticket:

        PLACED  →  PREPARING  →  READY  →  OUT_FOR_DELIVERY
                 ( ≤ kitchen_capacity concurrent )

    Public API
    ----------
    • place_new_order(buildings)                # from App every few seconds
    • step(sim_time)                            # advance kitchen timers
    • load_ready_orders_into_robots(robots)     # give READY tickets to bots
    """

    def __init__(self, timer, kitchen_capacity: int = 10):
        self.timer             = timer
        self.kitchen_capacity  = kitchen_capacity

        # one flat list keeps all tickets with their drop-off building
        self.orders: list[tuple] = []           # (building, order)

        # helpers for cheap bucket counts
        self._preparing_count = 0
        self._next_order_sim = 0

    # --------------------------------------------------------
    # ticket creation
    # --------------------------------------------------------
    def place_new_order(self, buildings):
        """Create one random ticket and return it to caller (for logging)."""
        now = self.timer.sim_time
        if now < self._next_order_sim:
            return None  # too early – try again next tick

        # schedule the next ticket
        self._next_order_sim = now + Config.Simulation.NEW_ORDER_INTERVAL

        building = random.choice(buildings)
        order    = Order(building, created_at=self.timer.sim_time)
        self.orders.append((building, order))
        return (building, order)

    # --------------------------------------------------------
    # main per-tick update
    # --------------------------------------------------------
    def step(self):
        """Run once per simulation step to update kitchen state."""
        now = self.timer.sim_time

        # 1) move finished PREPARING → READY
        for _b, o in self.orders:
            if o.status == OrderStatus.PREPARING and o.is_ready(now):
                o.status = OrderStatus.READY
                self._preparing_count -= 1

        # 2) pull tickets from waiting line until capacity is full
        free_slots = self.kitchen_capacity - self._preparing_count
        if free_slots > 0:
            for _b, o in self.orders:
                if free_slots == 0:
                    break
                if o.status == OrderStatus.PLACED:
                    o.status = OrderStatus.PREPARING
                    self._preparing_count += 1
                    free_slots -= 1

    # --------------------------------------------------------
    # warehouse → robot
    # --------------------------------------------------------
    def load_ready_orders_into_robots(self, robots):
        """
        Give READY tickets to robots parked on the pickup tile,
        one ticket at a time, least-loaded robot first.
        """
        still_waiting = []
        for building, order in self.orders:
            if order.status != OrderStatus.READY:
                still_waiting.append((building, order))
                continue

            # find idle robots at pickup
            parked = [
                r for r in robots
                if (r.position == r.restaurant_pickup_point
                    and len(r.orders) < r.capacity)
            ]
            if not parked:
                still_waiting.append((building, order))
                continue

            chosen = min(parked, key=lambda r: len(r.orders))
            if chosen.add_order(order):
                order.status = OrderStatus.OUT_FOR_DELIVERY
            else:
                still_waiting.append((building, order))

        # rewrite master list (keeps OUT_FOR_DELIVERY tickets too,
        # because GUI still needs to show them under the robot tab)
        self.orders = still_waiting + [
            pair for pair in self.orders if pair[1].status == OrderStatus.OUT_FOR_DELIVERY
        ]
