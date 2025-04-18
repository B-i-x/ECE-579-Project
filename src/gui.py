# src/foodie_ai/gui.py
import tkinter as tk
import threading

class FoodieApp(tk.Tk):
    """
    Main Tkinter application for running the FOODIE simulation with controls.
    """
    def __init__(self, duration: float, width: int, height: int):
        super().__init__()
        self.duration = duration
        self.env_size = (width, height)
        self.title("Foodie Delivery Simulator")
        self._create_widgets()

    def _create_widgets(self):
        controls = tk.Frame(self, padx=10, pady=10)
        controls.pack(fill=tk.X)

        tk.Label(controls, text="Map Size:").grid(row=0, column=0)
        self.size_label = tk.Label(controls, text=f"{self.env_size[0]}×{self.env_size[1]}")
        self.size_label.grid(row=0, column=1)

        tk.Label(controls, text="Duration:").grid(row=1, column=0)
        self.duration_label = tk.Label(controls, text=f"{self.duration} min")
        self.duration_label.grid(row=1, column=1)

        self.start_btn = tk.Button(controls, text="Start Simulation", command=self._on_start)
        self.start_btn.grid(row=2, column=0, columnspan=2, pady=(10,0))

        self.log = tk.Text(self, height=10, state='disabled')
        self.log.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

    def _on_start(self):
        """
        Disable controls and run simulation in background to keep GUI responsive.
        """
        self.start_btn.config(state='disabled')
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        """
        Execute the simulation and log output to the text box.
        """
        def logger(msg: str):
            self.log.config(state='normal')
            self.log.insert(tk.END, msg + '\n')
            self.log.see(tk.END)
            self.log.config(state='disabled')

        # Monkey-patch print to logger for the simulation run
        import builtins
        orig_print = builtins.print
        builtins.print = lambda *args, **kwargs: logger(' '.join(map(str,args)))
