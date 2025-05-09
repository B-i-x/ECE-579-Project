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

        if not self.buildings:
            raise RuntimeError("No buildings available to place an order.")

        # pick & place
        building = random.choice(self.buildings)
        order = building.place_order()

        # store and return
        self.orders.append((building, order))
        return order
    
    def load_order_into_robots(self, robots: list[Robot]):
        """
        Load the orders into the robots. For now this just loads an order into the robot with the least amount of orders.
        """

        for building, order in self.orders:    
            # Find the robot with the least number of orders
            robot = min(robots, key=lambda r: len(r.orders))
            robot.add_order(order)
            # print(f"[OrderPlacer] Loaded {order} into {robot}")
        
        self.orders.clear()  # Clear orders after loading into robots
        