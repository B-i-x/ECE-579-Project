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

        # 2) draw each robot with the "robot" tag
        radius = 1
        z  = self.data.zoom
        ox = self.data.offset_x
        oy = self.data.offset_y

        for robot in robots:
            screen_x = robot.position.y * z - ox
            screen_y = robot.position.x * z - oy

            self.canvas.create_oval(
                screen_x - radius, screen_y - radius,
                screen_x + radius, screen_y + radius,
                fill=CELL_TYPES.ROBOT.color,
                outline='',
                tags=("robot",)
            )