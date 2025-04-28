# src/BearDownBots/environment/cell.py
from BearDownBots.environment.cell_types import CELL_TYPES

class Cell:
    def __init__(self, x: int, y: int, cell_type: CELL_TYPES):
        self.x = x
        self.y = y
        # store a set of types (allows multiple types per cell)
        self.types = {cell_type}

    def add_type(self, cell_type: CELL_TYPES):
        """
        Add a type to this cell.
        """
        self.types.add(cell_type)

    def remove_type(self, cell_type: CELL_TYPES):
        """
        Remove a type from this cell, if present.
        """
        self.types.discard(cell_type)

    def has_type(self, cell_type: CELL_TYPES) -> bool:
        """
        Check if this cell has the given type.
        """
        return cell_type in self.types

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, types={self.types})"
