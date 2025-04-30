import tkinter as tk
from PIL import Image, ImageTk
import os

from BearDownBots.config import Config

from BearDownBots.static.map import Map

from BearDownBots.render.campus import CampusRenderer
from BearDownBots.render.loading import ProgressWindow
from BearDownBots.render.user_dash import UserDashboardRenderer
from BearDownBots.render.restaurant_dash import RestaurantDashboardRenderer

class GuiWrapper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        self.setup()

    def setup(self):
         # --- Main window title & size ---
        width = Config.GUI.WINDOW_WIDTH_PIXELS
        height = Config.GUI.WINDOW_HEIGHT_PIXELS
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        self.user_dash_frame = tk.Frame(self, height=80, bg="lightgrey")
        self.user_dash_frame.pack(side=tk.TOP, fill=tk.X)
        self.user_dash = UserDashboardRenderer(self.user_dash_frame)
        self.user_dash.render()

        # --- Main split content area ---
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # Right pane: info canvas
        self.restaurant_dash_frame = tk.Canvas(self.content_paned, bg="white", width=200)
        self.content_paned.add(self.restaurant_dash_frame)
        self.restaurant_dash = RestaurantDashboardRenderer(self.restaurant_dash_frame)
        self.restaurant_dash.render()

    def render_campus(self, campus_map: Map, progress_window: ProgressWindow = None):
        """
        Render the campus map using CampusRenderer.
        """
        self.renderer = CampusRenderer(self.content_paned, campus_map, progress_window)

    def show_main_screen(self):
        """
        Show the main screen of the GUI.
        """
        self.deiconify()
        self.mainloop()

