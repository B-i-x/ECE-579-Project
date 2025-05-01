"""
Run the campus for N simulated minutes and print every order placed.
"""

import time
from BearDownBots.static import create_campus_environment
from BearDownBots.clock import SimulationClock
from BearDownBots.config import Config

SIM_MINUTES_TO_RUN = 5  # how long you want to observe
TIME_SCALE = 1  # 1 real-sec = 120 sim-sec  (2 sim-min)
# real-interval  =  interval_sim_sec  /  time_scale     (seconds)
# quick test sizes
Config.Environment.MAP_ROWS = 100
Config.Environment.MAP_COLS = 100
Config.Environment.MAX_BUILDING_ATTEMPTS = 40

# make buildings small enough to fit on the tiny map
Config.Environment.MIN_BUILDING_CELLS = 25
Config.Environment.MAX_BUILDING_CELLS = 81


def main() -> None:
    # ------------------------------------------------------------------
    # Build the campus (progress window = None to stay CLI only)
    # ------------------------------------------------------------------
    env = create_campus_environment(progress_window=None)

    # accelerate the clock so you don’t wait 10 real minutes
    clock = SimulationClock()
    clock.time_scale = TIME_SCALE

    sim_end_time = SIM_MINUTES_TO_RUN * 60.0  # seconds

    while clock.sim_time < sim_end_time:
        dt = clock.tick()
        env.update(dt)  # drives RandomOrderScheduler
        time.sleep(0.01)  # keep CPU usage civil
    print("Hi")
    # ------------------------------------------------------------------
    # dump the queue length & a few orders just to be safe
    # ------------------------------------------------------------------
    print("\n=========================")
    print(f"Simulation time elapsed : {clock.sim_time / 60:.1f} sim-min")
    print(f"Orders waiting in queue : {len(env.restaurant)}")
    print("=========================")

    while env.restaurant.has_orders():
        bld, order = env.restaurant.send_next_order()
        print(f" -> {getattr(bld, 'name', 'UNKNOWN')}: {order}")


main()
