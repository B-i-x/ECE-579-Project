import os
import tkinter as tk
from PIL import Image, ImageTk

from BearDownBots.config import Config


class UserDashboardRenderer:
    def __init__(self, parent_frame: tk.Frame):
        self.parent = parent_frame
        self.assets_dir = Config.get_asset_dir()

           # — New: time label —
        self.time_label = tk.Label(self.parent,
                                   text="Time: 0.00s",
                                   font=("Arial", 14),
                                   bg="lightgrey")
        self.time_label.pack(side=tk.RIGHT, padx=10)
    
    
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
            bd=0, highlightthickness=0, relief=tk.FLAT,
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(
            self.center_frame, image=self.stop_icon,
            bd=0, highlightthickness=0, relief=tk.FLAT
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def start_clock(self, time_func, interval_ms=100):
        """
        Begin updating the time_label every interval_ms milliseconds,
        reading the current time from time_func().
        """
        self._time_func    = time_func
        self._interval_ms  = interval_ms
        self._update_clock()

    def _update_clock(self):
        current = self._time_func()
        # format however you like
        self.time_label.config(text=f"Time: {current:.2f}s")
        # schedule next update
        self.parent.after(self._interval_ms, self._update_clock)
