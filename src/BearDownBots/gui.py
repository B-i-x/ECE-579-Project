import tkinter as tk

class BearDownBotsApp(tk.Tk):
    def __init__(self, width=600, height=60):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        # create a canvas that fills the window
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
