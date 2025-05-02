import time

class SimulationClock:
    def __init__(self):
        self._last_real = time.perf_counter()
        self.sim_time   = 0.0  # accumulated simulation time (in real seconds)

    def tick(self) -> float:
        """
        Call each frame. Returns the real_dt (seconds of real time that passed).
        """
        now     = time.perf_counter()
        real_dt = now - self._last_real
        self._last_real = now

        self.sim_time += real_dt
        return real_dt
