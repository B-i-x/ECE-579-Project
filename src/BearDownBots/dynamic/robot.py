import random

from BearDownBots.static.map import Map
from BearDownBots.static.cell import CELL_TYPES, Position, Cell

class Direction:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Robot:
    def __init__(self, robot_id: int, map: Map):
        self.id = robot_id
        self.map: Map = map

        self.position = Position(0, 0)
        self.previous_position = Position(0, 0)
        self.next_direction_to_move = None  # Direction to move next

        self.a_star_path = []  # List of cells to traverse

        self.orders = []  # List of orders assigned to the robot

        self.place_self_on_restaurant()

    def place_self_on_restaurant(self):
        for cell in self.map.one_dimensional_grid:
            if cell.has_type(CELL_TYPES.RESTUARANT_PICKUP):
                # copy the cell’s coords instead of sharing the same object
                px, py = cell.position.x, cell.position.y
                self.position = Position(px, py)
                self.previous_position = Position(px, py)

                cell.add_type(CELL_TYPES.ROBOT)
                print(f"Placed robot {self.id} at {self.position}")
                return
            

    def a_star(self, start_cell: Cell, goal_cell: Cell) -> list[Cell]:
        """
        A* placeholder: picks one of the four cardinal neighbors **only**
        if that neighbor cell has type WALKWAY.
        Sets self.next_direction_to_move accordingly.
        """
        x, y = self.position.x, self.position.y
        candidates = []

        # check each direction
        for direction, dx, dy in [
            (Direction.UP,    -1,  0),
            (Direction.DOWN,   1,  0),
            (Direction.LEFT,   0, -1),
            (Direction.RIGHT,  0,  1),
        ]:
            nx, ny = x + dx, y + dy
            # in‐bounds?
            if 0 <= nx < self.map.rows and 0 <= ny < self.map.cols:
                cell = self.map.get_cell(nx, ny)
                # only allow moving onto WALKWAY
                if cell.has_type(CELL_TYPES.WALKWAY):
                    candidates.append(direction)

        if candidates:
            self.next_direction_to_move = random.choice(candidates)
        else:
            # no valid moves—stay put (or you could fallback to GROUND, etc.)
            self.next_direction_to_move = None

        # we’re not building a full path yet, so just return empty
        return []

        
    def move(self):
        """
        Move the robot in its next_direction_to_move,
        without ever mutating Position in place.
        """
        if self.next_direction_to_move is None:
            return

        # 1) stash the old position
        old_pos = self.position

        # 2) compute a brand-new Position
        if   self.next_direction_to_move == Direction.UP:
            new_pos = Position(old_pos.x - 1, old_pos.y)
        elif self.next_direction_to_move == Direction.DOWN:
            new_pos = Position(old_pos.x + 1, old_pos.y)
        elif self.next_direction_to_move == Direction.LEFT:
            new_pos = Position(old_pos.x, old_pos.y - 1)
        elif self.next_direction_to_move == Direction.RIGHT:
            new_pos = Position(old_pos.x, old_pos.y + 1)
        else:
            return

        # 3) update your record
        self.previous_position = old_pos
        self.position = new_pos

        print(f"Moving robot {self.id} from {old_pos} to {new_pos} in direction {self.next_direction_to_move}")

        # 4) update the map‐cell types
        self.map.get_cell(old_pos.x, old_pos.y).remove_type(CELL_TYPES.ROBOT)
        self.map.get_cell(new_pos.x, new_pos.y).add_type   (CELL_TYPES.ROBOT)

    def add_order(self, order):
        """
        Add an order to the robot's task list.
        """
        # Placeholder for adding an order to the robot's task list
        self.orders.append(order)

    def act(self):
        """
        Perform the robot's action.
        """
        self.a_star(1, 1)

        self.move()

    def __str__(self):
        return f"Robot {self.id} at {self.position}"
