import random
from BearDownBots.app_context import get_app
from BearDownBots.environment.grid import Grid
from BearDownBots.environment.cell import Cell, BuildingCell, WalkwayCell, RestaurantCell
from BearDownBots.environment.buildings import (
    RectangleBuilding,
    RatioRectangleBuilding,
    SquareBuilding,
    HollowSquareBuilding,
    TrapezoidBuilding,
)
from BearDownBots.environment.randOrders import OrderGenerator

SHAPE_CLASSES = {
    "rectangle":       RectangleBuilding,
    "ratio_rectangle": RatioRectangleBuilding,
    "square":          SquareBuilding,
    "hollow_square":   HollowSquareBuilding,
    "trapezoid":       TrapezoidBuilding,
}

colors = {
    "building": "#D2B48C",
    "walkway":  "#808080",
    "obstacle": "#B22222",   # ← deep red for clarity
}

class Campus:
    """
    Places varied‐shaped buildings in one pass:
      • rectangle          (random W×H)
      • ratio_rectangle    (aspect ≈1:2)
      • square             (solid)
      • hollow_square      (shell)
      • trapezoid          (linear interpolation between top/bottom widths)

    You can control the relative probabilities of each shape by passing
    a `shape_probabilities` dict, e.g.:

        shape_probabilities = {
          "rectangle":       0.4,
          "ratio_rectangle": 0.2,
          "square":          0.2,
          "hollow_square":   0.1,
          "trapezoid":       0.1,
        }
    """
    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: int = 2,
        ft_per_cell: int = 10,
        # building size bounds (in feet)
        b_min_ft: int = 250,
        b_max_ft: int = 500,
        num_attempts: int = 200,
        hollow_thickness: int = 10,

        shape_probabilities: dict = None
    ):
        self.rows        = rows
        self.cols        = cols
        self.cell_size   = cell_size
        self.ft_per_cell = ft_per_cell

        self.min_cells = max(1, b_min_ft // ft_per_cell)
        self.max_cells = max(self.min_cells, b_max_ft // ft_per_cell)
        self.buffer    = 1  # 1‑cell (=10ft) buffer

        self.hollow_thickness = hollow_thickness

        self.grid = Grid(rows, cols)

        app = get_app()
        if not hasattr(app, "campus_canvas"):
            raise RuntimeError("BearDownBotsApp must have a .canvas")
        self.canvas = app.campus_canvas

        # default uniform probs, now including trapezoid
        default_probs = {
            "rectangle":       0.9,
            "ratio_rectangle": 1.0,
            "square":          0.8,
            "hollow_square":   0.1,
            "trapezoid":       0.3,
        }
        self.shape_probs = shape_probabilities or default_probs

        total = sum(self.shape_probs.values())
        self.shapes  = list(self.shape_probs.keys())
        self.weights = [self.shape_probs[s]/total for s in self.shapes]

        # Place buildings
        self.buildings = []
        self._place_buildings(
            attempts  = num_attempts,
            min_cells = self.min_cells,
            max_cells = self.max_cells
        )

        self.restaurant_bldg = self.buildings[0]
        self.restaurant_bldg["name"] = "Bear Down Express"

        self.restaurant_coords = set(
            (self.restaurant_bldg["r0"] + dr,
             self.restaurant_bldg["c0"] + dc)
            for dr, dc in self.restaurant_bldg["cells"]
        )

        # Fill & draw
        self._fill_grid()
        self._draw_map()
        self._assign_entry_points()


    def _place_buildings(self, attempts, min_cells, max_cells):
        next_id = 1
        for _ in range(attempts):
            kind = random.choices(self.shapes, weights=self.weights, k=1)[0]
            cls  = SHAPE_CLASSES[kind]
            if kind == "hollow_square":
                bld = cls(min_cells, max_cells, self.hollow_thickness)
            else:
                bld = cls(min_cells, max_cells)
            cells, h, w = bld.cells, bld.h, bld.w

            # skip if building+buffer won't fit
            if w + 2*self.buffer > self.cols or h + 2*self.buffer > self.rows:
                continue

            # random origin that respects buffer
            r0 = random.randint(self.buffer, self.rows - h - self.buffer)
            c0 = random.randint(self.buffer, self.cols - w - self.buffer)

            # inflated bbox for spacing test
            br0, bc0 = r0 - self.buffer, c0 - self.buffer
            br1 = r0 + h - 1 + self.buffer
            bc1 = c0 + w - 1 + self.buffer

            conflict = False
            for b in self.buildings:
                or0, oc0, oh, ow = b["r0"], b["c0"], b["h"], b["w"]
                or1, oc1 = or0 + oh - 1, oc0 + ow - 1
                if not (br1 < or0 or br0 > or1 or bc1 < oc0 or bc0 > oc1):
                    conflict = True
                    break

            if not conflict:
                self.buildings.append({"id":   next_id, "cells": cells, "r0": r0, "c0": c0, "h": h, "w": w, "kind": kind})
                next_id += 1

    def get_building_by_id(self, bid: int):
        """Return the building dict with matching id (or None)."""
        for b in self.buildings:
            if b["id"] == bid:
                return b
        return None

    def _make_shape(self, kind, min_c, max_c):
        """
        Returns (cells_list, height, width) or None if unbuildable.
        cells_list is offsets (dr,dc) from the top‑left corner.
        """
        # rectangle
        if kind == "rectangle":
            base = random.randint(min_c, max_c)
            w = random.randint(max(1,int(base*0.5)), int(base*2))
            h = random.randint(max(1,int(base*0.5)), int(base*2))
            cells = [(dr, dc) for dr in range(h) for dc in range(w)]
            return (cells, h, w)

        # ratio_rectangle (1:2 aspect)
        if kind == "ratio_rectangle":
            base_max = max_c // 2
            if min_c > base_max:
                return None
            base = random.randint(min_c, base_max)
            w, h = base, base*2
            if random.random() < 0.5:
                w, h = h, w
            cells = [(dr, dc) for dr in range(h) for dc in range(w)]
            return (cells, h, w)

        # solid square
        if kind == "square":
            side = random.randint(min_c, max_c)
            cells = [(dr, dc) for dr in range(side) for dc in range(side)]
            return (cells, side, side)

        # hollow square
        if kind == "hollow_square":
            # ensure side is at least big enough to fit two borders
            side = random.randint(
                max(2*self.hollow_thickness + 1, min_c),
                max_c
            )
            t = self.hollow_thickness
            cells = []
            for dr in range(side):
                for dc in range(side):
                    # include any cell within t of the outer edge
                    if dr < t or dr >= side - t or dc < t or dc >= side - t:
                        cells.append((dr, dc))
            return (cells, side, side)

        # trapezoid
        if kind == "trapezoid":
            h = random.randint(min_c, max_c)
            top    = random.randint(min_c, max_c)
            bottom = random.randint(min_c, max_c)
            max_w  = max(top, bottom)
            cells  = []
            # for each row, interpolate width and center it
            for dr in range(h):
                if h > 1:
                    w_i = round(top + (bottom - top) * dr / (h - 1))
                else:
                    w_i = top
                offset = (max_w - w_i) // 2
                for dc in range(w_i):
                    cells.append((dr, offset + dc))
            return (cells, h, max_w)

        return None


    def _fill_grid(self):
        """
        Populate self.grid (a Grid of ObstacleCell by default) by:
        1) stamping each building footprint as BuildingCell
        2) carving a 1‑cell buffer around those footprints as WalkwayCell
        """
        # 1) Stamp building footprints
        for b in self.buildings:
            r0, c0 = b["r0"], b["c0"]
            for dr, dc in b["cells"]:
                if b is self.restaurant_bldg:
                    self.grid.set_cell(r0 + dr, c0 + dc, RestaurantCell(r0 + dr, c0 + dc))
                else:
                    self.grid.set_cell(r0 + dr, c0 + dc, BuildingCell(r0 + dr, c0 + dc))

        # 2) Carve sidewalks: any obstacle cell adjacent to a building becomes a walkway
        for r in range(self.rows):
            for c in range(self.cols):
                # skip if already a building
                if isinstance(self.grid.get_cell(r, c), (BuildingCell, RestaurantCell)):
                    continue

                # check 8 neighbors for a building
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if isinstance(self.grid.get_cell(nr, nc), (BuildingCell, RestaurantCell)):
                                # carve walkway here
                                self.grid.set_cell(r, c, WalkwayCell(r, c))
                                break
                    else:
                        continue
                    break

        self._connect_sidewalks()


    def _connect_sidewalks(self):
        # gather all walkway coordinates
        walk_cells = {(r,c)
                      for r in range(self.rows)
                      for c in range(self.cols)
                      if self.grid.get_cell(r,c).type == "walkway"}
        if not walk_cells:
            return

        # helper for 4‑neigh
        def neighbors(cell):
            r, c = cell
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield (nr, nc)

        # flood‑fill into connected components
        comps, seen = [], set()
        for cell in walk_cells:
            if cell in seen:
                continue
            comp = set([cell])
            queue = [cell]
            seen.add(cell)
            while queue:
                cur = queue.pop()
                for nb in neighbors(cur):
                    if nb in walk_cells and nb not in seen:
                        seen.add(nb)
                        comp.add(nb)
                        queue.append(nb)
            comps.append(comp)

        # pick “main” comp = the one containing the walkway nearest the grid center
        cx, cy = self.rows//2, self.cols//2
        nearest = min(walk_cells, key=lambda p: abs(p[0]-cx)+abs(p[1]-cy))
        main_comp = next(comp for comp in comps if nearest in comp)

        # connect every other comp back to main_comp
        for comp in comps:
            if comp is main_comp:
                continue
            # pick random endpoints
            r1, c1 = random.choice(tuple(comp))
            r0, c0 = random.choice(tuple(main_comp))

            # carve an L‑shaped connector (horiz then vert)
            # horizontal slice at row=r1
            for cc in range(min(c1,c0), max(c1,c0)+1):
                if not isinstance(self.grid.get_cell(r1,cc), (BuildingCell, RestaurantCell)):
                    self.grid.set_cell(r1, cc, WalkwayCell(r1, cc))
            # vertical slice at col=c0
            for rr in range(min(r1,r0), max(r1,r0)+1):
                if not isinstance(self.grid.get_cell(rr,c0), (BuildingCell, RestaurantCell)):
                    self.grid.set_cell(rr, c0, WalkwayCell(rr, c0))

            # merge them so further comps attach to unified main_comp
            main_comp |= comp

    def _assign_entry_points(self):
        """
        After sidewalks are finished, choose one walkway cell touching each
        building as the external entry.  Also mark the adjacent *internal*
        building cell so it shows up in a different color.
        """
        dirs4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
        cs = self.cell_size  # pixel size for drawing

        for b in self.buildings:
            r0, c0, h, w = b["r0"], b["c0"], b["h"], b["w"]
            kind = b.get("kind", "")

            # ---------- ❶ collect candidate walkway cells ----------
            candidates = []
            for dr, dc in b["cells"]:
                r, c = r0 + dr, c0 + dc
                for ddr, ddc in dirs4:
                    nr, nc = r + ddr, c + ddc
                    if (0 <= nr < self.rows) and (0 <= nc < self.cols):
                        if isinstance(self.grid.get_cell(nr, nc), WalkwayCell):
                            candidates.append((nr, nc))

            if kind == "hollow_square":
                candidates = [p for p in candidates
                              if not (r0 <= p[0] < r0 + h and
                                      c0 <= p[1] < c0 + w)]
                # ‑‑ explanation ‑‑
                # inner‑ring walkway sits strictly *inside* [r0,r0+h)×[c0,c0+w)
                # so removing those points leaves only the outside ring

            # ---------- ❷ pick / carve a door if none exist ----------
            if candidates:
                entry_out = random.choice(candidates)
            else:  # rare: carve one
                # pick random perimeter building cell and convert the
                # neighbour into a walkway.
                br, bc = r0 + random.choice(b["cells"])
                for ddr, ddc in dirs4:
                    nr, nc = br + ddr, bc + ddc
                    if (0 <= nr < self.rows) and (0 <= nc < self.cols):
                        if self.grid.get_cell(nr, nc).type == "ground":
                            self.grid.set_cell(nr, nc, WalkwayCell(nr, nc))
                            entry_out = (nr, nc)
                            break
                else:
                    entry_out = None  # should never happen

            # ---------- ❸ locate the *inside* cell ----------
            entry_in = None
            if entry_out:
                wr, wc = entry_out
                for ddr, ddc in dirs4:
                    nr, nc = wr + ddr, wc + ddc
                    if (0 <= nr < self.rows) and (0 <= nc < self.cols):
                        if isinstance(self.grid.get_cell(nr, nc),
                                      (BuildingCell, RestaurantCell)):
                            entry_in = (nr, nc)
                            break

            # ---------- ❹ save & draw ----------
            b["entry"] = entry_out  # external door tile
            b["entry_inside"] = entry_in  # internal door tile

            # draw outside (purple)
            if entry_out:
                x, y = entry_out[1] * cs, entry_out[0] * cs
                self.canvas.create_rectangle(
                    x, y, x + cs, y + cs,
                    fill="#A020F0", outline="", width=0
                )
            # draw inside (purple)
            if entry_in:
                x, y = entry_in[1] * cs, entry_in[0] * cs
                self.canvas.create_rectangle(
                    x, y, x + cs, y + cs,
                    fill="#A020F0", outline="", width=0
                )

    def _draw_map(self):
        """
        First paint every cell; then overlay one text label per building so
        the rectangles underneath can’t cover it.
        """
        cs = self.cell_size
        colors = {
            "ground": "#DFFFD0",
            "building": "#D2B48C",
            "restaurant": "#FFB347",
            "walkway": "#808080",
            "obstacle": "#B22222",
        }

        # ---------- PASS 1: rectangles ----------
        for r in range(self.rows):
            y1 = r * cs
            y2 = y1 + cs
            for c in range(self.cols):
                x1 = c * cs
                x2 = x1 + cs
                fill = colors[self.grid.get_cell(r, c).type]
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=fill, outline="", width=0)

        # ---------- PASS 2: labels ----------
        self._label_buildings()  # ← new helper, see below

    def _label_buildings(self):
        """
        Write either the numeric ID or a custom name at the pixel centre of
        each building so it never gets obscured.
        """
        cs = self.cell_size
        for b in self.buildings:
            # pixel centre of bounding box
            cx = (b["c0"] + b["w"] / 2) * cs
            cy = (b["r0"] + b["h"] / 2) * cs

            # use custom name if present (restaurant), else the numeric id
            label = b.get("name", str(b["id"]))

            # pick a font size that remains legible but fits small buildings
            #   ~ one character ≈ 6‑7 px wide; shrink for tiny buildings
            max_char_w = b["w"] * cs / max(len(label), 1)
            font_size = max(6, int(max_char_w * 0.75))

            self.canvas.create_text(
                cx, cy,
                text=label,
                fill="black",
                font=("Arial", font_size),
                anchor="center"
            )


    def highlight_cell(self, r:int, c:int, color:str="yellow"):
        x1 = c*self.cell_size + 1
        y1 = r*self.cell_size + 1
        x2 = x1 + self.cell_size - 2
        y2 = y1 + self.cell_size - 2
        items = self.canvas.find_enclosed(x1, y1, x2, y2)
        if items:
            self.canvas.itemconfig(items[0], fill=color)

    def generate_random_order(self):
        """
        Pick one of this campus’s buildings at random
        and generate a single random food order for it.
        Returns a tuple: (building_dict, Order instance).
        """
        # 1) pick a building footprint
        b = random.choice(self.buildings)
        # 2) generate one random order
        order = OrderGenerator(num_orders=1).generate_orders()[0]
        return b, order

