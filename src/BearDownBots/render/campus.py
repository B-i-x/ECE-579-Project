import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageColor

from BearDownBots.config import Config
from BearDownBots.static.cell import CELL_TYPES, Position
from BearDownBots.static.map import Map
from BearDownBots.render.loading import ProgressWindow
from BearDownBots.dynamic.robot import Robot

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

        # physical canvas size (pixels)
        self.canvas_w = int(Config.GUI.WINDOW_WIDTH_PIXELS)
        self.canvas_h = int(Config.GUI.WINDOW_HEIGHT_PIXELS)
        self.offset_x = 0
        self.offset_y = 0

        # the only place we generate the base‐image at 1px=1cell
        self._create_base_image()
        base_w, base_h = self._base_image.size
        
        # dynamic zoom limits so we NEVER zoom out below the canvas size
        self.min_zoom = 0.75
        self.max_zoom = 8.0
        self.zoom = 1

        # setup canvas
        self.canvas = tk.Canvas(
            self.parent,
            width=self.canvas_w,
            height=self.canvas_h,
            bg='white'
        )
         # pre‐scale once
        scaled_size      = (int(base_w * self.zoom), int(base_h * self.zoom))
        self._scaled_image = self._base_image.resize(scaled_size, Image.NEAREST)
        self._tk_image     = None

        # setup canvas widget
        self.canvas = tk.Canvas(parent, width=self.canvas_w, height=self.canvas_h, bg='white')
        parent.add(self.canvas)

        # bind events
        self.canvas.bind('<ButtonPress-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)

        self.render()

    def _create_base_image(self) -> Image.Image:
        rows, cols = self.campus_map.rows, self.campus_map.cols
        img_w = cols
        img_h = rows 
        img = Image.new('RGB', (img_w, img_h), CELL_TYPES.GROUND.color)
        draw = ImageDraw.Draw(img)

        self.progress_window.start_phase("Rendering Campus", rows)

        for i in range(rows):
            for j in range(cols):
                cell = self.campus_map.get_cell(i, j)
                for t in CELL_TYPES:
                    if cell.has_type(t):
                        color = t.color
                        break
                x0, y0 = j, i
                draw.rectangle([x0, y0, x0+1, y0+1], fill=color)


                
            if i % 5 == 0:
                self.progress_window.update_progress(i)

        font = ImageFont.load_default()
        for bld in self.campus_map.buildings:
            x0, y0 = bld.get_center_coords()
            text = bld.name
            x_text = y0 + 1
            y_text = x0 + 1
            draw.text((x_text, y_text), text, fill='black', font=font)

        self._base_image = img

    def update_robot_positions(self, robots: list[Robot]):
        """
        Batch‐update the 1px=1cell base image for all robots,
        then rebuild the scaled image and re‐render.
        """
        base_pix = self._base_image.load()
        z        = self.zoom

        for robot in robots:
            # --- ERASE old robot pixel ---
            prev = robot.previous_position
            if prev is not None:
                # map row/col → x,y
                px_old = prev.y
                py_old = prev.x

                # turn that cell back into a walkway
                self.campus_map.remove_cell_type(py_old, px_old, CELL_TYPES.ROBOT)
                self.campus_map.add_cell_type   (py_old, px_old, CELL_TYPES.WALKWAY)

                # grab the walkway color and paint it
                walkway_rgb = ImageColor.getrgb(CELL_TYPES.WALKWAY.color)
                base_pix[px_old, py_old] = walkway_rgb

            # --- DRAW new robot pixel ---
            px_new = robot.position.y
            py_new = robot.position.x
            robot_rgb = ImageColor.getrgb(CELL_TYPES.ROBOT.color)
            base_pix[px_new, py_new] = robot_rgb

            # remember for next frame
            robot.previous_position = Position(py_new, px_new)

        # --- rebuild the zoomed image and redraw ---
        base = self._base_image
        new_size = (int(base.width  * z), int(base.height * z))
        self._scaled_image = base.resize(new_size, Image.NEAREST)

        print(f"Moved robot {robot.id} to {robot.position}")
        self.render()

        


    def _on_mouse_down(self, event):
        # capture the *current* pixel offset when you start dragging
        self._drag_start = (event.x, event.y, self.offset_x, self.offset_y)

    def _on_mouse_drag(self, event):
        if not hasattr(self, '_drag_start'):
            return

        x0, y0, off_x0, off_y0 = self._drag_start
        dx = event.x - x0
        dy = event.y - y0

        # invert so map moves with mouse
        new_off_x = off_x0 - dx
        new_off_y = off_y0 - dy

        # no clamping—pan freely
        self.offset_x = new_off_x
        self.offset_y = new_off_y

        self.render()

    def _on_mouse_wheel(self, event):
        delta = 1 if getattr(event, 'delta', 0) > 0 or event.num == 4 else -1
        new_zoom = min(self.max_zoom, max(self.min_zoom, self.zoom + delta*0.1))
        if new_zoom != self.zoom:
            # compute center in image coords
            cx = self.canvas_w/2 + self.offset[1]*self.zoom
            cy = self.canvas_h/2 + self.offset[0]*self.zoom
            self.zoom = new_zoom
            size = (int(self._base_image.width*self.zoom), int(self._base_image.height*self.zoom))
            self._scaled_image = self._base_image.resize(size, Image.NEAREST)
            # recalc offset to maintain center
            co = int((cx - self.canvas_w/2)/(self.zoom))
            ro = int((cy - self.canvas_h/2)/(self.zoom))
            self.offset = (max(0, ro), max(0, co))
            self.render()

    def render(self):
        # crop the scaled image at pixel offset
        x0, y0 = int(self.offset_x), int(self.offset_y)
        x1, y1 = x0 + self.canvas_w, y0 + self.canvas_h
        view = self._scaled_image.crop((x0, y0, x1, y1))
        self._tk_image = ImageTk.PhotoImage(view)

        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self._tk_image)