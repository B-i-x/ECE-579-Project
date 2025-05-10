import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image

from BearDownBots.dynamic.robot import Robot
from BearDownBots.config import Config
from BearDownBots.render.campus import CampusRenderer


class RestaurantDashboardRenderer:
    def __init__(self, parent):
        self.parent = parent
        self.robots = None
        self.robot_label = []
        self.order_queue = []  # no longer used for display, but you can keep if needed

        self.total_order_count = 0

        self._last_orders_signature: tuple = ()

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

        # --- separator & orders below ---
        separator = ttk.Separator(self.parent, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        self.order_frame = tk.Frame(self.parent, bg="lightgrey")
        self.order_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Order count
        self.order_count_label = tk.Label(
            self.order_frame,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )

        self.order_count_label.pack(anchor='w', padx=5, pady=(0,5))

        # === scrollable orders list ===
        scroll_frame = tk.Frame(self.order_frame)
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Canvas
        self.orders_canvas = tk.Canvas(
            scroll_frame,
            bg="white",
            bd=0,
            highlightthickness=0
        )
        # Scrollbars
        self.v_scroll = ttk.Scrollbar(
            scroll_frame,
            orient='vertical',
            command=self.orders_canvas.yview
        )
        self.h_scroll = ttk.Scrollbar(
            scroll_frame,
            orient='horizontal',
            command=self.orders_canvas.xview
        )
        # Configure canvas to scroll with them
        self.orders_canvas.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )

        # Layout using grid so both scrollbars and canvas align
        self.orders_canvas.grid(row=0, column=0, sticky='nsew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Inner frame where you’ll pack the order labels
        self.orders_list_frame = tk.Frame(self.orders_canvas, bg="white")
        self.orders_canvas.create_window((0, 0),
                                         window=self.orders_list_frame,
                                         anchor='nw')

        # Whenever inner frame grows, update scrollable region
        self.orders_list_frame.bind(
            "<Configure>",
            lambda e: self.orders_canvas.configure(
                scrollregion=self.orders_canvas.bbox("all")
            )
        )

    def _compute_signature(self) -> tuple:
        # e.g. each robot by its id and the tuple of its order-objects
        return tuple(
            (robot.id, tuple(id(o) for o in robot.orders))
            for robot in self.robots
        )
    
    def update_order_labels(self):
        # build a cheap signature of current orders
        sig = self._compute_signature()
        if sig == self._last_orders_signature:
            # no change in who has what orders → skip the whole repaint
            return
        # otherwise, remember this signature and do the full redraw:
        self._last_orders_signature = sig

        # 1) update the total count
        total = sum(len(r.orders) for r in self.robots)
        self.order_count_label.config(text=f"Orders Placed: {total}")

        # 2) clear out old list
        for widget in self.orders_list_frame.winfo_children():
            widget.destroy()

        # 3) repopulate…
        for robot in self.robots:
            if not robot.orders:
                continue
            hdr = tk.Label(
                self.orders_list_frame,
                text=f"{robot} ({len(robot.orders)}):",
                bg="lightgrey",
                font=("Arial", 12, "bold")
            )
            hdr.pack(anchor='w', padx=5, pady=(5,0))

            for order in robot.orders:
                dropoff = order.building.dropoff_point
                lbl = tk.Label(
                    self.orders_list_frame,
                    text=f"Drop-off at {order.building.name}({dropoff}) → {order}",
                    bg="white",
                    font=("Arial", 11)
                )
                lbl.pack(anchor='w', padx=15, pady=1)

    def setup_robot_click_event(self):
        """
        Bind the robot label to a click event that centers the campus view on the robot's position.
        """
        # print(f"Robot labels are {self.robot_label}")
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
        # --- pull live widget size and update renderer ---
        cw = cam.canvas.winfo_width()
        ch = cam.canvas.winfo_height()
        cam.canvas_w = cw
        cam.canvas_h = ch

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

        # 7) Finally redraw
        cam.render()

    def update(self):
        """
        Update the restaurant dashboard.
        """
        self.update_robot_labels()
        self.update_order_labels()



