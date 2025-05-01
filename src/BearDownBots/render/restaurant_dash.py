import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image

from BearDownBots.dynamic.robot import Robot
from BearDownBots.config import Config
from BearDownBots.render.campus import CampusRenderer

class RestaurantDashboardRenderer:
    def __init__(self, parent_frame: tk.Frame):
        self.parent = parent_frame

        self.robot_label : list[tk.Label] = []

    def add_robots(self, robots):
        """
        Add robots to the restaurant dashboard.
        """
        self.robots : list[Robot] = robots

    def add_campus_renderer(self, campus_renderer: CampusRenderer):
        """
        Add the campus renderer to the restaurant dashboard.
        """
        self.campus_renderer : CampusRenderer = campus_renderer

    def render(self):
        # --- top: robot labels ---
        self.robot_frame = tk.Frame(self.parent, bg="lightgrey")
        self.robot_frame.pack(fill='x', padx=10, pady=(10, 5))

        for robot in self.robots:
            lbl = tk.Label(
                self.robot_frame,
                text=str(robot),
                bg="lightgrey",
                font=("Arial", 14)
            )
            lbl.pack(anchor='w', pady=2)

            self.robot_label.append(lbl)
            

        # --- separator & orders below (unchanged) ---
        separator = ttk.Separator(self.parent, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        self.order_frame = tk.Frame(self.parent, bg="lightgrey")
        self.order_frame.pack(fill='x', padx=10, pady=(5, 10))

        self.order_count_label = tk.Label(
            self.order_frame,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.order_count_label.pack(side=tk.LEFT, padx=5, pady=5)

    def setup_robot_click_event(self):
        """
        Bind the robot label to a click event that centers the campus view on the robot's position.
        """
        print(f"Robot labels are {self.robot_label}")
        # Bind the click event to the robot label
        for robot_index, lbl in enumerate(self.robot_label):
            handler = self._make_robot_click_handler(self.robots[robot_index])
            lbl.bind("<Button-1>", handler)

    def _make_robot_click_handler(self, robot):
        def handler(event):
            self._on_robot_clicked(robot)
        return handler

    def _on_robot_clicked(self, robot: Robot):
        """
        Center the campus view on robot.position at ROBOT_ZOOM_FACTOR scale,
        then re-render the campus map, clamping each axis only when needed.
        """
        cam         = self.campus_renderer
        base        = cam._base_image
        cw, ch      = cam.canvas_w, cam.canvas_h
        target_zoom = Config.GUI.ROBOT_ZOOM_FACTOR

        # 1) Apply zoom change first, if needed
        if cam.zoom != target_zoom:
            cam.zoom = target_zoom
            new_w = int(base.width  * target_zoom)
            new_h = int(base.height * target_zoom)
            cam._scaled_image = base.resize((new_w, new_h), Image.NEAREST)

        # 2) Map robot cell → pixel in the scaled image
        cell_x   = robot.position.x   # or .col
        cell_y   = robot.position.y   # or .row
        robot_px = cell_x * cam.zoom
        robot_py = cell_y * cam.zoom

        # 3) Compute raw offsets to center the robot
        raw_off_x = robot_px - cw / 2
        raw_off_y = robot_py - ch / 2

        # 4) Get the maximum allowable offsets
        scaled_w, scaled_h = cam._scaled_image.size
        max_off_x = scaled_w - cw
        max_off_y = scaled_h - ch

        # 5) Clamp each axis only if there's “room to pan”
        if max_off_x > 0:
            cam.offset_x = max(0, min(raw_off_x, max_off_x))
        else:
            # map is narrower or exactly fits: just left-align
            cam.offset_x = 0

        if max_off_y > 0:
            cam.offset_y = max(0, min(raw_off_y, max_off_y))
        else:
            # map is shorter or exactly fits: top-align
            cam.offset_y = 0

        # 6) Finally redraw
        cam.render()



