# # src/BearDownBots/__init__.py

from BearDownBots.app import BearDownBotsApp
from BearDownBots.config import Config
def main():
    app = BearDownBotsApp()

def fast():
    """
    Fast mode
    """
    Config.Environment.MAP_ROWS = 500
    Config.Environment.MAP_COLS = 500

    main()

