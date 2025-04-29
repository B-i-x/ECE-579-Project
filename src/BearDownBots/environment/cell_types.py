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
