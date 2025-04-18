from BearDownBots.app_context import get_app


class Robot:
    def __init__(self, robot_id, start_position):
        self.id = robot_id
        self.position = start_position

        # grab the singleton app and ask it to draw me
        app = get_app()

    def move_to(self, new_position):
        self.position = new_position

        # tell the GUI to update my marker
        app = get_app()
