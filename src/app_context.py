"""
Simple singleton pattern to store and retrieve the main Tk application instance.
"""
from main import FoodieApp

_app = None

def set_app(app):
    global _app
    _app = app


def get_app() -> FoodieApp:
    """
    Retrieve the globally stored Tk root (FoodieApp) instance.

    Returns:
        The FoodieApp instance, or None if not set.
    """
    return _app