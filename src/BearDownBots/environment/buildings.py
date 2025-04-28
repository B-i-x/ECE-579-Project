# src/BearDownBots/environment/buildings.py
import random
from BearDownBots.environment.cell_types import CELL_TYPES
from BearDownBots.environment.map import Map
from BearDownBots.config import Config


def randomly_place_buildings_onto_map(campus_map: Map) -> bool:
    """
    Attempt to place a random building on the map.
    Returns True if any placement succeeds within the configured attempts.
    """

    choices = list(Building.__subclasses__())
    weights = [cls.likelihood for cls in choices]

    for _ in range(Config.Environment.MAX_BUILDING_ATTEMPTS):
        x = random.randint(0, campus_map.rows - 1)
        y = random.randint(0, campus_map.cols - 1)

        cls = random.choices(choices, weights=weights, k=1)[0]
        bld = cls.generate(
            Config.Environment.MIN_BUILDING_CELLS,
            Config.Environment.MAX_BUILDING_CELLS
        )

        attempt = campus_map.attempt_to_place_building((x, y), (bld.h, bld.w))
        if attempt:
            print(f"Placed {bld} at ({x}, {y})")
        else:
            print(f"Failed to place {bld} at ({x}, {y})")
    

class Building:
    """Base class for all building types."""
    likelihood: float = 1.0  # default selection weight

    def __init__(self, cells: list[tuple[int,int]], height: int, width: int):
        self.cells  = cells   # list of (dr, dc) offsets from top-left
        self.h      = height
        self.w      = width
        self.name   = random.choice(BUILDING_NAMES)  # random name from list

    @classmethod
    def generate(cls, min_cells: int, max_cells: int) -> 'Building':
        """
        Factory method to create a new building instance with given cell count bounds.
        Subclasses may override if additional parameters are needed.
        """
        return cls(min_cells, max_cells)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(h={self.h}, w={self.w}, cells={len(self.cells)})"


class RectangleBuilding(Building):
    """A general rectangle with random width and height."""
    likelihood = 1.0

    def __init__(self, min_cells: int, max_cells: int):
        base = random.randint(min_cells, max_cells)
        w = random.randint(max(1, int(base * 0.5)), int(base * 2))
        h = random.randint(max(1, int(base * 0.5)), int(base * 2))
        cells = [(dr, dc) for dr in range(h) for dc in range(w)]
        super().__init__(cells, h, w)


class RatioRectangleBuilding(Building):
    """A 1:2 aspect rectangle (or flipped)."""
    likelihood = 0.8

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
    likelihood = 0.8

    def __init__(self, min_cells: int, max_cells: int):
        side = random.randint(min_cells, max_cells)
        cells = [(dr, dc) for dr in range(side) for dc in range(side)]
        super().__init__(cells, side, side)


class HollowSquareBuilding(Building):
    likelihood = 0.5
    thickness: int = 5

    def __init__(self, min_cells: int, max_cells: int, thickness: int = None):
        t = thickness if thickness is not None else type(self).thickness
        side = random.randint(max(2 * t + 1, min_cells), max_cells)
        cells = []
        for dr in range(side):
            for dc in range(side):
                if dr < t or dr >= side - t or dc < t or dc >= side - t:
                    cells.append((dr, dc))
        super().__init__(cells, side, side)


class TrapezoidBuilding(Building):
    """
    A trapezoid: top width vs bottom width interpolate over height.
    The bounding box width = max(top, bottom).
    """
    likelihood = 0.9

    def __init__(self, min_cells: int, max_cells: int):
        h = random.randint(min_cells, max_cells)
        top = random.randint(min_cells, max_cells)
        bottom = random.randint(min_cells, max_cells)
        max_w = max(top, bottom)
        cells = []
        for dr in range(h):
            w_i = round(top + (bottom - top) * dr / (h - 1)) if h > 1 else top
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
