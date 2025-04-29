import tkinter as tk
from math import floor
from PIL import Image, ImageDraw, ImageTk

from BearDownBots.config import Config
from BearDownBots.environment.cell import CELL_TYPES
from BearDownBots.environment.map import Map

class GuiWrapper(tk.Tk):
    def __init__(self, campus_map: Map):
        super().__init__()
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{Config.GUI.WINDOW_WIDTH_PIXELS}x{Config.GUI.WINDOW_HEIGHT_PIXELS}")

        self.campus_map = campus_map
        self.offset = (0, 0)  # (row_offset, col_offset)
        self._drag_start = None  # (x_pixel, y_pixel, row_off, col_off)

        self.content_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # base pixel size and zoom factor
        self.base_px = int(Config.GUI.PIXEL_TO_CELL_CONVERSION)
        self.zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        
        # canvas size
        self.canvas_w = int(Config.GUI.WINDOW_WIDTH_PIXELS)
        self.canvas_h = int(Config.GUI.WINDOW_HEIGHT_PIXELS)

        self.campus_canvas = tk.Canvas(
            self.content_paned,
            width=self.canvas_w,
            height=self.canvas_h,
            bg='white'
        )
        self.content_paned.add(self.campus_canvas)

         # generate base image once at base resolution
        self._base_image = self._create_base_image()
        self._scaled_image = None
        self._tk_image = None

        # bind events
        self.campus_canvas.bind('<ButtonPress-1>', self._on_mouse_down)
        self.campus_canvas.bind('<B1-Motion>', self._on_mouse_drag)
        # Windows/Mac scroll
        self.campus_canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        # Linux scroll
        self.campus_canvas.bind('<Button-4>', self._on_mouse_wheel)
        self.campus_canvas.bind('<Button-5>', self._on_mouse_wheel)

        self.render_campus()

    def _create_base_image(self) -> Image.Image:
        """Create the campus image at base pixel-per-cell resolution."""
        rows, cols = self.campus_map.rows, self.campus_map.cols
        img_w = cols * self.base_px
        img_h = rows * self.base_px
        base_img = Image.new('RGB', (img_w, img_h), CELL_TYPES.GROUND.color)
        draw = ImageDraw.Draw(base_img)
        for i in range(rows):
            for j in range(cols):
                cell = self.campus_map.get_cell(i, j)
                for t in (CELL_TYPES.OBSTACLE, CELL_TYPES.BUILDING,
                          CELL_TYPES.WALKWAY, CELL_TYPES.GROUND):
                    if cell.has_type(t):
                        color = t.color
                        break
                x0 = j * self.base_px
                y0 = i * self.base_px
                x1 = x0 + self.base_px
                y1 = y0 + self.base_px
                draw.rectangle([x0, y0, x1, y1], fill=color)
        return base_img

    def _on_mouse_down(self, event):
        row_off, col_off = self.offset
        self._drag_start = (event.x, event.y, row_off, col_off)

    def _on_mouse_drag(self, event):
        if not self._drag_start:
            return
        x0, y0, row_off, col_off = self._drag_start
        dx, dy = event.x - x0, event.y - y0
        step = self.base_px * self.zoom
        dcol = -int(dx / step)
        drow = -int(dy / step)
        max_row = max(0, self.campus_map.rows - int(self.canvas_h/step))
        max_col = max(0, self.campus_map.cols - int(self.canvas_w/step))
        new_row = min(max_row, max(0, row_off + drow))
        new_col = min(max_col, max(0, col_off + dcol))
        self.offset = (new_row, new_col)
        self.render_campus()

    def _on_mouse_wheel(self, event):
        # Determine scroll direction
        delta = 1 if event.delta > 0 or getattr(event, 'num', None) == 4 else -1
        new_zoom = min(self.max_zoom, max(self.min_zoom, self.zoom + delta*0.1))
        if new_zoom != self.zoom:
            # adjust offset to keep center
            center_x = self.canvas_w // 2 + self.offset[1]*self.base_px*self.zoom
            center_y = self.canvas_h // 2 + self.offset[0]*self.base_px*self.zoom
            # update zoom
            self.zoom = new_zoom
            # scale image
            new_size = (int(self._base_image.width * self.zoom), int(self._base_image.height * self.zoom))
            self._scaled_image = self._base_image.resize(new_size, Image.NEAREST)
            # recalc offset to keep center
            col_off = int((center_x - self.canvas_w//2)/(self.base_px*self.zoom))
            row_off = int((center_y - self.canvas_h//2)/(self.base_px*self.zoom))
            self.offset = (max(0, min(self.campus_map.rows, row_off)), max(0, min(self.campus_map.cols, col_off)))
            self.render_campus()

    def render_campus(self):
        """Crop the scaled image by offset and display it."""
        if self._scaled_image is None:
            self._scaled_image = self._base_image.copy()
        step = self.base_px * self.zoom
        row_off, col_off = self.offset
        left = int(col_off * step)
        upper = int(row_off * step)
        right = left + self.canvas_w
        lower = upper + self.canvas_h
        cropped = self._scaled_image.crop((left, upper, right, lower))
        self._tk_image = ImageTk.PhotoImage(cropped)
        self.campus_canvas.delete('all')
        self.campus_canvas.create_image(0, 0, anchor='nw', image=self._tk_image)
