# # src/BearDownBots/__init__.py

from BearDownBots.app import BearDownBotsApp
from BearDownBots.config import Config
def main():
    app = BearDownBotsApp()

    app.run()

def fast():
    """
    Fast mode for running the application without GUI.
    """
    Config.Environment.MAP_ROWS = 500
    Config.Environment.MAP_COLS = 500

    main()

