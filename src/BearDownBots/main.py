import tkinter as tk

class FoodieApp(tk.Tk):
    """
    Minimal Tkinter application for the FOODIE simulation.
    """
    def __init__(self):
        super().__init__()
        self.title("Foodie Delivery Simulator")
        # Optional: set a default size
        self.geometry("400x300")

if __name__ == "__main__":
    app = FoodieApp()
    app.mainloop()
