# src/BearDownBots/environment/obstacles.py
import random
from BearDownBots.environment.cell import ObstacleCell, WalkwayCell

class ObstacleField:
    """
    After the Campus has carved its sidewalk network, turn a
    fraction of those walkway cells into static obstacles.

    Parameters
    ----------
    campus : Campus
        The fully‑constructed Campus instance.
    density : float
        Probability that any given walkway cell becomes an obstacle
        (typ. 1–5%).  Guaranteed not to block the warehouse cell.
    rng : random.Random | None
        For reproducible tests.
    """
    def __init__(self, campus, density: float = 0.02, rng=None):
        self.campus  = campus
        self.density = density
        self.rng     = rng or random

    def drop(self, forbid=None, color="#B22222"):
        forbid = forbid or set()
        cvs    = self.campus.canvas
        cs     = self.campus.cell_size

        for r in range(self.campus.rows):
            for c in range(self.campus.cols):
                if (r, c) in forbid:
                    continue
                cell = self.campus.grid.get_cell(r, c)
                if isinstance(cell, WalkwayCell) and self.rng.random() < self.density:
                    # ❶ flip the logical cell
                    self.campus.grid.set_cell(r, c, ObstacleCell(r, c))
                    # ❷ paint it immediately
                    x1, y1 = c*cs, r*cs
                    cvs.create_rectangle(
                        x1, y1, x1+cs, y1+cs,
                        fill=color,
                        outline="", width=0
                    )
