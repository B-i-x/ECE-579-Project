# src/BearDownBots/config.py

class Config:

    class GUI:
        # general
        WINDOW_WIDTH_PIXELS  = 800
        WINDOW_HEIGHT_PIXELS = 600

    class Environment:
        # environment
        MAP_ROWS  = 50
        MAP_COLS  = 80

# optional singleton instance if you prefer attribute access
config = Config()
