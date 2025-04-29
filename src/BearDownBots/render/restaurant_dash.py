import os
import tkinter as tk
from PIL import Image, ImageTk

class RestaurantDashboardRenderer:
    def __init__(self, parent_frame: tk.Frame):
        self.parent = parent_frame

    def render(self):
        """
        Render the info canvas with a placeholder image and text.
        """

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