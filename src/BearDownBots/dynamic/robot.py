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
        """
        Place the robot on a restaurant cell.
        """
        # Placeholder for placing the robot on a restaurant cell
        for cell in self.map.one_dimensional_grid:
            if cell.has_type(CELL_TYPES.RESTUARANT_PICKUP):
                self.position = cell.position
                self.map.get_cell(self.position.x, self.position.y).add_type(CELL_TYPES.ROBOT)
                print(f"Placed robot {self.id} at {self.position}")
                break
            

    def a_star(self, start_cell : Cell, goal_cell : Cell) -> list[Cell]:
        """
        A* algorithm to find the shortest path from start to goal.
        """
        # Placeholder for A* algorithm implementation

        ## for now just choose a random direction to move in
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        self.next_direction_to_move = random.choice(directions)
        pass

    def move(self):
        """
        Move the robot in the next direction.
        This method updates the robot's position and the map accordingly.
        """


        if not self.position or not self.next_direction_to_move:
            return  # No movement if position or direction is undefined

        # Update the previous position
        self.previous_position = Position(self.position.x, self.position.y)

        # Move in the next direction
        if self.next_direction_to_move == "up":
            self.position.x -= 1
        elif self.next_direction_to_move == "down":
            self.position.x += 1
        elif self.next_direction_to_move == "left":
            self.position.y -= 1
        elif self.next_direction_to_move == "right":
            self.position.y += 1

        print(f"Moving robot {self.id} from {self.previous_position} to {self.position} in direction {self.next_direction_to_move}")    

        # Update the map with the robot's new position
        self.map.get_cell(self.position.x, self.position.y).add_type(CELL_TYPES.ROBOT)
        self.map.get_cell(self.previous_position.x, self.previous_position.y).remove_type(CELL_TYPES.ROBOT)

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
