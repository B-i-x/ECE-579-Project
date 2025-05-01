# src/BearDownBots/environment/obstacles.py
import random
from typing import Set, Tuple, List

from BearDownBots.static.cell import WalkwayCell, ObstacleCell

Coord = Tuple[int, int]


class ObstacleField:
    """
    Place a fixed number of brick‑red obstacles on random walkway cells.

    Parameters
    ----------
    campus         : the Campus instance (already fully built & drawn)
    rng            : optional random‑number generator for reproducibility
    """

    def __init__(self, campus, rng=None):
        self.campus = campus
        self.rng    = rng or random

    # ------------------------------------------------------------------ #
    # ▸ PUBLIC API
    # ------------------------------------------------------------------ #
    def drop(
        self,
        num_obstacles: int,
        forbid: Set[Coord] | None = None,
        color: str = "#B22222",
    ):
        """
        Sprinkle exactly `num_obstacles` blocks on random walkways.

        * `forbid`  : set of (row, col) coordinates that must stay free
                      (e.g. the warehouse entrance).

        Raises
        ------
        ValueError if num_obstacles > available walkway cells.
        """
        forbid = forbid or set()

        # ------------------------------------------------------------------
        # 1) Build a list of eligible walkway cells
        walkway_cells: List[Coord] = [
            (r, c)
            for r in range(self.campus.rows)
            for c in range(self.campus.cols)
            if self.campus.grid.get_cell(r, c).type == "walkway"
               and (r, c) not in forbid
        ]

        if num_obstacles > len(walkway_cells):
            raise ValueError(
                f"Requested {num_obstacles} obstacles but only "
                f"{len(walkway_cells)} walkway cells are available."
            )

        # ------------------------------------------------------------------
        # 2) Pick N unique positions
        chosen = self.rng.sample(walkway_cells, num_obstacles)

        # ------------------------------------------------------------------
        # 3) Convert each to ObstacleCell and draw it immediately
        cvs, cs = self.campus.canvas, self.campus.cell_size
        for r, c in chosen:
            self.campus.grid.set_cell(r, c, ObstacleCell(r, c))
            x1, y1 = c * cs, r * cs
            cvs.create_rectangle(
                x1, y1, x1 + cs, y1 + cs,
                fill=color,
                outline="", width=0,
            )
