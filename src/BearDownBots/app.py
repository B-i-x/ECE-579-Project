from BearDownBots.environment import create_campus_environment
from BearDownBots.render.gui import GuiWrapper
from BearDownBots.config import Config
from BearDownBots.render.loading import ProgressWindow
from BearDownBots.clock import SimulationClock

import time
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
        self.clock = SimulationClock
        self.environment = create_campus_environment(self.progress_window)

        self.renderer.setup()

        self.renderer.render_campus(self.environment, self.progress_window)

        self.progress_window.destroy()  #setup is done

        self.renderer.show_main_screen()


    def run(self): 
        """
        Time loop for the application.
        """

        while True:
            dt = self.clock.tick()

            self.environment.update(self.clock.delta_time)
            self.renderer.update(self.clock.delta_time)

            time.sleep(1)

        