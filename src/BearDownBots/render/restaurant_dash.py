import tkinter as tk
from tkinter import ttk
from PIL import Image

from BearDownBots.config import Config
from BearDownBots.dynamic.robot import Robot
from BearDownBots.dynamic.randOrders import OrderStatus


class RestaurantDashboardRenderer:
    """
    Left-pane dashboard with:
        • robot list
        • four notebook tabs (Placed / Preparing / Ready / Out for Delivery)
    """

    # ------------------------------------------------------------
    # construction
    # ------------------------------------------------------------
    def __init__(self, parent):
        self.parent   = parent
        self.robots   = []       # set later with add_robots()
        self.scheduler = None

        self.robot_label = []

    # ------------------------------------------------------------
    # one-off wiring helpers
    # ------------------------------------------------------------
    def add_robots(self, robots):
        self.robots = robots

    def add_scheduler(self, scheduler):
        self.scheduler = scheduler

    def add_campus_renderer_data(self, campus_renderer_obj, renderer_data):
        """Allows robot-click to recentre the map."""
        self.campus_renderer_obj = campus_renderer_obj
        self.renderer_data       = renderer_data

    # ------------------------------------------------------------
    # UI building
    # ------------------------------------------------------------
    def render(self):
        # ---------- robot list ----------
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

        # ---------- separator ----------
        ttk.Separator(
            self.parent, orient='horizontal'
        ).pack(fill='x', padx=10, pady=5)

        # ---------- four-tab notebook ----------
        nb_frame = tk.Frame(self.parent, bg="lightgrey")
        nb_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        self.notebook = ttk.Notebook(nb_frame)
        self.notebook.pack(fill='both', expand=True)

        def _make_tab(title: str):
            outer  = tk.Frame(self.notebook, bg="lightgrey")
            self.notebook.add(outer, text=title)

            canvas = tk.Canvas(outer, bg="white", bd=0, highlightthickness=0)
            vbar   = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
            canvas.configure(yscrollcommand=vbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            vbar.pack  (side='right', fill='y')

            inner = tk.Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=inner, anchor='nw')
            inner.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            return inner

        self.tab_new        = _make_tab("Placed")
        self.tab_prep       = _make_tab("Preparing")
        self.tab_ready      = _make_tab("Ready")
        self.tab_delivering = _make_tab("Out for Delivery")

        # keep wrap-length tidy as each tab resizes
        for inner in (
            self.tab_new, self.tab_prep, self.tab_ready, self.tab_delivering
        ):
            inner.bind("<Configure>", self._on_inner_resize, add="+")

        # click-to-centre handlers for robot labels
        self.setup_robot_click_event()

    # ------------------------------------------------------------
    # periodic updates
    # ------------------------------------------------------------
    def update_robot_labels(self):
        for idx, robot in enumerate(self.robots):
            lbl = self.robot_label[idx]
            lbl.config(text=str(robot))

    def update_order_labels(self):
        if self.scheduler is None:
            return

        # clear every tab
        for tab in (
            self.tab_new, self.tab_prep, self.tab_ready, self.tab_delivering
        ):
            for widget in tab.winfo_children():
                widget.destroy()

        # --- tickets not yet on robots ---------------------------
        bucket = {
            OrderStatus.PLACED:    self.tab_new,
            OrderStatus.PREPARING: self.tab_prep,
            OrderStatus.READY:     self.tab_ready,
        }

        for building, order in self.scheduler.orders:
            # skip OUT_FOR_DELIVERY here – they’re handled in the next loop
            if order.status not in bucket:
                continue

            parent = bucket[order.status]
            self._add_label(parent, f"{building.name} → {order}")

        # --- tickets already loaded ------------------------------
        for robot in self.robots:
            if not robot.orders:
                continue

            hdr = tk.Label(
                self.tab_delivering,
                text=f"{robot} ({len(robot.orders)})",
                bg="lightgrey",
                font=("Arial", 11, "bold")
            )
            hdr.pack(anchor='w', padx=4, pady=(4, 1))

            for ord in robot.orders:
                self._add_label(
                    self.tab_delivering,
                    f"→ {ord.building.name} : {ord}"
                )

    def update(self):
        self.update_robot_labels()
        self.update_order_labels()

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------
    def _add_label(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg="white",
            font=("Arial", 10),
            anchor="w",
            justify="left",
            wraplength=220
        ).pack(fill='x', padx=12, pady=1)

    def _on_inner_resize(self, event):
        """Auto-adjust wrap-length when a tab’s frame is resized."""
        wrap = max(event.width - 30, 50)
        for child in event.widget.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(wraplength=wrap, justify="left")

    # ------------------------------------------------------------
    # click-to-centre logic (unchanged from your version)
    # ------------------------------------------------------------
    def setup_robot_click_event(self):
        for idx, lbl in enumerate(self.robot_label):
            lbl.bind("<Button-1>", self._make_robot_click_handler(self.robots[idx]))

    def _make_robot_click_handler(self, robot):
        def handler(event):
            self._on_robot_clicked(robot)
        return handler

    def _on_robot_clicked(self, robot: Robot):
        cam   = self.campus_renderer_obj
        data  = self.renderer_data
        base  = cam._base_image

        cw, ch       = cam.canvas.winfo_width(), cam.canvas.winfo_height()
        cam.canvas_w = cw
        cam.canvas_h = ch

        target_zoom = Config.GUI.ROBOT_ZOOM_FACTOR
        if data.zoom != target_zoom:
            data.zoom = target_zoom
            new_w = int(base.width  * data.zoom)
            new_h = int(base.height * data.zoom)
            cam._scaled_image = base.resize((new_w, new_h), Image.NEAREST)

        cell_x, cell_y = robot.position.y, robot.position.x
        robot_px = cell_x * data.zoom
        robot_py = cell_y * data.zoom

        raw_off_x = robot_px - cw / 2
        raw_off_y = robot_py - ch / 2

        scaled_w, scaled_h = cam._scaled_image.size
        max_off_x = scaled_w - cw
        max_off_y = scaled_h - ch

        data.offset_x = max(0, min(raw_off_x, max_off_x)) if max_off_x > 0 else 0
        data.offset_y = max(0, min(raw_off_y, max_off_y)) if max_off_y > 0 else 0

        cam.render()
