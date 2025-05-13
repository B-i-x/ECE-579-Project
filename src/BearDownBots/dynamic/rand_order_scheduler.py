# BearDownBots/actors/random_order_scheduler.py
import random
from BearDownBots.dynamic.randOrders import Order, OrderStatus
from typing import Sequence

from BearDownBots.static.buildings import Building
from BearDownBots.config import Config
from BearDownBots.dynamic.robot import Robot
from BearDownBots.clock import SimulationClock

class OrderPlacer:
    """
    Generates one random Order every `interval_sim_sec` of **simulation time**.
    Call   scheduler.update(dt)   once per frame with dt = simulation-seconds elapsed.
    """
    def __init__(self,
                 buildings,
                 timer : SimulationClock,          
                 ):
        self.buildings : list[Building] = buildings
        self.timer : SimulationClock = timer
        self.orders : list[tuple[Building, Order]] = []  # List to store placed orders
        self.MAX_PREP = 10
        self.PREP_SECONDS = 15
        self._time_acc    = 0.0     # accumulated sim time since last order
        self._last_sim_time = timer.sim_time
        self._last_kitch_t = timer.sim_time

    def place_new_order(self) -> Order | None:
        """
        Must be called every frame. Internally calls timer.tick() to advance
        sim-time. Once accumulated sim-time ≥ NEW_ORDER_INTERVAL, places one
        order and resets the accumulator (minus the interval).
        """
        # advance sim clock and accumulate
        # 1) compute how much sim-time has passed since our last invocation
        current_sim = self.timer.sim_time
        dt = current_sim - self._last_sim_time
        self._last_sim_time = current_sim

        # 2) accumulate
        self._time_acc += dt

        interval = Config.Simulation.NEW_ORDER_INTERVAL
        if self._time_acc < interval:
            return None

        # time to place one order—subtract the interval
        self._time_acc -= interval

        candidates = [b for b in self.buildings if b.name != "Food Warehouse"]

        if not candidates:
            raise RuntimeError("No valid buildings to choose from!")

        building = random.choice(candidates)

        order = building.place_order()
        order.status = OrderStatus.PLACED
        order.prep_remaining = self.PREP_SECONDS

        # store and return
        self.orders.append((building, order))
        return [(building, order)]
    
    def load_order_into_robots(self, robots: list[Robot]):
        """
        Load orders into robots using a configurable strategy:
        - "oldest": oldest available orders
        - "proximity": oldest + 2 closest to that destination (among top 10)
        - "between": 2 oldest + 1 between them
        """
        unassigned: list[tuple[Building, Order]] = []

        # Advance kitchen status
        self._advance_kitchen()

        # Separate orders by status
        ready_orders = [(b, o) for (b, o) in self.orders if o.status == OrderStatus.READY]
        unassigned = [(b, o) for (b, o) in self.orders if o.status != OrderStatus.READY]

        # Find eligible robots
        waiting = [
            r for r in robots
            if r.position == r.restaurant_pickup_point and len(r.orders) < r.MAX_CARRY
        ]

        if not waiting or not ready_orders:
            self.orders = unassigned + ready_orders
            return

        strategy = Config.Simulation.ORDER_ASSIGNMENT_STRATEGY.lower()

        for robot in waiting:
            if not ready_orders:
                break

            selected_orders = []

            if strategy == "oldest":
                selected_orders = ready_orders[-robot.MAX_CARRY:]

            elif strategy == "proximity":
                primary = ready_orders[-1]
                rest = ready_orders[-10:-1]  # 9 before it

                def dist(t):
                    x1, y1 = primary[0].dropoff_point
                    x2, y2 = t[0].dropoff_point
                    return abs(x1 - x2) + abs(y1 - y2)

                close = sorted(rest, key=dist)[:robot.MAX_CARRY - 1]
                selected_orders = [primary] + close

            elif strategy == "between":
                if len(ready_orders) < 2:
                    selected_orders = ready_orders[:robot.MAX_CARRY]
                else:
                    first = ready_orders[-1]
                    second = ready_orders[-2]
                    rest = ready_orders[-10:-2]

                    def between(t):
                        x = t[0].dropoff_point[0]
                        y = t[0].dropoff_point[1]
                        x_range = sorted([first[0].dropoff_point[0], second[0].dropoff_point[0]])
                        y_range = sorted([first[0].dropoff_point[1], second[0].dropoff_point[1]])
                        return x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]

                    mid = next((t for t in rest if between(t)), None)
                    selected_orders = [second, first]
                    if mid:
                        selected_orders.append(mid)

            # Assign selected orders to this robot
            for building, order in selected_orders:
                if robot.add_order(order):
                    order.status = OrderStatus.OUT_FOR_DELIVERY
                    print(f"[Scheduler] Loaded {order} into {robot}")
                    ready_orders.remove((building, order))

        self.orders = unassigned + ready_orders

    def _advance_kitchen(self):
        """
        • keep at most MAX_PREP tickets in PREPARING
        • decrement their timers
        • when prep_remaining ≤ 0 → status = READY
        """
        preparing   = [t for t in self.orders if t[1].status == OrderStatus.PREPARING]
        placed      = [t for t in self.orders if t[1].status == OrderStatus.PLACED]

        # pull from PLACED → PREPARING until capacity full
        while len(preparing) < self.MAX_PREP and placed:
            building, order = placed.pop(0)
            order.status = OrderStatus.PREPARING
            preparing.append((building, order))

        # cook!
        now = self.timer.sim_time
        dt = now - self._last_kitch_t
        self._last_kitch_t = now
        for _, order in preparing:
            order.prep_remaining -= dt
            if order.prep_remaining <= 0:
                order.status = OrderStatus.READY