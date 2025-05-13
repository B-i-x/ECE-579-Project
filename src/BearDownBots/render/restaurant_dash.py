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

        self._shown = {
            OrderStatus.PLACED:    {},   # order_id -> Label
            OrderStatus.PREPARING: {},
            OrderStatus.READY:     {},
            "DELIVERING_HDR": {},        # robot_id -> header Label
            "DELIVERING_ORD": {}         # (robot_id, order_id) -> Label
        }

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

        # 1) Build the desired buckets of order_ids
        desired = {
            OrderStatus.PLACED:    set(),
            OrderStatus.PREPARING: set(),
            OrderStatus.READY:     set(),
        }
        for building, order in self.scheduler.orders:
            if order.status in desired:
                desired[order.status].add(id(order))

        # 2) Diff & update each non‐delivering tab
        for status, tab in ((OrderStatus.PLACED, self.tab_new),
                            (OrderStatus.PREPARING, self.tab_prep),
                            (OrderStatus.READY, self.tab_ready)):
            shown = self._shown[status]
            # remove labels no longer desired
            for oid in list(shown):
                if oid not in desired[status]:
                    shown[oid].destroy()
                    del shown[oid]
            # add any new orders
            for building, order in self.scheduler.orders:
                oid = id(order)
                if order.status == status and oid not in shown:
                    lbl = self._add_label(tab, f"{building.name} → {order}")
                    shown[oid] = lbl

        # 3) Delivering tab: handle headers and order items per robot
        # Track which robot‐headers and which (robot,order) pairs we now need
        desired_hdr = set()
        desired_ord = set()
        for robot in self.robots:
            if not robot.orders:
                continue
            desired_hdr.add(robot.id)
            for order in robot.orders:
                desired_ord.add( (robot.id, id(order)) )

        # remove old headers
        for rid, hdr_lbl in list(self._shown["DELIVERING_HDR"].items()):
            if rid not in desired_hdr:
                hdr_lbl.destroy()
                del self._shown["DELIVERING_HDR"][rid]
        # add new headers
        for robot in self.robots:
            if robot.orders and robot.id not in self._shown["DELIVERING_HDR"]:
                hdr = tk.Label(
                    self.tab_delivering,
                    text=f"{robot} ({len(robot.orders)})",
                    bg="lightgrey", font=("Arial", 11, "bold")
                )
                hdr.pack(anchor='w', padx=4, pady=(4,1))
                self._shown["DELIVERING_HDR"][robot.id] = hdr

        # remove old order‐labels
        for key, lbl in list(self._shown["DELIVERING_ORD"].items()):
            if key not in desired_ord:
                lbl.destroy()
                del self._shown["DELIVERING_ORD"][key]
        # add new order‐labels
        for robot in self.robots:
            if not robot.orders:
                continue
            for order in robot.orders:
                key = (robot.id, id(order))
                if key not in self._shown["DELIVERING_ORD"]:
                    lbl = self._add_label(
                        self.tab_delivering, f"→ {order.building.name} : {order}"
                    )
                    self._shown["DELIVERING_ORD"][key] = lbl


    def update(self):
        self.update_robot_labels()
        self.update_order_labels()

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------
    def _add_label(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            bg="white",
            font=("Arial", 10),
            anchor="w",
            justify="left",
            wraplength=220
        )
        lbl.pack(fill='x', padx=12, pady=1)

        return lbl


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