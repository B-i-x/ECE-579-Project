import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

from BearDownBots.config import Config
from BearDownBots.environment.cell import CELL_TYPES
from BearDownBots.environment.map import Map
from BearDownBots.render.loading import ProgressWindow

class CampusRenderer:
    def __init__(self, parent, campus_map: Map, progress_window: ProgressWindow = None):
        """
        Initialize the CampusRenderer with a parent widget and a campus map.
        """
        self.progress_window = progress_window
        self.campus_map = campus_map
        self.parent = parent
        self.offset = (0, 0)
        self._drag_start = None
        self.base_px = int(Config.GUI.PIXEL_TO_CELL_CONVERSION)
        self.zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.canvas_w = int(Config.GUI.WINDOW_WIDTH_PIXELS)
        self.canvas_h = int(Config.GUI.WINDOW_HEIGHT_PIXELS)

        # setup canvas
        self.canvas = tk.Canvas(
            self.parent,
            width=self.canvas_w,
            height=self.canvas_h,
            bg='white'
        )
        self.parent.add(self.canvas)

        # generate base image once
        self._base_image = self._create_base_image()
        self._scaled_image = self._base_image.copy()
        self._tk_image = None

        # bind events
        self.canvas.bind('<ButtonPress-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)

        self.render()

    def _create_base_image(self) -> Image.Image:
        rows, cols = self.campus_map.rows, self.campus_map.cols
        img_w = cols * self.base_px
        img_h = rows * self.base_px
        img = Image.new('RGB', (img_w, img_h), CELL_TYPES.GROUND.color)
        draw = ImageDraw.Draw(img)

        self.progress_window.start_phase("Rendering Campus", rows)

        step = 0
        for i in range(rows):
            for j in range(cols):
                cell = self.campus_map.get_cell(i, j)
                for t in (CELL_TYPES.OBSTACLE, CELL_TYPES.BUILDING,
                          CELL_TYPES.WALKWAY, CELL_TYPES.GROUND):
                    if cell.has_type(t):
                        color = t.color
                        break
                x0, y0 = j*self.base_px, i*self.base_px
                draw.rectangle([x0, y0, x0+self.base_px, y0+self.base_px], fill=color)


                
            if i % 5 == 0:
                self.progress_window.update_progress(i)


        return img

    def _on_mouse_down(self, event):
        self._drag_start = (event.x, event.y, *self.offset)

    def _on_mouse_drag(self, event):
        if not self._drag_start:
            return
        x0, y0, ro, co = self._drag_start
        dx, dy = event.x - x0, event.y - y0
        step = self.base_px * self.zoom
        dro = -int(dy/step)
        dco = -int(dx/step)
        max_ro = max(0, self.campus_map.rows - int(self.canvas_h/step))
        max_co = max(0, self.campus_map.cols - int(self.canvas_w/step))
        ro_new = min(max_ro, max(0, ro+dro))
        co_new = min(max_co, max(0, co+dco))
        self.offset = (ro_new, co_new)
        self.render()

    def _on_mouse_wheel(self, event):
        delta = 1 if getattr(event, 'delta', 0) > 0 or event.num == 4 else -1
        new_zoom = min(self.max_zoom, max(self.min_zoom, self.zoom + delta*0.1))
        if new_zoom != self.zoom:
            # compute center in image coords
            cx = self.canvas_w/2 + self.offset[1]*self.base_px*self.zoom
            cy = self.canvas_h/2 + self.offset[0]*self.base_px*self.zoom
            self.zoom = new_zoom
            size = (int(self._base_image.width*self.zoom), int(self._base_image.height*self.zoom))
            self._scaled_image = self._base_image.resize(size, Image.NEAREST)
            # recalc offset to maintain center
            co = int((cx - self.canvas_w/2)/(self.base_px*self.zoom))
            ro = int((cy - self.canvas_h/2)/(self.base_px*self.zoom))
            self.offset = (max(0, ro), max(0, co))
            self.render()

    def render(self):
        step = self.base_px * self.zoom
        ro, co = self.offset
        left, top = int(co*step), int(ro*step)
        right, bottom = left+self.canvas_w, top+self.canvas_h
        crop = self._scaled_image.crop((left, top, right, bottom))
        self._tk_image = ImageTk.PhotoImage(crop)
        self.canvas.delete('all')
        self.canvas.create_image(0,0,anchor='nw',image=self._tk_image)