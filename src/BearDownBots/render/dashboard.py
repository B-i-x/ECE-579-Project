import os
import tkinter as tk
from PIL import Image, ImageTk


class DashboardRenderer:
    def __init__(self, parent_frame: tk.Frame, assets_dir: str):
        self.parent = parent_frame
        self.assets_dir = assets_dir

    def render(self):
        # Load and resize icons
        start_img = Image.open(os.path.join(self.assets_dir, "start_icon.png"))
        stop_img  = Image.open(os.path.join(self.assets_dir, "stop_icon.png"))
        self.start_icon = ImageTk.PhotoImage(start_img.resize((32, 32), Image.LANCZOS))
        self.stop_icon  = ImageTk.PhotoImage(stop_img.resize((32, 32), Image.LANCZOS))

        # Center frame for Start/Stop buttons
        self.center_frame = tk.Frame(self.parent, bg="lightgrey")
        self.center_frame.pack(side=tk.LEFT, expand=True)
        self.start_button = tk.Button(
            self.center_frame, image=self.start_icon,
            bd=0, highlightthickness=0, relief=tk.FLAT
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(
            self.center_frame, image=self.stop_icon,
            bd=0, highlightthickness=0, relief=tk.FLAT
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Orders Placed label
        self.order_count_label = tk.Label(
            self.parent,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.order_count_label.pack(side=tk.LEFT, padx=10, pady=20)

        # Robots Active label
        self.robot_status_label = tk.Label(
            self.parent,
            text="Robots Active: 3",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.robot_status_label.pack(side=tk.LEFT, padx=10, pady=20)