import tkinter as tk
from math import floor

from BearDownBots.config import Config
from BearDownBots.environment.cell import CELL_TYPES
from BearDownBots.environment.map import Map

class GuiWrapper(tk.Tk):
    def __init__(self, map: Map):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{Config.GUI.WINDOW_WIDTH_PIXELS}x{Config.GUI.WINDOW_HEIGHT_PIXELS}")

        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        self.campus_map = map
        self.campus_canvas = tk.Canvas(self.content_paned,
                                width=Config.GUI.WINDOW_WIDTH_PIXELS,
                                height=Config.GUI.WINDOW_HEIGHT_PIXELS,
                                bg='white')
        

        self.campus_canvas.pack(fill=tk.BOTH, expand=True)
        # Left pane: campus view


    def render_campus(self, offset: tuple[int,int]=(0,0)):
        """
        Draws the visible portion of campus_map into the canvas.
        offset: (row_offset, col_offset) in cells to pan the view.
        Uses Config.GUI.PIXEL_TO_CELL_CONVERSION to map cells to pixels.
        """
        # clear previous drawings
        self.campus_canvas.delete('all')

        px_per_cell = Config.GUI.PIXEL_TO_CELL_CONVERSION
        canvas_w = int(self.campus_canvas['width'])
        canvas_h = int(self.campus_canvas['height'])

        # compute how many cells fit
        cols_visible = floor(canvas_w / px_per_cell)
        rows_visible = floor(canvas_h / px_per_cell)

        row_off, col_off = offset
        for i in range(rows_visible):
            for j in range(cols_visible):
                map_i = row_off + i
                map_j = col_off + j
                try:
                    cell = self.campus_map.get_cell(map_i, map_j)
                except IndexError:
                    # out of bounds: draw as empty ground
                    color = CELL_TYPES.GROUND.color
                else:
                    # pick highest-priority type in cell.types
                    # priority: OBSTACLE > BUILDING > WALKWAY > GROUND
                    for t in (CELL_TYPES.OBSTACLE, CELL_TYPES.BUILDING, CELL_TYPES.WALKWAY, CELL_TYPES.GROUND):
                        if cell.has_type(t):
                            color = t.color
                            break

                x0 = j * px_per_cell
                y0 = i * px_per_cell
                x1 = x0 + px_per_cell
                y1 = y0 + px_per_cell

                # draw rectangle
                self.campus_canvas.create_rectangle(x0, y0, x1, y1, fill=color)
