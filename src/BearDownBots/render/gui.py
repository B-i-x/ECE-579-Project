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

        # Main window title and size
        width = Config.GUI.WINDOW_WIDTH_PIXELS
        height = Config.GUI.WINDOW_HEIGHT_PIXELS
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        # Top dashboard bar
        self.dashboard_frame = tk.Frame(self, height=80, bg="lightgrey")
        self.dashboard_frame.pack(side=tk.TOP, fill=tk.X)

        # Dashboard widgets
        self.order_count_label = tk.Label(
            self.dashboard_frame,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.order_count_label.pack(side=tk.LEFT, padx=10, pady=20)

        self.robot_status_label = tk.Label(
            self.dashboard_frame,
            text="Robots Active: 3",
            bg="lightgrey",
            font=("Arial", 14)
        )
        
        self.robot_status_label.pack(side=tk.LEFT, padx=10, pady=20)

        # Main split content area
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: will hold campus renderer
        # Right pane: information canvas
        self.info_canvas = tk.Canvas(self.content_paned, bg="white", width=200)
        self.content_paned.add(self.info_canvas)

    def render_campus(self, campus_map: Map, progress_window: ProgressWindow = None):
        """
        Render the campus map using CampusRenderer.
        """
        self.renderer = CampusRenderer(self.content_paned, campus_map, progress_window)

