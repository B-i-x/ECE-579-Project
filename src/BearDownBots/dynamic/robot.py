import random
import heapq
import itertools
from itertools import cycle

from BearDownBots.static.map import Map
from BearDownBots.static.cell import CELL_TYPES, Position, Cell
from BearDownBots.dynamic.randOrders import Order

class Direction:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

ROBOT_COLOURS = cycle([
    "#e6194b",  # red
    "#3cb44b",  # green
    "#4363d8",  # blue
])

class Robot:
    MAX_CARRY = 3
    def __init__(self, robot_id: int, map: Map):
        self.id = robot_id
        self.map: Map = map

        self.position = Position(0, 0)
        self.previous_position = Position(0, 0)
        self.restaurant_pickup_point : Position = None 
        self.dropoff_point : Position = None
        self.next_direction_to_move = None  # Direction to move next
        self.colour = next(ROBOT_COLOURS)

        self.path = []  # List of cells to traverse

        self._pending_orders : list[Order] = []    # <-- internal queue
        self.current_batch: list[Order] = []



        self.state = "idle"   # one of: "delivering", "returning", "idle"

        self.place_self_on_restaurant()

        self.pathfinding_method = "a_star"  # Options: "a_star", "greedy", "dfs"

    @property
    def orders(self) -> list[Order]:
        return self.current_batch if self.current_batch else self._pending_orders

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

    def _select_orders_batch(self, batch_size: int = 3) -> list[Order]:
        """
        Always pick the oldest order, then up to (batch_size-1) more
        by nearest-neighbor on dropoff_point.
        """
        if not self._pending_orders:
            return []

        # 1) oldest first
        batch = [self._pending_orders[0]]
        remaining = self._pending_orders[1:]

        # 2) greedy nearest-neighbor on dropoff_point
        def manhattan(o: Order, ref_xy: tuple[int,int]):
            x0,y0 = ref_xy
            x1,y1 = o.building.dropoff_point
            return abs(x0-x1) + abs(y0-y1)

        # pick second closest to first
        if remaining and len(batch) < batch_size:
            ref1 = batch[0].building.dropoff_point
            second = min(remaining, key=lambda o: manhattan(o, ref1))
            batch.append(second)
            remaining = [o for o in remaining if o is not second]

        # pick third closest to **second**
        if remaining and len(batch) < batch_size:
            ref2 = batch[1].building.dropoff_point
            third = min(remaining, key=lambda o: manhattan(o, ref2))
            batch.append(third)

        return batch


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

                self.path = path_pos[1:]   # drop the start—these are the next steps

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
                # 1) never walk into obstacles
                if cell.has_type(CELL_TYPES.OBSTACLE):
                    continue
                # 2) only walk on sidewalks
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


    def greedy_best_first_search(self, raw_start, raw_goal) -> list[Position]:
        if raw_start is None or raw_goal is None:
            return []

        start = Position(*raw_start) if isinstance(raw_start, tuple) else raw_start
        goal  = Position(*raw_goal)  if isinstance(raw_goal, tuple) else raw_goal

        def h(p: Position, q: Position) -> int:
            return abs(p.x - q.x) + abs(p.y - q.y)

        counter = itertools.count()
        open_heap = [(h(start, goal), next(counter), start)]
        came_from = {}
        visited = set()

        while open_heap:
            _, _, current = heapq.heappop(open_heap)

            if current == goal:
                path_pos = []
                while current != start:
                    path_pos.append(current)
                    current = came_from[current]
                path_pos.append(start)
                path_pos.reverse()
                return path_pos

            visited.add(current)

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nbr = Position(current.x + dx, current.y + dy)

                if (0 <= nbr.x < self.map.rows and 0 <= nbr.y < self.map.cols and
                    nbr not in visited and
                    self.map.get_cell(nbr.x, nbr.y).has_type(CELL_TYPES.WALKWAY)):
                    if nbr not in came_from:
                        came_from[nbr] = current
                        heapq.heappush(open_heap, (h(nbr, goal), next(counter), nbr))

        return []


    def depth_first_search(self, raw_start, raw_goal) -> list[Position]:
        if raw_start is None or raw_goal is None:
            return []

        start = Position(*raw_start) if isinstance(raw_start, tuple) else raw_start
        goal  = Position(*raw_goal)  if isinstance(raw_goal, tuple) else raw_goal

        stack = [(start, [start])]
        visited = set()

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            visited.add(current)

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nbr = Position(current.x + dx, current.y + dy)

                if (0 <= nbr.x < self.map.rows and 0 <= nbr.y < self.map.cols and
                    nbr not in visited and
                    self.map.get_cell(nbr.x, nbr.y).has_type(CELL_TYPES.WALKWAY)):
                    stack.append((nbr, path + [nbr]))

        return []


    def plan_path(self, start, goal) -> list[Position]:
        if self.pathfinding_method == "a_star":
            path_cells = self.a_star(start, goal)
            return [cell.position for cell in path_cells] if path_cells else []
        elif self.pathfinding_method == "greedy":
            return self.greedy_best_first_search(start, goal)
        elif self.pathfinding_method == "dfs":
            return self.depth_first_search(start, goal)
        else:
            print(f"Unknown pathfinding method '{self.pathfinding_method}', defaulting to A*.")
            path_cells = self.a_star(start, goal)
            return [cell.position for cell in path_cells] if path_cells else []


        
    def move(self):
        """
        Step *along* the precomputed self.path.
        Each call pops the next Position and walks there,
        removing that cell from the front of the path.
        """
        # nothing queued?
        if not self.path:
            return

        # 1) figure out where to go next
        next_pos = self.path.pop(0)  # Position(x,y)
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
        if len(self._pending_orders) >= self.MAX_CARRY:
            return False

        self._pending_orders.append(order)

        if self.state == "idle":
            self._start_next_delivery()

        return True

    #def _start_next_delivery(self):
        # pop the next order off the queue (but keep it for removal on arrival)
        #next_order = self.orders[0]
        #raw_dropoff = next_order.building.dropoff_point

        #self.dropoff_point = Position(*raw_dropoff) if isinstance(raw_dropoff, tuple) else raw_dropoff
        
        #self.state = "delivering"
        #self.a_star(self.position, self.dropoff_point)       # plan path to dropoff_point

    def _start_next_delivery(self):
        # select up to three
        self.current_batch = self._select_orders_batch()

        # remove them from the main queue so act() won’t see them twice
        for o in self.current_batch:
            self._pending_orders.remove(o)

        # now begin with the first in the batch
        first = self.current_batch[0]
        drop = first.building.dropoff_point
        self.dropoff_point = Position(*drop) if isinstance(drop, tuple) else drop

        self.state = "delivering"
        self.a_star_path = self.plan_path(self.restaurant_pickup_point, self.dropoff_point)



    #def act(self):
        """
        Perform the robot's action.
        """

        #self.move()

        # 2) did we just arrive?
        #if self.position == self.dropoff_point:
            #if self.state == "delivering":
                #print(f"Robot {self.id} arrived at dropoff point {self.dropoff_point}.")
                # remove the completed order
                #completed = self.orders.pop(0)

                # if there’s another order waiting, go straight to it
                #if self.orders:
                    #self._start_next_delivery()
                #else:
                    # no more orders → return home
                    #self.state = "returning"
                    #self.path = self.plan_path(self.dropoff_point, self.restaurant_pickup_point)

                    #self.dropoff_point = self.restaurant_pickup_point


            #elif self.state == "returning":
                # we’re home!
                #self.state = "idle"
                #print(f"Robot {self.id} returned to restaurant pickup point {self.restaurant_pickup_point}.")
                # (you could also clear path, etc.)

    def act(self):
        self.move()

        # did we just arrive?
        if self.position == self.dropoff_point:
            if self.state == "delivering":
                print(f"Robot {self.id} arrived at {self.dropoff_point}.")

                # mark this one done
                done = self.current_batch.pop(0)

                if self.current_batch:
                    # more in this batch → go to next
                    next_drop = self.current_batch[0].building.dropoff_point
                    self.dropoff_point = Position(*next_drop)
                    self.a_star_path = self.plan_path(self.position, self.dropoff_point)
                else:
                    # batch finished → return home
                    self.state = "returning"
                    self.a_star_path = self.plan_path(self.position, self.restaurant_pickup_point)
                    self.dropoff_point = self.restaurant_pickup_point

            elif self.state == "returning":
                self.state = "idle"
                print(f"Robot {self.id} returned home.")
                # if more orders queued, start a new batch:
                if self._pending_orders:
                    self._start_next_delivery()

    

    def __str__(self):
        return f"Robot {self.id} at {self.position} (method: {self.pathfinding_method})"
