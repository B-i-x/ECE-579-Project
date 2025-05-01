# src/BearDownBots/config.py

class Config:
    TIME_SCALE = 1 ## time scale for the simulation (1 = real time, 2 = twice as fast, etc.)
    
    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800 ## width of the window in pixels
        WINDOW_HEIGHT_PIXELS = 600 ## height of the window in pixels
        ROBOT_ZOOM_FACTOR = 2.5 ## zoom factor for the robot images (1 = normal size, 0.5 = half size, etc.)

    class Environment:
        # environment
        MAP_ROWS  = 2000 ## number of rows in the map
        MAP_COLS  = 2000 ## number of columns in the map
        MAX_BUILDING_ATTEMPTS = 100 ## the higher the number, the denser the campus is
        MIN_BUILDING_CELLS = 75 ## minimum number of cells a building can occupy
        MAX_BUILDING_CELLS = 200 ## maximum number of cells a building can occupy
        OBSTACLES_AS_PERCENTAGE_OF_WALKWAYS = 0.002 ## percentage is in decimal form (0.002 = 0.2%)

    class Simulation:
        # simulation
        NUM_ROBOTS = 3

    def get_asset_dir():
        # Get the directory of the assets folder
        import os
        pkg_dir    = os.path.dirname(__file__)               # .../src/BearDownBots
        src_dir    = os.path.dirname(pkg_dir)                # .../src
        root_dir   = os.path.dirname(src_dir)                # project root
        assets_dir = os.path.join(root_dir, "assets")
        return assets_dir
