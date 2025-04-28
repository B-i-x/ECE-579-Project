# src/BearDownBots/config.py

class Config:

    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800
        WINDOW_HEIGHT_PIXELS = 600

    class Environment:
        # environment
        MAP_ROWS  = 500
        MAP_COLS  = 500
        MAX_BUILDING_ATTEMPTS = 100
        MIN_BUILDING_CELLS = 100
        MAX_BUILDING_CELLS = 250
