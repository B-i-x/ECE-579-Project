import random
import heapq
import itertools

from BearDownBots.static.map import Map
from BearDownBots.static.cell import CELL_TYPES, Position, Cell
from BearDownBots.dynamic.randOrders import Order

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
        self.restaurant_pickup_point : Position = None 
        self.dropoff_point : Position = None
        self.next_direction_to_move = None  # Direction to move next

        self.a_star_path = []  # List of cells to traverse

        self.orders : list[Order] = []  # List of orders assigned to the robot

        self.place_self_on_restaurant()

    def place_self_on_restaurant(self):
        for cell in self.map.one_dimensional_grid:
            if cell.has_type(CELL_TYPES.RESTUARANT_PICKUP):
                # copy the cell’s coords instead of sharing the same object
                px, py = cell.position.x, cell.position.y
                self.position = Position(px, py)
                self.previous_position = Position(px, py)
                self.restaurant_pickup_point = Position(px, py)
                cell.add_type(CELL_TYPES.ROBOT)
                # print(f"Placed robot {self.id} at {self.position}")
                return
            
    def a_star(self) -> list[Cell]:
        """
        Find a path along WALKWAY cells from restaurant_pickup_point to dropoff_point.
        Sets self.next_direction_to_move to the first step’s direction.
        """
        raw_start = self.restaurant_pickup_point
        raw_goal  = self.dropoff_point

        if raw_start is None or raw_goal is None:
            return []

        # Ensure we have Position instances
        start = Position(*raw_start) if isinstance(raw_start, tuple) else raw_start
        goal  = Position(*raw_goal)  if isinstance(raw_goal, tuple)  else raw_goal

        if start == goal:
            self.next_direction_to_move = None
            return []

        def h(p: Position, q: Position) -> int:
            return abs(p.x - q.x) + abs(p.y - q.y)

        # A counter for tie-breaking
        counter = itertools.count()

        open_heap = []
        # push (f_score, tie_breaker, Position)
        heapq.heappush(open_heap, (h(start, goal), next(counter), start))

        came_from: dict[Position, Position] = {}
        g_score: dict[Position, int] = {start: 0}
        closed: set[Position] = set()

        while open_heap:
            _, _, current = heapq.heappop(open_heap)

            if current in closed:
                continue

            if current == goal:
                # reconstruct path
                path_pos = []
                p = current
                while p != start:
                    path_pos.append(p)
                    p = came_from[p]
                path_pos.append(start)
                path_pos.reverse()

                path_cells = [self.map.get_cell(p.x, p.y) for p in path_pos]

                # set next_direction_to_move
                dx = path_pos[1].x - start.x
                dy = path_pos[1].y - start.y
                if dx == -1:
                    self.next_direction_to_move = Direction.UP
                elif dx == 1:
                    self.next_direction_to_move = Direction.DOWN
                elif dy == -1:
                    self.next_direction_to_move = Direction.LEFT
                elif dy == 1:
                    self.next_direction_to_move = Direction.RIGHT
                else:
                    self.next_direction_to_move = None

                return path_cells

            closed.add(current)

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nbr = Position(current.x + dx, current.y + dy)

                if not (0 <= nbr.x < self.map.rows and 0 <= nbr.y < self.map.cols):
                    continue
                if nbr in closed:
                    continue

                cell = self.map.get_cell(nbr.x, nbr.y)
                if not cell.has_type(CELL_TYPES.WALKWAY):
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(nbr, float('inf')):
                    came_from[nbr]    = current
                    g_score[nbr]      = tentative_g
                    f_score           = tentative_g + h(nbr, goal)
                    heapq.heappush(open_heap, (f_score, next(counter), nbr))

        # no path found
        self.next_direction_to_move = None
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

        # print(f"Moving robot {self.id} from {old_pos} to {new_pos} in direction {self.next_direction_to_move}")

        # 4) update the map‐cell types
        self.map.get_cell(old_pos.x, old_pos.y).remove_type(CELL_TYPES.ROBOT)
        self.map.get_cell(new_pos.x, new_pos.y).add_type   (CELL_TYPES.ROBOT)

    def add_order(self, order):
        """
        Add an order to the robot's task list.
        """
        # Placeholder for adding an order to the robot's task list
        self.orders.append(order)
        
        self.dropoff_point = order.building.dropoff_point

    def act(self):
        """
        Perform the robot's action.
        """
        self.a_star()

        self.move()

    def __str__(self):
        return f"Robot {self.id} at {self.position}"
