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
        self.PREP_SECONDS = 5 * 60
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
        Load orders into any robot that is both at the restaurant pickup
        point *and* has the fewest orders.  Any order for which no robot
        is at the pickup point remains in self.orders (unassigned).
        """
        unassigned: list[tuple[Building, Order]] = []

        # 1) First move tickets through the kitchen pipeline
        self._advance_kitchen()

        # 2) Then try to load READY tickets into idle robots
        for building, order in self.orders:
            if order.status != OrderStatus.READY:
                unassigned.append((building, order))
                continue

            # find bots parked at the pickup point
            waiting = [
                r for r in robots
                if r.position == r.restaurant_pickup_point
            ]

            if not waiting:
                unassigned.append((building, order))
                continue

            chosen = min(waiting, key=lambda r: len(r.orders))
            chosen.add_order(order)
            order.status = OrderStatus.OUT_FOR_DELIVERY
            print(f"[Scheduler] Loaded {order} into {chosen}")

        # for building, order in self.orders:
        #     # find all robots currently waiting at the restaurant
        #     available = [
        #         r for r in robots
        #         if r.position == r.restaurant_pickup_point
        #     ]
        #
        #     if not available:
        #         # no one at pickup → leave this order unassigned
        #         unassigned.append((building, order))
        #         continue
        #
        #     # among those at the pickup, pick the one with fewest orders
        #     chosen = min(available, key=lambda r: len(r.orders))
        #     chosen.add_order(order)
        #     print(f"[OrderPlacer] Loaded {order} into {chosen}")

        # keep only the orders that we were unable to load
        self.orders = unassigned

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------
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