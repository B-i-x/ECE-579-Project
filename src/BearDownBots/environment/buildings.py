# src/BearDownBots/environment/buildings.py

import random
import math

class Building:
    """Base class for all building types."""
    def __init__(self, cells: list[tuple[int,int]], height: int, width: int):
        self.cells  = cells   # list of (dr, dc) offsets from top-left
        self.h      = height
        self.w      = width

    def __repr__(self):
        return f"{self.__class__.__name__}(h={self.h}, w={self.w}, cells={len(self.cells)})"


class RectangleBuilding(Building):
    """A general rectangle with random width and height."""
    def __init__(self, min_cells: int, max_cells: int):
        base = random.randint(min_cells, max_cells)
        w    = random.randint(max(1, int(base*0.5)), int(base*2))
        h    = random.randint(max(1, int(base*0.5)), int(base*2))
        cells = [(dr, dc) for dr in range(h) for dc in range(w)]
        super().__init__(cells, h, w)


class RatioRectangleBuilding(Building):
    """A 1:2 aspect rectangle (or flipped)."""
    def __init__(self, min_cells: int, max_cells: int):
        base_max = max_cells // 2
        if min_cells > base_max:
            raise ValueError("Not enough room for a 1:2 rectangle")
        base = random.randint(min_cells, base_max)
        w, h = base, base * 2
        if random.random() < 0.5:
            w, h = h, w
        cells = [(dr, dc) for dr in range(h) for dc in range(w)]
        super().__init__(cells, h, w)


class SquareBuilding(Building):
    """A solid square."""
    def __init__(self, min_cells: int, max_cells: int):
        side = random.randint(min_cells, max_cells)
        cells = [(dr, dc) for dr in range(side) for dc in range(side)]
        super().__init__(cells, side, side)


class HollowSquareBuilding(Building):
    """A hollow square shell of configurable thickness."""
    def __init__(self, min_cells: int, max_cells: int, thickness: int = 1):
        # ensure side >= 2*thickness + 1
        side = random.randint(max(2*thickness + 1, min_cells), max_cells)
        cells = []
        for dr in range(side):
            for dc in range(side):
                if dr < thickness or dr >= side - thickness or \
                   dc < thickness or dc >= side - thickness:
                    cells.append((dr, dc))
        super().__init__(cells, side, side)


class TrapezoidBuilding(Building):
    """
    A trapezoid: top width vs bottom width interpolate over height.
    The bounding box width = max(top, bottom).
    """
    def __init__(self, min_cells: int, max_cells: int):
        h       = random.randint(min_cells, max_cells)
        top     = random.randint(min_cells, max_cells)
        bottom  = random.randint(min_cells, max_cells)
        max_w   = max(top, bottom)
        cells   = []
        for dr in range(h):
            if h > 1:
                w_i = round(top + (bottom - top) * dr / (h - 1))
            else:
                w_i = top
            offset = (max_w - w_i) // 2
            for dc in range(w_i):
                cells.append((dr, offset + dc))
        super().__init__(cells, h, max_w)
