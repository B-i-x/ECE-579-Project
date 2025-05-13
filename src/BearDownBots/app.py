import sys
import time
import threading

from BearDownBots.config import Config
from BearDownBots.clock import SimulationClock

from BearDownBots.static import create_campus_environment

from BearDownBots.dynamic.robot import Robot

from BearDownBots.render.gui import GuiWrapper
from BearDownBots.render.loading import ProgressWindow

from BearDownBots.dynamic.rand_order_scheduler import OrderPlacer
class BearDownBotsApp():
    def __init__(self):
        # core state
        self.environment     = None
        self.renderer        = None
        self.progress_window = None
        self.running         = False
        self.sim_thread      = None

        self.base_fps   = Config.Simulation.UPDATES_PER_SEC
        self.time_scale = Config.Simulation.TIME_SCALE

        self.renderer = GuiWrapper()
        self.progress_window = ProgressWindow(self.renderer)
        # 1) common setup
        self.setup()

        # 2) headless vs GUI
        if Config.HEADLESS_FLAG:
            self.run_cli()
        else:
            # -- GUI mode wiring --
            self.renderer.add_objects_to_render(
                campus_map=self.environment,
                robots=self.robots,
                scheduler = self.order_scheduler,
                progress_window=self.progress_window
            )
            self.renderer.user_dash.start_button .configure(command=self.start_simulation)
            self.renderer.user_dash.stop_button  .configure(command=self.pause_simulation)
            self.renderer.user_dash.start_clock(
                time_func=lambda: self.sim_clock.now(),
                interval_ms=int(1000 / self.base_fps)
            )
            self.renderer.setup_dynamic_events()
            self.renderer.mainloop()

    def setup(self):
        """Shared environment and robot initialization."""
        self.sim_clock       = SimulationClock()
        self.environment     = create_campus_environment(self.progress_window if not Config.HEADLESS_FLAG else None)
        self.order_scheduler = OrderPlacer(self.environment.buildings, self.sim_clock)
        self.robots = [
            Robot(i, self.environment)
            for i in range(Config.Simulation.NUM_ROBOTS)
        ]

    def start_simulation(self):
        """Start the GUI scheduler or un-block the CLI start command."""
        if not self.running:
            self.sim_clock._last_real = time.perf_counter()
            self.running = True
            if not Config.HEADLESS_FLAG:
                self._schedule_next_simulation_step()

    def pause_simulation(self):
        """Stop the simulation loop."""
        if self.running:
            self.running = False
            print("Simulation stopped.")

    def _schedule_next_simulation_step(self):
        """GUI‐driven scheduling via tkinter.after."""
        if not self.running:
            return
        self._do_step()
        delay = int((1000 / self.base_fps) / self.time_scale)
        self.renderer.after(delay, self._schedule_next_simulation_step)

    def _do_step(self):
        """One tick of sim: clock, orders, robots, and GUI updates if any."""
        # advance clock
        self.sim_clock.tick()

        # place new orders
        new_orders = self.order_scheduler.place_new_order()

        # if not Config.HEADLESS_FLAG:
        #
        #     if new_orders:
        #         # for b, o in new_orders:
        #         #     oid = getattr(o, "id", str(o))
        #         #     self.renderer.restaurant_dash.add_order_to_listbox(b.name, oid)
        #         self.renderer.restaurant_dash.order_count_label.config(
        #             text=f"Orders Placed: {self.renderer.restaurant_dash.total_order_count}"
        #         )

        # assign & move robots
        self.order_scheduler.load_order_into_robots(self.robots)

        for bot in self.robots:
            bot.act()

        # redraw
        if not Config.HEADLESS_FLAG:
            self.renderer.robot_renderer .render_robots(self.robots)
            self.renderer.restaurant_dash.update()

    def run_cli(self):
        """
        Simple REPL for headless mode.

        Commands:
          start   — begin continuous simulation
          stop    — pause it
          step    — advance exactly one tick
          status  — show time, pending orders, robots
          help    — list commands
          exit    — quit
        """
        command_explanation = """
            start\tstart continuous simulation
            stop \tpause it")
            step \tadvance one simulation step
            status\tprint time, orders, robot positions
            exit \tquit the program
        """

        print("=== BearDownBots CLI (headless mode) ===")
        print(command_explanation)
        print("Type 'help' for commands.")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "help":
                print(command_explanation)

            elif cmd == "start":
                if not self.running:
                    self.running = True
                    self.sim_thread = threading.Thread(
                        target=self._cli_loop, daemon=True
                    )
                    self.sim_thread.start()
                    print("Simulation started.")
                else:
                    print("Already running.")
            elif cmd == "stop":
                if self.running:
                    self.running = False
                    self.sim_thread.join()
                    print("Simulation paused.")
                else:
                    print("Not running.")
            elif cmd == "step":
                self._do_step()
                print(f"Step done. Time = {self.sim_clock.now():.2f}s")
            elif cmd == "status":
                t = self.sim_clock.now()
                pending = len(self.order_scheduler.orders)
                print(f"Time = {t:.2f}s, pending orders = {pending}")
                for bot in self.robots:
                    print(f"  {bot}  orders={len(bot.orders)}")
            elif cmd in ("exit", "quit"):
                if self.running:
                    self.running = False
                    self.sim_thread.join()
                print("Exiting.")
                sys.exit(0)
            else:
                print(f"Unknown command: '{cmd}'. Type 'help'.")

    def _cli_loop(self):
        """Background loop for `start` command in CLI mode."""
        interval = 1.0 / (self.base_fps * self.time_scale)
        while self.running:
            self._do_step()
            time.sleep(interval)

if __name__ == "__main__":
    app = BearDownBotsApp()
    