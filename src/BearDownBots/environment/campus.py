import random
from collections import deque
from BearDownBots.app_context import get_app

class Campus:
    """
    Randomly generates a campus map with large building blocks and narrow walkways,
    then draws it onto the global BearDownBotsApp.canvas. Ensures corridor connectivity.
    """
    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: int = 20,
        num_main_corridors: int = None
    ):
        self.rows      = rows
        self.cols      = cols
        self.cell_size = cell_size

        # pick 1 or 2 main corridors if not specified
        self.num_main_corridors = (
            num_main_corridors
            if num_main_corridors is not None
            else random.choice([1, 2])
        )

        # grab the singleton app & its canvas
        app = get_app()
        if not hasattr(app, "canvas"):
            raise RuntimeError("BearDownBotsApp must have a .canvas")
        self.canvas = app.canvas

        # initialize everything as building
        self.grid = [["building"] * self.cols for _ in range(self.rows)]

        # carve corridors & walkways
        self._generate_layout()

        # ensure connectivity
        self._ensure_connectivity()

        # draw the result
        self._draw_map()

    def _generate_layout(self):
        # ─── Main corridors (thickness=1, partial length) ───
        for _ in range(self.num_main_corridors):
            ori = random.choice(["horizontal", "vertical"])
            length = (random.randint(self.cols//3, self.cols//2)
                      if ori=="horizontal" else
                      random.randint(self.rows//3, self.rows//2))
            if ori == "horizontal":
                row = random.randint(self.rows//4, 3*self.rows//4)
                start = random.randint(0, self.cols-length)
                for c in range(start, start+length):
                    self.grid[row][c] = "main_walkway"
            else:
                col = random.randint(self.cols//4, 3*self.cols//4)
                start = random.randint(0, self.rows-length)
                for r in range(start, start+length):
                    self.grid[r][col] = "main_walkway"

        # ─── Secondary walkways (many short segments) ───
        count = random.randint((self.rows+self.cols)//10,
                               (self.rows+self.cols)//6)
        for _ in range(count):
            ori = random.choice(["horizontal", "vertical"])
            seg_len = random.randint(2, min(6, self.cols if ori=="horizontal" else self.rows))
            if ori == "horizontal":
                row = random.randint(1, self.rows-2)
                start = random.randint(0, self.cols-seg_len)
                for c in range(start, start+seg_len):
                    if self.grid[row][c] == "building":
                        self.grid[row][c] = "walkway"
            else:
                col = random.randint(1, self.cols-2)
                start = random.randint(0, self.rows-seg_len)
                for r in range(start, start+seg_len):
                    if self.grid[r][col] == "building":
                        self.grid[r][col] = "walkway"

    def _ensure_connectivity(self):
        # find all walkway cells
        walk_cells = {
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c] in ("walkway", "main_walkway")
        }
        if not walk_cells:
            return

        # helper to get neighbors
        def neighbors(cell):
            r, c = cell
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield (nr, nc)

        # find connected components
        comps = []
        seen = set()
        for cell in walk_cells:
            if cell in seen:
                continue
            # BFS for this component
            q = deque([cell])
            comp = {cell}
            seen.add(cell)
            while q:
                cur = q.popleft()
                for nb in neighbors(cur):
                    if nb in walk_cells and nb not in seen:
                        seen.add(nb)
                        comp.add(nb)
                        q.append(nb)
            comps.append(comp)

        # if more than one component, connect them to comp[0]
        main_comp = comps[0]
        for other in comps[1:]:
            # pick one cell from each
            r0, c0 = next(iter(main_comp))
            r1, c1 = next(iter(other))
            # carve an L‑shaped corridor between (r1,c1)→(r0,c0)
            # first horizontally, then vertically
            for c in range(min(c0,c1), max(c0,c1)+1):
                if self.grid[r1][c] == "building":
                    self.grid[r1][c] = "walkway"
            for r in range(min(r0,r1), max(r0,r1)+1):
                if self.grid[r][c0] == "building":
                    self.grid[r][c0] = "walkway"
            # merge the other comp into main_comp
            main_comp |= other

    def _draw_map(self):
        colors = {
            "building":     "#D2B48C",  # tan
            "walkway":      "#FFFFFF",  # white
            "main_walkway": "#CCCCCC",  # light gray
        }

        for r in range(self.rows):
            for c in range(self.cols):
                fill = colors[self.grid[r][c]]
                x1, y1 = c*self.cell_size, r*self.cell_size
                x2, y2 = x1+self.cell_size, y1+self.cell_size
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill, outline="black", width=1
                )

    def highlight_cell(self, r: int, c: int, color: str = "yellow"):
        x1 = c*self.cell_size + 1
        y1 = r*self.cell_size + 1
        x2 = x1 + self.cell_size - 2
        y2 = y1 + self.cell_size - 2
        items = self.canvas.find_enclosed(x1, y1, x2, y2)
        if items:
            self.canvas.itemconfig(items[0], fill=color)
