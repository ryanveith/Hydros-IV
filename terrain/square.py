import drawable_object
import utility.constants as CONSTANTS
from tkinter import *
from PIL import ImageTk

class Square(drawable_object.Drawable_Object):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, str(x)+"x"+str(y), "Static Terrain", CONSTANTS.TILE_WIDTH,  CONSTANTS.TILE_HEIGHT, "diamond.png")
        self.world = "Hydros"        
        self.terrain = "ground"
        self.occupied = None
        self.resources = [];

    def draw_self(self, zoom: int, screen_x: int, screen_y: int, canvas: Canvas, mode: str, tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        super().draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)
        for item in self.resources:
            item.draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)
