from BearDownBots.environment.map import Map

_map_instance: Map | None = None

def get_campus_map(rows: int = 50, cols: int = 80) -> Map:
    global _map_instance
    if _map_instance is None:
        _map_instance = create_campus_environment(rows, cols)
    return _map_instance


def create_campus_environment(rows: int, cols: int) -> Map:
    """
    Create a campus environment with the specified number of rows and columns.
    """
    campus_map = Map(rows, cols)
    # Add any additional features or obstacles to the map here


    return campus_map