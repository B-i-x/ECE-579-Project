import time

from BearDownBots.config import Config

class SimulationClock:
    def __init__(self):
        self.time_scale    = Config.TIME_SCALE   # e.g. 0.5 = half speed, 2.0 = double speed
        self._last_real    = time.perf_counter()
        self.sim_time      = 0.0          # accumulated simulation time

    def tick(self) -> float:
        """
        Call each frame. Returns sim_dt (seconds of sim time that passed).
        """
        now      = time.perf_counter()
        real_dt  = now - self._last_real
        self._last_real = now
        sim_dt   = real_dt * self.time_scale
        self.sim_time += sim_dt
        return sim_dt
