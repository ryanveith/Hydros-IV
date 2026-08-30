import drawable_object
import utility.constants as CONSTANTS
from tkinter import *
from PIL import ImageTk


def get_adjacent_tiles(world: dict, tile_x: int, tile_y: int) -> list:
    # Offset-grid neighbors: even vs odd tile_y uses different diagonals.
    # From 0,0 can go to 0,1 and 0,-1 and -1,1 and -1,-1.
    # From 0,1 can go to 1,0 and 1,2 and 0,0 and 0,2.
    if tile_y % 2 == 0:
        coords = [
            (tile_x - 1, tile_y + 1),
            (tile_x - 1, tile_y - 1),
            (tile_x, tile_y + 1),
            (tile_x, tile_y - 1),
        ]
    else:
        coords = [
            (tile_x, tile_y + 1),
            (tile_x, tile_y - 1),
            (tile_x + 1, tile_y + 1),
            (tile_x + 1, tile_y - 1),
        ]
    tiles = []
    for x, y in coords:
        tile = world.get(str(x) + "x" + str(y))
        if tile is not None:
            tiles.append(tile)
    return tiles


class Square(drawable_object.Drawable_Object):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, str(x)+"x"+str(y), "Static Terrain", CONSTANTS.TILE_WIDTH,  CONSTANTS.TILE_HEIGHT, "diamond.png")
        self.world = "Hydros"        
        self.terrain = "ground"
        self.occupied = None
        self.resources = []

    def draw_self(self, zoom: int, screen_x: int, screen_y: int, canvas: Canvas, mode: str, tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        super().draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)
        for item in self.resources:
            item.draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)
