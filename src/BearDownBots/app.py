from BearDownBots.environment import create_campus_environment
from BearDownBots.render.gui import GuiWrapper
from BearDownBots.config import Config
from BearDownBots.render.loading import ProgressWindow

class BearDownBotsApp():
    def __init__(self):
        self.environment = None  # Placeholder for the environment object
        self.renderer = None  # Placeholder for the renderer object
    
    def run(self):
        """
        Setup the application environment and renderer.
        """
        # Initialize the environment and renderer here
        self.renderer = GuiWrapper()

        progress_window = ProgressWindow(self.renderer)

        self.environment = create_campus_environment(progress_window)

        self.renderer.setup()
        self.renderer.render_campus(self.environment, progress_window)

        progress_window.destroy()  # once done, close the popup

        self.renderer.deiconify()

        self.renderer.mainloop()
