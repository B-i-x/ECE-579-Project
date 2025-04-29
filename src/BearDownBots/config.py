# src/BearDownBots/config.py

class Config:

    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800
        WINDOW_HEIGHT_PIXELS = 600
        PIXEL_TO_CELL_CONVERSION = 1

    class Environment:
        # environment
        MAP_ROWS  = 1000
        MAP_COLS  = 1000
        MAX_BUILDING_ATTEMPTS = 100
        MIN_BUILDING_CELLS = 100
        MAX_BUILDING_CELLS = 250
