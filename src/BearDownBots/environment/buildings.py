# src/BearDownBots/environment/buildings.py
import random
from BearDownBots.environment.cell_types import CELL_TYPES
from BearDownBots.environment.map import Map

def randomly_place_buildings_onto_map(campus_map: Map, max_attempts: int = 100) -> bool:
    """
    Attempt to place a building on the map at a random location.
    Returns True if successful, False if not.
    """
    pass
    

class Building:
    """Base class for all building types."""
    def __init__(self, cells: list[tuple[int,int]], height: int, width: int):
        self.cells  = cells   # list of (dr, dc) offsets from top-left
        self.h      = height
        self.w      = width
        self.name   = random.choice(BUILDING_NAMES)  # random name from list


    def __repr__(self):
        return f"{self.__class__.__name__}(h={self.h}, w={self.w}, cells={len(self.cells)})"

    def place(self, campus_map: Map, top_left: tuple[int,int]):
        """
        Place this building onto the given map at top_left (x, y).
        Removes GROUND and adds BUILDING type to each cell.
        """
        x0, y0 = top_left
        for dr, dc in self.cells:
            x, y = x0 + dr, y0 + dc
            # bounds check
            if 0 <= x < campus_map.rows and 0 <= y < campus_map.cols:
                campus_map.remove_cell_type(x, y, CELL_TYPES.GROUND)
                campus_map.add_cell_type(x, y, CELL_TYPES.BUILDING)
            else:
                raise IndexError(f"Building placement out of map bounds at ({x},{y})")

class RectangleBuilding(Building):
    """A general rectangle with random width and height."""
    def __init__(self, min_cells: int, max_cells: int):
        base = random.randint(min_cells, max_cells)
        w    = random.randint(max(1, int(base*0.5)), int(base*2))
        h    = random.randint(max(1, int(base*0.5)), int(base*2))
        cells = [(dr, dc) for dr in range(h) for dc in range(w)]
        super().__init__(cells, h, w)

class RatioRectangleBuilding(Building):
    """A 1:2 aspect rectangle (or flipped)."""
    def __init__(self, min_cells: int, max_cells: int):
        base_max = max_cells // 2
        if min_cells > base_max:
            raise ValueError("Not enough room for a 1:2 rectangle")
        base = random.randint(min_cells, base_max)
        w, h = base, base * 2
        if random.random() < 0.5:
            w, h = h, w
        cells = [(dr, dc) for dr in range(h) for dc in range(w)]
        super().__init__(cells, h, w)

class SquareBuilding(Building):
    """A solid square."""
    def __init__(self, min_cells: int, max_cells: int):
        side = random.randint(min_cells, max_cells)
        cells = [(dr, dc) for dr in range(side) for dc in range(side)]
        super().__init__(cells, side, side)

class HollowSquareBuilding(Building):
    """A hollow square shell of configurable thickness."""
    def __init__(self, min_cells: int, max_cells: int, thickness: int = 1):
        # ensure side >= 2*thickness + 1
        side = random.randint(max(2*thickness + 1, min_cells), max_cells)
        cells = []
        for dr in range(side):
            for dc in range(side):
                if dr < thickness or dr >= side - thickness or \
                   dc < thickness or dc >= side - thickness:
                    cells.append((dr, dc))
        super().__init__(cells, side, side)

class TrapezoidBuilding(Building):
    """
    A trapezoid: top width vs bottom width interpolate over height.
    The bounding box width = max(top, bottom).
    """
    def __init__(self, min_cells: int, max_cells: int):
        h       = random.randint(min_cells, max_cells)
        top     = random.randint(min_cells, max_cells)
        bottom  = random.randint(min_cells, max_cells)
        max_w   = max(top, bottom)
        cells   = []
        for dr in range(h):
            if h > 1:
                w_i = round(top + (bottom - top) * dr / (h - 1))
            else:
                w_i = top
            offset = (max_w - w_i) // 2
            for dc in range(w_i):
                cells.append((dr, offset + dc))
        super().__init__(cells, h, max_w)

BUILDING_NAMES = [
    # academic halls
    "Physics Hall", "Chemistry Hall", "Biology Hall", "Mathematics Hall",
    "Computer Science Center", "Engineering Annex", "Civil Engineering Lab",
    "Aerospace Research Wing", "Optics Institute", "Robotics Center",
    "Environmental Sciences", "Neuroscience Pavilion",
    "Humanities Hall", "Philosophy House", "History Hall",
    "Language Arts Building", "Journalism Center", "Music Conservatory",
    "Art & Design Studio", "Theatre Arts Complex",

    # lecture and event venues
    "Centennial Auditorium", "Heritage Theatre", "Innovation Forum",
    "Discovery Lecture Hall", "Founders Conference Center",

    # libraries & study
    "Main Library", "Science Library", "Law Library",

    # student life & admin
    "Student Union", "Campus Bookstore", "Career Services",
    "Health Services", "Recreation Center", "Financial Aid Office",
    "Admissions Hall", "International Programs", "Alumni House",
    "Campus Police Headquarters",

    # dorms & apartments
    "Ocotillo Dorm", "Saguaro Hall", "Agave Suites",
    "Bear Creek Apartments", "Cactus Court", "Desert Vista Hall",
    "Mesa Residence", "Rincon Suites", "Catalina Complex",

    # dining & retail (non‑restaurant bldg)
    "Coffee Commons", "Campus Market", "Print & Copy Center",

    # athletics
    "Bear Down Gym", "Track & Field House", "Aquatics Center",
    "Stadium Offices", "Athletic Training Facility",

    # research parks / misc
    "Innovation Hub", "Technology Incubator", "Sustainability Center",
    "Data Science Lab", "Cybersecurity Institute"
]
