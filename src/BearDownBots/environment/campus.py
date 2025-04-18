import random
from BearDownBots.app_context import get_app

class Campus:
    """
    Places roughly‐square buildings randomly on a grid, ensuring
    at least a one‐cell walkway margin between them.
    Everything not occupied by a building is considered walkway.
    """
    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: int = 20,
        num_attempts: int = 500
    ):
        self.rows      = rows
        self.cols      = cols
        self.cell_size = cell_size
        self._buffer   = 1  # one‐cell margin

        app = get_app()
        if not hasattr(app, "canvas"):
            raise RuntimeError("BearDownBotsApp must have a .canvas")
        self.canvas = app.canvas

        # try placing up to num_attempts buildings
        self._place_buildings(num_attempts)
        # build the cell grid from building footprints
        self._fill_grid()
        # draw the final map
        self._draw_map()

    def _place_buildings(self, num_attempts: int):
        self.buildings = []  # list of (r0, c0, h, w)
        for _ in range(num_attempts):
            # pick a “base size” between 1/10 and 1/4 of the smaller dimension
            base = random.randint(
                min(self.rows, self.cols)//10,
                max(2, min(self.rows, self.cols)//4)
            )
            # give it ±20% randomness
            w = random.randint(int(base*0.8), int(base*1.2))
            h = random.randint(int(base*0.8), int(base*1.2))
            # clamp sizes so they actually fit
            w = max(2, min(w, self.cols - 2))
            h = max(2, min(h, self.rows - 2))

            # pick a random top‐left that stays on the board
            r0 = random.randint(0, self.rows - h)
            c0 = random.randint(0, self.cols - w)

            # build the buffered rectangle (including 1‐cell margin)
            br0 = max(0, r0 - self._buffer)
            bc0 = max(0, c0 - self._buffer)
            br1 = min(self.rows - 1, r0 + h - 1 + self._buffer)
            bc1 = min(self.cols - 1, c0 + w - 1 + self._buffer)

            # test against every existing building’s true footprint
            conflict = False
            for (or0, oc0, oh, ow) in self.buildings:
                or1 = or0 + oh - 1
                oc1 = oc0 + ow - 1
                # do rectangles [br0..br1]×[bc0..bc1] vs [or0..or1]×[oc0..oc1] overlap?
                if not (br1 < or0 or br0 > or1 or bc1 < oc0 or bc0 > oc1):
                    conflict = True
                    break

            if not conflict:
                # accepts this building
                self.buildings.append((r0, c0, h, w))

    def _fill_grid(self):
        # start with every cell = walkway
        self.grid = [["walkway"] * self.cols for _ in range(self.rows)]
        # paint in each building
        for (r0, c0, h, w) in self.buildings:
            for r in range(r0, r0 + h):
                for c in range(c0, c0 + w):
                    self.grid[r][c] = "building"

    def _draw_map(self):
        colors = {
            "building": "#D2B48C",  # tan
            "walkway":  "#FFFFFF",  # white
        }
        for r in range(self.rows):
            for c in range(self.cols):
                fill = colors[self.grid[r][c]]
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill, outline="black", width=1
                )

    def highlight_cell(self, r: int, c: int, color: str = "yellow"):
        """Recolor a single cell after drawing."""
        x1 = c*self.cell_size + 1
        y1 = r*self.cell_size + 1
        x2 = x1 + self.cell_size - 2
        y2 = y1 + self.cell_size - 2
        items = self.canvas.find_enclosed(x1, y1, x2, y2)
        if items:
            self.canvas.itemconfig(items[0], fill=color)
