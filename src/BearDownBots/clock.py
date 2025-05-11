import time
from BearDownBots.config import Config

class SimulationClock:
    def __init__(self):
        # read the global scale factor
        self.time_scale = Config.Simulation.TIME_SCALE  
        self._last_real = time.perf_counter()
        self.sim_time   = 0.0  # accumulated simulation time (in sim-seconds)

    def tick(self) -> float:
        """
        Call each frame. Returns sim_dt (seconds of simulation time that passed),
        which is real_dt multiplied by Config.Simulation.TIME_SCALE.
        """
        now     = time.perf_counter()
        real_dt = now - self._last_real
        self._last_real = now

        sim_dt = real_dt * self.time_scale
        self.sim_time += sim_dt
        return sim_dt
    
    def now(self) -> float:
        return self.sim_time
