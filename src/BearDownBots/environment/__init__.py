import random

from BearDownBots.environment.map import Map
from BearDownBots.config import Config
from BearDownBots.environment.buildings import Building
from BearDownBots.environment.cell import CELL_TYPES


from BearDownBots.render.loading import ProgressWindow


def create_campus_environment(progress_window: ProgressWindow) -> Map:
    """
    Create a campus environment with the specified number of rows and columns.
    """
    # Initialize the progress window
    progress_window.start_phase("Creating Campus", Config.Environment.MAX_BUILDING_ATTEMPTS)

    campus_map = Map(Config.Environment.MAP_ROWS, Config.Environment.MAP_COLS)

    choices = list(Building.__subclasses__())
    weights = [cls.likelihood for cls in choices]

    for i in range(Config.Environment.MAX_BUILDING_ATTEMPTS):
        x = random.randint(0, campus_map.rows - 1)
        y = random.randint(0, campus_map.cols - 1)

        cell = campus_map.get_cell(x, y)
        if cell.has_type(CELL_TYPES.BUILDING) or cell.has_type(CELL_TYPES.WALKWAY):
            continue

        cls = random.choices(choices, weights=weights, k=1)[0]
        bld = cls.generate(
            Config.Environment.MIN_BUILDING_CELLS,
            Config.Environment.MAX_BUILDING_CELLS
        )

        attempt = campus_map.attempt_to_place_building((x, y), bld)
        if attempt:
            print(f"Placed {bld} at ({x}, {y})")
        else:
            print(f"Failed to place {bld} at ({x}, {y})")

        progress_window.update_progress(i)

    campus_map.connect_sidewalks()
    
    return campus_map