import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageColor

from BearDownBots.config import Config
from BearDownBots.static.cell import CELL_TYPES, Position
from BearDownBots.static.map import Map
from BearDownBots.render.loading import ProgressWindow
from BearDownBots.dynamic.robot import Robot

class CampusRenderer:
    def __init__(self, parent, 
                 campus_map: Map, 
                 progress_window: ProgressWindow = None,
                 campus_render_data = None):
        """
        Initialize the CampusRenderer with a parent widget and a campus map.
        """
        self.progress_window = progress_window
        self.campus_map = campus_map
        self.parent = parent

        self.renderer_data = campus_render_data

        self._drag_start = None

        # physical canvas size (pixels)
        self.canvas_w = 0
        self.canvas_h = 0
        self.offset_x = 0
        self.offset_y = 0

        # the only place we generate the base‐image at 1px=1cell
        self._create_base_image()
        base_w, base_h = self._base_image.size
        
        # dynamic zoom limits so we NEVER zoom out below the canvas size
        self.min_zoom = 0.75
        self.max_zoom = 8.0

        self.canvas = tk.Canvas(
            self.parent,
            bg='white'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)  # ensure it fills its container

        self.parent.add(self.canvas)

        self.canvas.bind("<Configure>", self._on_resize)

         # pre‐scale once
        scaled_size      = (int(base_w * self.renderer_data.zoom), int(base_h * self.renderer_data.zoom))
        self._scaled_image = self._base_image.resize(scaled_size, Image.NEAREST)
        self._tk_image     = None

        # bind events
        self.canvas.bind('<ButtonPress-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)

        self.render()

    def _on_resize(self, event):
        self.canvas_w = event.width
        self.canvas_h = event.height

        # Optionally rebuild scaled image for new canvas
        new_size = (
            int(self._base_image.width * self.renderer_data.zoom),
            int(self._base_image.height * self.renderer_data.zoom)
        )
        self._scaled_image = self._base_image.resize(new_size, Image.NEAREST)

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
        z        = self.renderer_data.zoom

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
        self._drag_start = (event.x, event.y, self.renderer_data.offset_x, self.renderer_data.offset_y)

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
        self.renderer_data.offset_x = new_off_x
        self.renderer_data.offset_y = new_off_y

        self.render()

    def _on_mouse_wheel(self, event):
        # 1) Figure out whether we’re zooming in or out
        delta     = 1 if getattr(event, 'delta', 0) > 0 or event.num == 4 else -1
        old_zoom  = self.renderer_data.zoom
        new_zoom  = min(self.max_zoom, max(self.min_zoom, old_zoom + delta * 0.1))
        if new_zoom == old_zoom:
            return

        # 2) Compute the current canvas‐center in base‐image coords
        cx_canvas, cy_canvas = self.canvas_w / 2, self.canvas_h / 2
        # offset_x is in SCALED‐IMAGE pixels, so convert back to base‐coords:
        center_base_x = (self.renderer_data.offset_x + cx_canvas) / old_zoom
        center_base_y = (self.renderer_data.offset_y + cy_canvas) / old_zoom

        # 3) Apply the new zoom and rebuild the scaled image
        self.renderer_data.zoom = new_zoom
        new_size = (
            int(self._base_image.width  * new_zoom),
            int(self._base_image.height * new_zoom)
        )
        self._scaled_image = self._base_image.resize(new_size, Image.NEAREST)

        # 4) Compute new offsets so that (center_base_x,center_base_y) sits at canvas center
        self.renderer_data.offset_x = center_base_x * new_zoom - cx_canvas
        self.renderer_data.offset_y = center_base_y * new_zoom - cy_canvas

        max_off_x = max(0, self._scaled_image.width  - self.canvas_w)
        max_off_y = max(0, self._scaled_image.height - self.canvas_h)
        self.offset_x = min(max(self.offset_x, 0), max_off_x)
        self.offset_y = min(max(self.offset_y, 0), max_off_y)

        # 6) Finally, re-render
        self.render()


    def render(self):
        # crop the scaled image at pixel offset
        x0, y0 = int(self.renderer_data.offset_x), int(self.renderer_data.offset_y)
        x1, y1 = x0 + self.canvas_w, y0 + self.canvas_h
        view = self._scaled_image.crop((x0, y0, x1, y1))
        self._tk_image = ImageTk.PhotoImage(view)

        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self._tk_image)