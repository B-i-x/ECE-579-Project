import tkinter as tk
import os

from PIL import Image, ImageTk

class BearDownBotsApp(tk.Tk):
    def __init__(self, width, height):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        # Top dashboard bar
        self.dashboard_frame = tk.Frame(self, height=80, bg="lightgrey")
        self.dashboard_frame.pack(side=tk.TOP, fill=tk.X)

        pkg_dir   = os.path.dirname(__file__)              # …/src/BearDownBots
        src_dir   = os.path.dirname(pkg_dir)               # …/src
        root_dir  = os.path.dirname(src_dir)               # …/ECE-579-Project
        assets_dir = os.path.join(root_dir, "assets")

        # Load icon images (ensure these files exist in your project directory)
        start_img = Image.open(os.path.join(assets_dir, "start_icon.png"))
        stop_img  = Image.open(os.path.join(assets_dir, "stop_icon.png"))
        start_resized = start_img.resize((32, 32), Image.LANCZOS)
        stop_resized  = stop_img.resize((32, 32), Image.LANCZOS)
        self.start_icon = ImageTk.PhotoImage(start_resized)
        self.stop_icon  = ImageTk.PhotoImage(stop_resized)
        # Start and Stop buttons on dashboard with icons
        self.start_button = tk.Button(
            self.dashboard_frame,
            image=self.start_icon,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            width=32,
            height=32
        )
        self.start_button.pack(side=tk.RIGHT, padx=10, pady=20)

        self.stop_button = tk.Button(
            self.dashboard_frame,
            image=self.stop_icon,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            width=32,
            height=32
        )
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=20)


        # Main content area: split screen
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: campus view
        self.campus_canvas = tk.Canvas(self.content_paned, bg="white")
        self.content_paned.add(self.campus_canvas)

        # Right pane: secondary dashboard / info canvas
        self.info_canvas = tk.Canvas(self.content_paned, bg="white", width=200)
        self.content_paned.add(self.info_canvas)

        # Move robot status to info_canvas using create_window
        self.robot_status_label = tk.Label(
            self.info_canvas,
            text="Robots Active: 3",
            font=("Arial", 14)
        )

                # Example widget on dashboard: order count
        self.order_count_label = tk.Label(
            self.info_canvas,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.order_count_label.pack(side=tk.LEFT, padx=10, pady=20)

        # Position at x=10, y=20 inside the canvas
        self.info_canvas.create_window(10, 20, anchor="nw", window=self.robot_status_label)

        # Now you can draw your campus on self.campus_canvas
        # and add other info widgets or graphics on self.info_canvas

if __name__ == "__main__":
    app = BearDownBotsApp(800, 600)
    app.mainloop()
