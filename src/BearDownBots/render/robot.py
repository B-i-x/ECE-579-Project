class RobotRenderer:
    def __init__(self):
        # … existing init …
        self.robot_icons: dict[Robot, int] = {}  # Robot → canvas item id

    def render(self):
        # … existing background draw …
        self._draw_robots()

    def _draw_robots(self):
        px = self.base_px * self.zoom
        ro, co = self.offset

        # 1) Create icon if new
        for robot in self.campus_map.robots:
            if robot not in self.robot_icons:
                # a simple circle or image
                x, y = robot.get_position()
                cx = (y - co + 0.5) * px
                cy = (x - ro + 0.5) * px
                item = self.canvas.create_oval(
                    cx- px*0.4, cy- px*0.4, cx+ px*0.4, cy+ px*0.4,
                    fill="blue", tags="robot"
                )
                self.robot_icons[robot] = item

        # 2) Move existing icons
        for robot, item in list(self.robot_icons.items()):
            if robot not in self.campus_map.robots:
                self.canvas.delete(item)
                del self.robot_icons[robot]
                continue
            x, y = robot.get_position()
            cx = (y - co + 0.5) * px
            cy = (x - ro + 0.5) * px
            self.canvas.coords(item, cx- px*0.4, cy- px*0.4, cx+ px*0.4, cy+ px*0.4)
