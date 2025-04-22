# src/BearDownBots/__init__.py

from BearDownBots.gui import BearDownBotsApp
from BearDownBots.app_context import set_app
from BearDownBots.environment.campus import Campus
from BearDownBots.environment.sidewalks import Sidewalks
from BearDownBots.environment.obstacles import ObstacleField


def main():
    # 1) Define your logical campus size and cell‐pixel size
    rows, cols = 300, 300
    cell_size = 2
    map_width = cols * cell_size
    map_height = rows * cell_size

    # 2) Define your dashboard and info‐pane dimensions
    dashboard_h = 80
    info_width = 200

    # 3) Compute the total window size
    win_width = map_width + info_width
    win_height = map_height + dashboard_h

    # 4) Create the app window at exactly the size you need
    app = BearDownBotsApp(width=win_width, height=win_height)
    set_app(app)

    # 5) Fix the two canvases to the correct sizes
    app.campus_canvas.config(width=map_width, height=map_height)
    app.info_canvas   .config(width=info_width)
    app.dashboard_frame.config(height=dashboard_h)

    # 6) Build the campus, draw sidewalks
    campus = Campus(rows=rows, cols=cols, cell_size=cell_size)

    # 7) Sprinkle static obstacles on 2% of walkways
    obs_field = ObstacleField(campus)

    obs_field.drop(num_obstacles=10, forbid=campus.restaurant_coords)

    # 8) Launch
    app.mainloop()

if __name__ == "__main__":
    main()
