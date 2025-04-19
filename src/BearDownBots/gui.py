import tkinter as tk

class BearDownBotsApp(tk.Tk):
    def __init__(self, width, height):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        # Top dashboard bar
        self.dashboard_frame = tk.Frame(self, height=80, bg="lightgrey")
        self.dashboard_frame.pack(side=tk.TOP, fill=tk.X)

        # Example widgets on dashboard
        self.order_count_label = tk.Label(
            self.dashboard_frame,
            text="Orders Placed: 0",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.order_count_label.pack(side=tk.LEFT, padx=10, pady=20)

        self.robot_status_label = tk.Label(
            self.dashboard_frame,
            text="Robots Active: 3",
            bg="lightgrey",
            font=("Arial", 14)
        )
        self.robot_status_label.pack(side=tk.LEFT, padx=10, pady=20)

        # Main content area: split screen
        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: campus view
        self.campus_canvas = tk.Canvas(self.content_paned, bg="white")
        self.content_paned.add(self.campus_canvas)

        # Right pane: secondary dashboard / info canvas
        self.info_canvas = tk.Canvas(self.content_paned, bg="white", width=200)
        self.content_paned.add(self.info_canvas)

        # Now you can draw your campus on self.campus_canvas
        # and other graphics or charts on self.info_canvas
