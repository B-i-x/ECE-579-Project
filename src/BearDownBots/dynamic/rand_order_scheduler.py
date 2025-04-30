# BearDownBots/actors/random_order_scheduler.py
import random
from BearDownBots.dynamic.randOrders import Order            # or OrderGenerator
from typing import Sequence

class RandomOrderScheduler:
    """
    Generates one random Order every `interval_sim_sec` of **simulation time**.
    Call   scheduler.update(dt)   once per frame with dt = simulation-seconds elapsed.
    """
    def __init__(self,
                 buildings: Sequence,          # list[Building] or list[dict]
                 order_placer,                 # object with .place_order(building, order)
                 interval_sim_sec: float = 600 # 10 sim-minutes
                 ):
        self.buildings = list(buildings)
        self.order_placer = order_placer
        self.interval = interval_sim_sec
        self._accumulator = 0.0           # counts sim-seconds since last order

    # ------------------------------------------------------------------ helpers
    def _pick_building(self):
        return random.choice(self.buildings)

    def _make_order(self):
        return Order()                         # or OrderGenerator(1).generate_orders()[0]

    def _dispatch_order(self, building, order):
        self.order_placer.place_order(building, order)
        bname = getattr(building, "name", None)
        if bname is None and isinstance(building, dict):
            bname = building.get("name", "UNKNOWN")
        print(f"[{self.__class__.__name__}]  ➜  {bname}: {order}")

    # ------------------------------------------------------------------ public
    def update(self, dt: float):
        """Call once per frame with dt = simulation-seconds elapsed."""
        self._accumulator += dt
        if self._accumulator >= self.interval:
            self._accumulator -= self.interval   # retain spill-over time
            self._dispatch_order(self._pick_building(), self._make_order())
