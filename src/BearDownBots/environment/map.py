from BearDownBots.environment.cell import Cell, CELL_TYPES
from BearDownBots.environment.buildings import Building

class Map:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.create_empty_map()
        # keep track of obstacle specifics
        self.obstacles = {}  # {(x, y): obstacle_type}

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
