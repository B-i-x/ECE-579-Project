from enum import Enum

class InitialEnum(Enum):
    @property
    def initial(self) -> str:
        # take the first character of the name
        return self.name[0]
    
class CELL_TYPES(InitialEnum):
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
