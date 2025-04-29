import tkinter as tk
from tkinter import ttk

class ProgressWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Progress")
        self.geometry("400x150")
        self.total_attempts = 0
        self.step_label = ""

        self.label = tk.Label(self, text="Starting...")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self, maximum=self.total_attempts, length=300)
        self.progress.pack(pady=10)

    def set_total_attempts(self, total_attempts: int):
        """Adjust the total number of steps for the next phase."""
        self.total_attempts = total_attempts
        self.progress.config(maximum=total_attempts)
        self.progress['value'] = 0

    def start_phase(self, phase_name: str, total_attempts: int):
        """
        Begin a new progress phase: reset bar, update label, and set new total.
        """
        self.step_label = phase_name
        self.set_total_attempts(total_attempts)
        self.label.config(text=f"{phase_name}: 0%")
        self.update_idletasks()

    def update_progress(self, attempt: int):
        """
        Update the progress bar to the given attempt count.
        """
        pct = attempt / self.total_attempts if self.total_attempts else 0
        self.label.config(text=f"{self.step_label}: {pct:.2%}")
        self.progress['value'] = attempt
        self.update_idletasks()
