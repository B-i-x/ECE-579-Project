# src/BearDownBots/environment/cell.py
from enum import Enum

class CustomCellTypeEnum(Enum):
    def __new__(cls, value, color: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._color  = color           # attach a .color attribute
        return obj

    @property
    def initial(self) -> str:
        return self.name[0]
    
    @property
    def color(self) -> str:
        return self._color

    
class CELL_TYPES(CustomCellTypeEnum):
    GROUND     = (0, "#00ff00")   # green
    BUILDING   = (1, "#d2b48c")   # tan
    WALKWAY    = (2, "#cccccc")   # gray
    OBSTACLE   = (3, "#ff0000")
    ROBOT      = (4, "#0000ff")
    RESTAURANT = (5, "#00aa00")
    CUSTOMER   = (6, "#ffaa00")

class OBSTACLE_TYPES(Enum):
    PERSON = 0
    LIGHT_POST = 1

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
