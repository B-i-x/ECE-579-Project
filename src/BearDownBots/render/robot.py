import tkinter as tk

from BearDownBots.static.cell import CELL_TYPES

from BearDownBots.dynamic.robot import Robot
from BearDownBots.config import Config
from BearDownBots.static.cell import CELL_TYPES

class RobotRenderer:

    def __init__(self, 
                canvas: tk.Canvas,
                campus_renderer_data):
        """Initialize the RobotRenderer."""
        self.data = campus_renderer_data
        self.canvas = canvas

    def render_robots(self, robots: list[Robot]):
        """
        Draw each robot as a circle on the canvas, using the current
        zoom/offset from data. Clears any previous robot ovals first.
        """
        # 1) remove old robot ovals
        self.canvas.delete("robot")

        z  = self.data.zoom
        ox = self.data.offset_x
        oy = self.data.offset_y

        # pick a radius that's, say, 30% of one cell, but at least 3px
        world_radius = 0.5            # fraction of a cell
        min_px      = 3               # floor so it never vanishes
        radius      = max(min_px, int(world_radius * z))

        for robot in robots:
            screen_x = robot.position.y * z - ox
            screen_y = robot.position.x * z - oy

            self.canvas.create_oval(
                screen_x - radius, screen_y - radius,
                screen_x + radius, screen_y + radius,
                fill=robot.colour,
                outline='',
                tags=("robot",)
            )