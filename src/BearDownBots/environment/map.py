from BearDownBots.environment.cell_types import CELL_TYPES
from BearDownBots.environment.cell import Cell

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