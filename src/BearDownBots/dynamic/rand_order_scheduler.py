# BearDownBots/actors/random_order_scheduler.py
import random
from BearDownBots.dynamic.randOrders import Order            # or OrderGenerator
from typing import Sequence

from BearDownBots.static.buildings import Building
from BearDownBots.config import Config
from BearDownBots.dynamic.robot import Robot

class OrderPlacer:
    """
    Generates one random Order every `interval_sim_sec` of **simulation time**.
    Call   scheduler.update(dt)   once per frame with dt = simulation-seconds elapsed.
    """
    def __init__(self,
                 buildings,          
                 ):
        self.buildings : list[Building] = buildings

        self.orders : list[Order] = []  # List to store placed orders

    def place_new_order(self) -> Order | None:
        """
        With probability Config.Simulation.ORDER_FREQUENCY, pick a random building
        and place a new order there. Otherwise, do nothing.

        Returns the new Order if one was placed, or None if skipped.
        """
        if not self.buildings:
            raise RuntimeError("No buildings available to place an order.")

        # Roll the dice
        if random.random() > Config.Simulation.ORDER_FREQUENCY:
            # skip placing this time
            return None

        # Otherwise pick & place
        building = random.choice(self.buildings)
        order = building.place_order()
        print(f"[OrderPlacer] Placed {order} at {building.name}")

        self.orders.append((building, order))
        return self.orders
    
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
        