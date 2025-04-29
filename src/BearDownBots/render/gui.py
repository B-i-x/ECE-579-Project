import tkinter as tk
from math import floor
from PIL import Image, ImageDraw, ImageTk

from BearDownBots.config import Config
from BearDownBots.environment.cell import CELL_TYPES
from BearDownBots.environment.map import Map

from BearDownBots.render.campus import CampusRenderer

class GuiWrapper(tk.Tk):
    def __init__(self, campus_map: Map):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{Config.GUI.WINDOW_WIDTH_PIXELS}x{Config.GUI.WINDOW_HEIGHT_PIXELS}")
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)
        # embed CampusRenderer
        self.renderer = CampusRenderer(self.content_paned, campus_map)
