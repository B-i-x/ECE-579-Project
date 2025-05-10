# BearDownBots/actors/random_order_scheduler.py
import random
from BearDownBots.dynamic.randOrders import Order            # or OrderGenerator
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
        self.orders : list[Order] = []  # List to store placed orders
        self._time_acc    = 0.0     # accumulated sim time since last order
        self._last_sim_time = timer.sim_time

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

        # pick & place
        building = random.choice(self.buildings)

        
        order = building.place_order()

        # store and return
        self.orders.append((building, order))
        return order
    
    def load_order_into_robots(self, robots: list[Robot]):
        """
        Load orders into any robot that is both at the restaurant pickup
        point *and* has the fewest orders.  Any order for which no robot
        is at the pickup point remains in self.orders (unassigned).
        """
        unassigned: list[tuple[Building, Order]] = []

        for building, order in self.orders:
            # find all robots currently waiting at the restaurant
            available = [
                r for r in robots
                if r.position == r.restaurant_pickup_point
            ]

            if not available:
                # no one at pickup → leave this order unassigned
                unassigned.append((building, order))
                continue

            # among those at the pickup, pick the one with fewest orders
            chosen = min(available, key=lambda r: len(r.orders))
            chosen.add_order(order)
            print(f"[OrderPlacer] Loaded {order} into {chosen}")

        # keep only the orders that we were unable to load
        self.orders = unassigned

        