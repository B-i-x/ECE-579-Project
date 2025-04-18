import tkinter as tk

class BearDownBotsApp(tk.Tk):
    """
    Minimal Tkinter application for the FOODIE simulation.
    """
    def __init__(self):
        super().__init__()
        self.title("Foodie Delivery Simulator")
        # Optional: set a default size
        self.geometry("400x300")


