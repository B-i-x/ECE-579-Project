from enum import Enum

class CELL_TYPES(Enum):
    GROUND = 0
    BUILDING = 1
    WALKWAY = 2
    OBSTACLE = 3
    ROBOT = 4
    RESTAURANT = 5
    CUSTOMER = 6

class OBSTACLE_TYPES(Enum):
    PERSON = 0
    LIGHT_POST = 1
