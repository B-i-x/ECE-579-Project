# src/BearDownBots/environment/cell.py

class Cell:
    """Base class for a grid cell."""
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    @property
    def type(self) -> str:
        return "empty"


class BuildingCell(Cell):
    @property
    def type(self) -> str:
        return "building"


class WalkwayCell(Cell):
    @property
    def type(self) -> str:
        return "walkway"


class ObstacleCell(Cell):
    @property
    def type(self) -> str:
        return "obstacle"
