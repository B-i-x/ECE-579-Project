import tkinter as tk

from BearDownBots.config import Config

from BearDownBots.static.map import Map

from BearDownBots.render.campus import CampusRenderer
from BearDownBots.render.loading import ProgressWindow
from BearDownBots.render.user_dash import UserDashboardRenderer
from BearDownBots.render.restaurant_dash import RestaurantDashboardRenderer
from BearDownBots.render.robot import RobotRenderer

from BearDownBots.dynamic.robot import Robot

class CampusRendererDataStorage:
    """
    Class to store the campus renderer data.
    """
    def __init__(self):
        self.zoom = Config.GUI.CAMPUS_MAP_ZOOM
        self.offset_x = 0
        self.offset_y = 0


class GuiWrapper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()


        # --- Main window title & size ---
        width = Config.GUI.WINDOW_WIDTH_PIXELS
        height = Config.GUI.WINDOW_HEIGHT_PIXELS
        self.title("Bear Down Bots Simulator")
        self.geometry(f"{width}x{height}")

        self.user_dash_frame = tk.Frame(self, height=80, bg="lightgrey")
        self.user_dash_frame.pack(side=tk.TOP, fill=tk.X)
        self.user_dash = UserDashboardRenderer(self.user_dash_frame)
        self.user_dash.render()

        # --- Main split content area ---
        self.content_paned = tk.PanedWindow(self,orient = tk.HORIZONTAL, sashrelief = tk.RAISED,  showhandle = True)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        # Right pane: info canvas
        self.restaurant_dash_frame = tk.Canvas(self.content_paned, bg="white", width=240)
        self.content_paned.add(self.restaurant_dash_frame, minsize=180)

        self.restaurant_dash = RestaurantDashboardRenderer(self.restaurant_dash_frame)

        self.campus_render_data = CampusRendererDataStorage()

    def add_objects_to_render(self, 
                                campus_map: Map,
                                robots: list,
                                order_scheduler,
                                progress_window: ProgressWindow = None):
        """
        Add objects to the campus map renderer.
        """
        self.campus_map : Map = campus_map
        self.robots : list[Robot] = robots
        self.progress_window : ProgressWindow = progress_window
        self.order_scheduler = order_scheduler

        self.restaurant_dash.add_robots(robots)
        self.restaurant_dash.add_scheduler(order_scheduler)


    def setup_dynamic_events(self):
        """
        Setting up the GUI components.
        """
        self.campus_renderer = CampusRenderer(self.content_paned, self.campus_map, self.progress_window, self.campus_render_data)
        self.campus_renderer.render()

        self.robot_renderer = RobotRenderer(self.campus_renderer.canvas, self.campus_render_data)
        self.robot_renderer.render_robots(self.robots)
        # now re-bind the same events to also redraw robots afterwards
        canvas = self.campus_renderer.canvas
        for seq in ('<ButtonPress-1>', '<B1-Motion>', '<MouseWheel>', '<Button-4>', '<Button-5>'):
            canvas.bind(seq,
                        lambda e, rr=self.robot_renderer, rs=self.robots: rr.render_robots(rs),
                        add='+')
    
        self.restaurant_dash.add_campus_renderer_data(self.campus_renderer, self.campus_render_data)
        self.restaurant_dash.render()
        self.restaurant_dash.setup_robot_click_event()
        for lbl in self.restaurant_dash.robot_label:
            lbl.bind(
                "<Button-1>",
                lambda e, rr=self.robot_renderer, rs=self.robots: rr.render_robots(rs),
                add='+'
            )
        
        self.progress_window.destroy()  

        self.deiconify()
        self.mainloop()



