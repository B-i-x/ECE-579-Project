"""
Simple singleton pattern to store and retrieve the main Tk application instance.
"""
from BearDownBots.gui import BearDownBotsApp

_app = None

def set_app(app):
    global _app
    _app = app
 

def get_app() -> BearDownBotsApp:
    """
    Retrieve the globally stored Tk root (FoodieApp) instance.

    Returns:
        The FoodieApp instance, or None if not set.
    """
    return _app

