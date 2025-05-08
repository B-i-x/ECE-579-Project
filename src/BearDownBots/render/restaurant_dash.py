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

        self.total_order_count = 0

    def add_robots(self, robots):
        """
        Add robots to the restaurant dashboard.
        """
        self.robots : list[Robot] = robots

    def add_campus_renderer_data(self, campus_renderer_obj, renderer_data):
        """
        Add the campus renderer to the restaurant dashboard.
        """
        self.campus_renderer_obj = campus_renderer_obj
        self.renderer_data = renderer_data

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
        self.order_count_label.pack(anchor='w', padx=5, pady=(0, 5))

          # --- NEW: Order list display ---
        self.order_listbox = tk.Listbox(self.order_frame, height=8, width=28, font=("Courier", 10))
        self.order_listbox.pack(fill='x', padx=5, pady=(0, 5))

    def add_order_to_listbox(self, building_name: str, order_id: str):
        """
        Add a single order to the listbox.
        """
        self.total_order_count += 1

        if hasattr(self, "order_listbox"):
            self.order_listbox.insert(0, f"{order_id} -> {building_name}")
            # Limit to most recent N orders (optional)
            if self.order_listbox.size() > 15:
                self.order_listbox.delete(15)
        
        if hasattr(self, "order_count_label"):
            self.order_count_label.config(text=f"Orders Placed: {self.total_order_count}")

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

    def update_robot_labels(self):
        """
        Update the robot labels with their current positions.
        """

        for robot in self.robots:
            # --- new label-update logic ---
            try:
                idx = self.robots.index(robot)
                selected_lbl = self.robot_label[idx]

                # 1) Refresh its text in case robot.__str__ shows updated info
                selected_lbl.config(text=str(robot))

                # 2) Highlight the selected label and reset others
                for lbl in self.robot_label:
                    lbl.config(bg="lightgrey")
                selected_lbl.config(bg="lightblue")

            except ValueError:
                # robot wasn’t found in the list—ignore
                pass

            
    def _on_robot_clicked(self, robot: Robot):
        """
        Center the campus view on robot.position at ROBOT_ZOOM_FACTOR scale,
        then re-render the campus map, clamping each axis only when needed.
        """
        cam   = self.campus_renderer_obj
        data  = self.renderer_data
        base  = cam._base_image
        cw, ch = cam.canvas_w, cam.canvas_h
        target_zoom = Config.GUI.ROBOT_ZOOM_FACTOR

        # 1) Apply zoom change first, if needed
        if data.zoom != target_zoom:
            data.zoom = target_zoom
            new_w = int(base.width  * data.zoom)
            new_h = int(base.height * data.zoom)
            cam._scaled_image = base.resize((new_w, new_h), Image.NEAREST)

        # 2) Map robot cell → pixel in the scaled image
        cell_x   = robot.position.y   # or .col
        cell_y   = robot.position.x   # or .row
        robot_px = cell_x * data.zoom
        robot_py = cell_y * data.zoom

        # 3) Compute raw offsets to center the robot
        raw_off_x = robot_px - cw / 2
        raw_off_y = robot_py - ch / 2

        # 4) Get the maximum allowable offsets
        scaled_w, scaled_h = cam._scaled_image.size
        max_off_x = scaled_w - cw
        max_off_y = scaled_h - ch

        # 5) Clamp each axis only if there's “room to pan”
        if max_off_x > 0:
            data.offset_x = max(0, min(raw_off_x, max_off_x))
        else:
            data.offset_x = 0

        if max_off_y > 0:
            data.offset_y = max(0, min(raw_off_y, max_off_y))
        else:
            data.offset_y = 0

        # 6) Push the updated values back onto the renderer
        cam.zoom     = data.zoom
        cam.offset_x = data.offset_x
        cam.offset_y = data.offset_y

        # 7) Finally redraw
        cam.render()



