# src/BearDownBots/environment/sidewalks.py

from BearDownBots.app_context import get_app

class Sidewalks:
    """
    Draws all corridor (“walkway”) cells as gray sidewalks
    on the global BearDownBotsApp.canvas.
    """
    def __init__(self, campus):
        """
        campus: an instance of Campus, which now has:
          - grid:    a Grid object with get_cell(r, c).type
          - rows, cols, cell_size
        """
        self.campus = campus
        app = get_app()
        if not hasattr(app, "campus_canvas"):
            raise RuntimeError("BearDownBotsApp must have a .canvas")
        self.canvas = app.campus_canvas

    def draw(self):
        gray = "#808080"  # sidewalk color
        for r in range(self.campus.rows):
            for c in range(self.campus.cols):
                cell = self.campus.grid.get_cell(r, c)
                if cell.type == "walkway":
                    x1 = c * self.campus.cell_size
                    y1 = r * self.campus.cell_size
                    x2 = x1 + self.campus.cell_size
                    y2 = y1 + self.campus.cell_size
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=gray,
                        outline="", width=0
                    )
