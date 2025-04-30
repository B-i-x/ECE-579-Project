from BearDownBots.static.map import Map
from BearDownBots.static.cell import CELL_TYPES


class Robot:
    def __init__(self, robot_id: int, map: Map):
        self.id = robot_id
        self.map: Map = map

        self.position = None
        self.previous_position = None
        self.next_direction_to_move = None

        self.place_self_on_restaurant()

    def place_self_on_restaurant(self):
        """
        Place the robot on a restaurant cell.
        """
        # Placeholder for placing the robot on a restaurant cell
        pass

    def a_star(self, start_cell, goal_cell):
        """
        A* algorithm to find the shortest path from start to goal.
        """
        # Placeholder for A* algorithm implementation
        pass

    def step(self, dt: float):
        """
        Called every tick with dt = scaled seconds.
        Use dt to drive movement, cooldowns, animations, etc.
        """
        if self.position is None or self.next_direction_to_move is None:
            return  # No movement if position or direction is undefined

        # Calculate the distance to move
        distance = 1.0 * dt  # Assuming 1 cell per second

        # Update the previous position
        self.previous_position = self.position

        # Move in the next direction
        if self.next_direction_to_move == "up":
            self.position = (self.position[0] - distance, self.position[1])
        elif self.next_direction_to_move == "down":
            self.position = (self.position[0] + distance, self.position[1])
        elif self.next_direction_to_move == "left":
            self.position = (self.position[0], self.position[1] - distance)
        elif self.next_direction_to_move == "right":
            self.position = (self.position[0], self.position[1] + distance)

        self.map.get_cell(self.position[0], self.position[1]).add_type(CELL_TYPES.ROBOT)
        self.map.get_cell(self.previous_position[0], self.previous_position[1]).remove_type(CELL_TYPES.ROBOT)

    def add_food(self, food):
        """
        Add food to the robot's inventory.
        """
        # Placeholder for adding food to the robot's inventory
        pass

    def __str__(self):
        return f"Robot {self.id} at {self.map.get_cell(self.id).location}"