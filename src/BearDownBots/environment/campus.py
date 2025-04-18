from BearDownBots.app_context import get_app

class Campus:
    """
    Draws a grid of boxes (the “campus”) onto the main app’s canvas.
    """

    def __init__(self, rows: int, cols: int, cell_size: int = 20):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # grab the singleton app and its canvas
        app = get_app()
        try:
            self.canvas = app.canvas
        except AttributeError:
            raise RuntimeError("BearDownBotsApp must have a .canvas attribute")

        # store rectangle IDs so you can update them later
        self._cells = {}
        self._draw_grid()

    def _draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="lightgray", fill=""
                )
                self._cells[(r, c)] = rect

    def highlight_cell(self, r: int, c: int, color: str="yellow"):
        """
        Example helper: fill one cell with color.
        """
        rect_id = self._cells.get((r, c))
        if rect_id:
            self.canvas.itemconfig(rect_id, fill=color)
