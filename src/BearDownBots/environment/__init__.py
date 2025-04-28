from BearDownBots.environment.map import Map
from BearDownBots.config import Config


_map_instance: Map | None = None

def get_campus_map() -> Map:
    global _map_instance
    if _map_instance is None:
        _map_instance = create_campus_environment()
    return _map_instance


def create_campus_environment() -> Map:
    """
    Create a campus environment with the specified number of rows and columns.
    """
    
    campus_map = Map(Config.Environment.MAP_ROWS, Config.Environment.MAP_COLS)
    # Add any additional features or obstacles to the map here

    print("Campus environment created with dimensions:", campus_map.rows, "x", campus_map.cols)
    print(campus_map)  # This will call the __repr__ method of the Map class

    return campus_map