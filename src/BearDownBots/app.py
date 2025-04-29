from BearDownBots.environment import create_campus_environment
from BearDownBots.render.gui import GuiWrapper

class BearDownBotsApp():
    def __init__(self):
        self.environment = None  # Placeholder for the environment object
        self.renderer = None  # Placeholder for the renderer object
    
    def setup(self):
        """
        Setup the application environment and renderer.
        """
        # Initialize the environment and renderer here
        self.environment = create_campus_environment()
        self.renderer = GuiWrapper(self.environment)

        self.renderer.render_campus()

        
        self.renderer.mainloop()
