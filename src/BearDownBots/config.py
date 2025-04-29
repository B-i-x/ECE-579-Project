# src/BearDownBots/config.py

class Config:

    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800
        WINDOW_HEIGHT_PIXELS = 600

    class Environment:
        # environment
        MAP_ROWS  = 2000
        MAP_COLS  = 2000
        MAX_BUILDING_ATTEMPTS = 100 ## the higher the number, the denser the campus is
        MIN_BUILDING_CELLS = 75
        MAX_BUILDING_CELLS = 200

    def get_asset_dir():
        # Get the directory of the assets folder
        import os
        pkg_dir    = os.path.dirname(__file__)               # .../src/BearDownBots
        src_dir    = os.path.dirname(pkg_dir)                # .../src
        root_dir   = os.path.dirname(src_dir)                # project root
        assets_dir = os.path.join(root_dir, "assets")
        return assets_dir
