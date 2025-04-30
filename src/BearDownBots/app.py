import time

from BearDownBots.config import Config
from BearDownBots.clock import SimulationClock

from BearDownBots.static import create_campus_environment

from BearDownBots.dynamic.robot import Robot

from BearDownBots.render.gui import GuiWrapper
from BearDownBots.render.loading import ProgressWindow

class BearDownBotsApp():
    def __init__(self):
        self.environment = None  # Placeholder for the environment object
        self.renderer = None  # Placeholder for the renderer object

        self.renderer = GuiWrapper()

        self.progress_window = ProgressWindow(self.renderer)
        
        self.setup()
        # self.run()

    def setup(self):
        """
        Setup the application environment and renderer.
        """
        self.clock = SimulationClock()

        self.environment = create_campus_environment(self.progress_window)

        self.robots = [Robot(count, self.environment) for count in range(Config.Simulation.NUM_ROBOTS)]


        self.renderer.add_objects_to_render(
            campus_map=self.environment,
            robots=self.robots,
            progress_window=self.progress_window
        )

        self.renderer.start()


    def run(self): 
        """
        Time loop for the application.
        """

        while True:
            dt = self.clock.tick()

            self.environment.update(self.clock.delta_time)

            self.renderer.update(self.clock.delta_time)

            time.sleep(1)

        