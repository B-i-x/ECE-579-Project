import tkinter as tk

from BearDownBots.config import Config

from BearDownBots.environment.map import Map

from BearDownBots.render.campus import CampusRenderer
from BearDownBots.render.loading import ProgressWindow

class GuiWrapper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()


    def setup(self):

        self.title("Bear Down Bots Simulator")

        self.geometry(f"{Config.GUI.WINDOW_WIDTH_PIXELS}x{Config.GUI.WINDOW_HEIGHT_PIXELS}")
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

    def render_campus(self, campus_map: Map, progress_window: ProgressWindow = None):
        """
        Render the campus map using CampusRenderer.
        """
        self.renderer = CampusRenderer(self.content_paned, campus_map, progress_window)

