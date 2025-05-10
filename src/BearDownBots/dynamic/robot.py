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

        self.state = "idle"   # one of: "delivering", "returning", "idle"

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
            
    def a_star(self, raw_start, raw_goal) -> list[Cell]:
        """
        Find a path along WALKWAY cells from restaurant_pickup_point to dropoff_point.
        Sets self.next_direction_to_move to the first step’s direction.
        """
        # raw_start = self.restaurant_pickup_point
        # raw_goal  = self.dropoff_point

        if raw_start is None:
            print(f"Robot {self.id} has no start position.")
            return []
        
        if raw_goal is None:
            print(f"Robot {self.id} has no goal position.")
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

                self.a_star_path = path_pos[1:]   # drop the start—these are the next steps

                # print(f"Robot {self.id} found a path from {start} to {goal} with {len(path_cells)} cells.")
                # print(f"Robot {self.id} moving from {start} to {goal} in direction {self.next_direction_to_move}")
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

        # print(f"Robot {self.id} failed to find a path from {start} to {goal}.")
        # no path found
        self.next_direction_to_move = None
        return []

        
    def move(self):
        """
        Step *along* the precomputed self.a_star_path.
        Each call pops the next Position and walks there,
        removing that cell from the front of the path.
        """
        # nothing queued?
        if not self.a_star_path:
            return

        # 1) figure out where to go next
        next_pos = self.a_star_path.pop(0)  # Position(x,y)
        old_pos  = self.position

        # 2) compute the direction (optional, for your logic)
        dx = next_pos.x - old_pos.x
        dy = next_pos.y - old_pos.y
        if   dx == -1: self.next_direction_to_move = Direction.UP
        elif dx ==  1: self.next_direction_to_move = Direction.DOWN
        elif dy == -1: self.next_direction_to_move = Direction.LEFT
        elif dy ==  1: self.next_direction_to_move = Direction.RIGHT
        else:
            # somehow not adjacent?
            return

        # 3) actually step
        self.previous_position = old_pos
        self.position          = next_pos

    def add_order(self, order):
        """
        Add an order to the robot's task list.
        """
        # Placeholder for adding an order to the robot's task list
        self.orders.append(order)

        if self.state == "idle":
            self._start_next_delivery()

    def _start_next_delivery(self):
        # pop the next order off the queue (but keep it for removal on arrival)
        next_order = self.orders[0]
        raw_dropoff = next_order.building.dropoff_point

        self.dropoff_point = Position(*raw_dropoff) if isinstance(raw_dropoff, tuple) else raw_start
        
        self.state         = "delivering"
        self.a_star(self.restaurant_pickup_point, self.dropoff_point)       # plan path to dropoff_point


    def act(self):
        """
        Perform the robot's action.
        """

        self.move()

        # 2) did we just arrive?
        if self.position == self.dropoff_point:
            if self.state == "delivering":
                print(f"Robot {self.id} arrived at dropoff point {self.dropoff_point}.")
                # remove the completed order
                completed = self.orders.pop(0)

                # if there’s another order waiting, go straight to it
                if self.orders:
                    self._start_next_delivery()
                else:
                    # no more orders → return home
                    self.state = "returning"
                    self.a_star(self.dropoff_point, self.restaurant_pickup_point)  # plan path back to restaurant
                    self.dropoff_point = self.restaurant_pickup_point


            elif self.state == "returning":
                # we’re home!
                self.state = "idle"
                print(f"Robot {self.id} returned to restaurant pickup point {self.restaurant_pickup_point}.")
                # (you could also clear a_star_path, etc.)
    

    def __str__(self):
        return f"Robot {self.id} at {self.position}"
