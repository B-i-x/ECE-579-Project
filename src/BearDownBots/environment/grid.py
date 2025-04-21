# src/BearDownBots/environment/grid.py

from BearDownBots.environment.cell import Cell, GroundCell, BuildingCell, WalkwayCell, ObstacleCell

class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # initialize every cell as a ground cell
        self.grid: list[list[Cell]] = [
            [GroundCell(r, c) for c in range(cols)]
            for r in range(rows)
        ]

    def set_cell(self, row: int, col: int, cell: Cell):
        """Place a Cell instance at (row, col)."""
        self.grid[row][col] = cell

    def get_cell(self, row: int, col: int) -> Cell:
        return self.grid[row][col]

    def __repr__(self):
        return f"Grid({self.rows}×{self.cols})"
