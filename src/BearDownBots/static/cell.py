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
    ROBOT      = (4, "#00008B")   # dark blue
    RESTAURANT = (5, "#e6eb14")   # yellow
    RESTUARANT_PICKUP = (6, "#e06192")  # pink
    BUILDING_DROP_OFF = (7, "#ff8c00")  # dark orange
    GROUND     = (0, "#c1e8c2")   # dark green
    BUILDING   = (1, "#A0522D")   # sienna
    OBSTACLE   = (3, "#8B0000")   # dark red
    WALKWAY    = (2, "#555555")   # dark gray



class OBSTACLE_TYPES(Enum):
    PERSON = 0
    LIGHT_POST = 1

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))
    
class Cell:
    def __init__(self, x: int, y: int, cell_type: CELL_TYPES):
        self.position = Position(x, y)
        self.x = self.position.x
        self.y = self.position.y
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
