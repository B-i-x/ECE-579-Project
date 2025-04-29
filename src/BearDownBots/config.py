# src/BearDownBots/config.py

class Config:

    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800
        WINDOW_HEIGHT_PIXELS = 600
        PIXEL_TO_CELL_CONVERSION = 1

    class Environment:
        # environment
        MAP_ROWS  = 2000
        MAP_COLS  = 2000
        MAX_BUILDING_ATTEMPTS = 100 ## the higher the number, the denser the campus is
        MIN_BUILDING_CELLS = 100
        MAX_BUILDING_CELLS = 250
