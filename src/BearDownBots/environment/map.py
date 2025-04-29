from BearDownBots.environment.cell import Cell, CELL_TYPES
from BearDownBots.environment.buildings import Building

import random

class Map:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.create_empty_map()
        # keep track of obstacle specifics
        self.obstacles = {}  # {(x, y): obstacle_type}

        self.buildings = []  # list of buildings placed on the map
        self.walkways = []  # list of walkways placed on the map

    def create_empty_map(self):
        """
        Initialize a rows x cols grid of Cells, all set to GROUND.
        """
        self.grid = [
            [Cell(x, y, CELL_TYPES.GROUND) for y in range(self.cols)]
            for x in range(self.rows)
        ]
        return self.grid

    def get_cell(self, x: int, y: int) -> Cell:
        """
        Return the Cell at (x, y), or raise IndexError if out of bounds.
        """
        if 0 <= x < self.rows and 0 <= y < self.cols:
            return self.grid[x][y]
        raise IndexError(f"Cell coordinates out of bounds: ({x}, {y})")

    def add_cell_type(self, x: int, y: int, cell_type: CELL_TYPES):
        """
        Add a type to the Cell at (x, y).
        """
        cell = self.get_cell(x, y)
        cell.add_type(cell_type)

    def remove_cell_type(self, x: int, y: int, cell_type: CELL_TYPES):
        """
        Remove a type from the Cell at (x, y).
        """
        cell = self.get_cell(x, y)
        cell.remove_type(cell_type)

    def attempt_to_place_building(self, top_left: tuple[int, int], building: Building) -> bool:
        """
        Attempt to place the given building onto the map at the given top_left coordinate.
        Checks conflicts within the building's bounding box (outline),
        and places cells according to the building's defined cells if successful.
        Adds sidewalks (WALKWAY) around the building.
        """
        x0, y0 = top_left
        height, width = building.h, building.w

        # Bounds check for the outline (bounding box)
        if x0 < 0 or y0 < 0 or x0 + height > self.rows or y0 + width > self.cols:
            return False

        # Conflict check within the bounding box
        for dx in range(height):
            for dy in range(width):
                x, y = x0 + dx, y0 + dy
                cell = self.get_cell(x, y)
                if cell.has_type(CELL_TYPES.BUILDING) or cell.has_type(CELL_TYPES.WALKWAY):
                    return False


        # Actually place the building shape using its specific cells
        for dr, dc in building.cells:
            x, y = x0 + dr, y0 + dc
            if 0 <= x < self.rows and 0 <= y < self.cols:
                self.remove_cell_type(x, y, CELL_TYPES.GROUND)
                self.add_cell_type(x, y, CELL_TYPES.BUILDING)

        # Place sidewalks around the building's actual cells
        for dr, dc in building.cells:
            for adj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # up, down, left, right
                adj_r, adj_c = dr + adj[0], dc + adj[1]
                x, y = x0 + adj_r, y0 + adj_c
                if 0 <= x < self.rows and 0 <= y < self.cols:
                    cell = self.get_cell(x, y)
                    if cell.has_type(CELL_TYPES.GROUND):
                        self.remove_cell_type(x, y, CELL_TYPES.GROUND)
                        self.add_cell_type(x, y, CELL_TYPES.WALKWAY)

        building.top_left_x = x0
        building.top_left_y = y0
        # Store the building for later reference
        self.buildings.append(building)

        return True

    def connect_sidewalks(self):
        """
        Ensures all WALKWAY cells form a single connected network by linking
        disjoint walkway groups with L-shaped connectors.
        """
        # collect all walkway positions
        walk_cells = {
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.get_cell(r, c).has_type(CELL_TYPES.WALKWAY)
        }
        if not walk_cells:
            return

        # neighbors for 4-connectivity
        def neighbors(pos):
            r, c = pos
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield (nr, nc)

        # flood-fill to find connected components
        comps = []
        seen = set()
        for start in walk_cells:
            if start in seen:
                continue
            comp = {start}
            stack = [start]
            seen.add(start)
            while stack:
                cell = stack.pop()
                for nb in neighbors(cell):
                    if nb in walk_cells and nb not in seen:
                        seen.add(nb)
                        comp.add(nb)
                        stack.append(nb)
            comps.append(comp)

        # pick the component closest to the map center as the main one
        cx, cy = self.rows // 2, self.cols // 2
        nearest = min(walk_cells, key=lambda p: abs(p[0]-cx) + abs(p[1]-cy))
        main = next(comp for comp in comps if nearest in comp)

        # connect other components back to main via random L-shaped paths
        for comp in comps:
            if comp is main:
                continue
            # choose random endpoints
            r1, c1 = random.choice(tuple(comp))
            r0, c0 = random.choice(tuple(main))

            # horizontal segment at row=r1
            for cc in range(min(c1, c0), max(c1, c0) + 1):
                cell = self.get_cell(r1, cc)
                if cell.has_type(CELL_TYPES.GROUND):
                    self.remove_cell_type(r1, cc, CELL_TYPES.GROUND)
                    self.add_cell_type(r1, cc, CELL_TYPES.WALKWAY)
            # vertical segment at col=c0
            for rr in range(min(r1, r0), max(r1, r0) + 1):
                cell = self.get_cell(rr, c0)
                if cell.has_type(CELL_TYPES.GROUND):
                    self.remove_cell_type(rr, c0, CELL_TYPES.GROUND)
                    self.add_cell_type(rr, c0, CELL_TYPES.WALKWAY)

            # merge component into main
            main |= comp

    def create_food_warehouse(self):
        """
        Choose a random building and convert that to a food warehouse.
        """
        if not self.buildings:
            return
        building = random.choice(self.buildings)
        # remove the building type from the cell
        for dr, dc in building.cells:
            x, y = building.top_left_x + dr, building.top_left_y + dc
            cell = self.get_cell(x, y)
            cell.remove_type(CELL_TYPES.BUILDING)
            cell.add_type(CELL_TYPES.RESTAURANT)

    
    
    def __repr__(self):
        # build 2D list of initials
        rows_letters = []
        max_len = 0

        for row in self.grid:
            row_repr = []
            for cell in row:
                # pull initials from the enum
                initials = ''.join(sorted(t.initial for t in cell.types))
                row_repr.append(initials)
                max_len = max(max_len, len(initials))
            rows_letters.append(row_repr)

        # pad and join
        lines = []
        for row_repr in rows_letters:
            padded = [s.ljust(max_len) for s in row_repr]
            lines.append(' '.join(padded))

        return '\n'.join(lines)
