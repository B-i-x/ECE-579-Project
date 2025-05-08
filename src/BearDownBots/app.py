import time

from BearDownBots.config import Config
from BearDownBots.clock import SimulationClock

from BearDownBots.static import create_campus_environment

from BearDownBots.dynamic.robot import Robot

from BearDownBots.render.gui import GuiWrapper
from BearDownBots.render.loading import ProgressWindow

from BearDownBots.dynamic.rand_order_scheduler import OrderPlacer

class BearDownBotsApp():
    def __init__(self):
        self.environment = None  # Placeholder for the environment object
        self.renderer = None  # Placeholder for the renderer object
        self.running = False

        self.renderer = GuiWrapper()

        self.progress_window = ProgressWindow(self.renderer)
        
        self.setup()
        # self.run()

    def setup(self):
        """
        Setup the application environment and renderer.
        """
        self.sim_clock = SimulationClock()

        self.environment = create_campus_environment(self.progress_window)

        self.order_scheduler = OrderPlacer(self.environment.buildings)

        self.robots = [Robot(count, self.environment) for count in range(Config.Simulation.NUM_ROBOTS)]

        self.renderer.add_objects_to_render(
            campus_map=self.environment,
            robots=self.robots,
            progress_window=self.progress_window
        )

        self.renderer.user_dash.start_button.configure(command=self.start_simulation)
        self.renderer.user_dash.stop_button.configure(command=self.pause_simulation)

        self.renderer.setup_dynamic_events()

    def start_simulation(self):
        if not self.running:
            # reset the clock’s “last real” to avoid huge jump
            self.sim_clock._last_real = time.perf_counter()
            self.running = True
            self._schedule_next_simulation_step()

    def pause_simulation(self):
        self.running = False
        print("Simulation stopped.")

    def _schedule_next_simulation_step(self):
        """Advance the sim clock once, update UI, and re-schedule if still running."""
        if not self.running:
            return

        # 1) Advance the simulation clock
        self.sim_clock.tick()

        self.order_scheduler.place_new_order()

        new_orders = self.order_scheduler.place_new_order()

# Add to listbox if any new orders were placed
        if new_orders:
            for building, order in new_orders:
                order_id = getattr(order, "id", str(order))  # fallback if no .id exists
                self.renderer.restaurant_dash.add_order_to_listbox(building.name, order_id)

        #  Update the order count based on counter
        self.renderer.restaurant_dash.order_count_label.config(
            text=f"Orders Placed: {self.renderer.restaurant_dash.total_order_count}")

        self.order_scheduler.load_order_into_robots(self.robots)
        
        for bot in self.robots:
            bot.act()

        self.renderer.robot_renderer.render_robots(self.robots)
        self.renderer.restaurant_dash.update_robot_labels()
        # this is like the window.update() call in a GUI loop
        # 3) Schedule the next step in ~16ms (about 60 updates/sec)
        self.renderer.after(
            16,
            self._schedule_next_simulation_step
        )

if __name__ == "__main__":
    app = BearDownBotsApp()
    app.renderer.deiconify()   # Show the window (it starts hidden)
    app.renderer.mainloop()