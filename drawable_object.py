from tkinter import *
from PIL import Image, ImageTk

import utility.constants as CONSTANTS

class Drawable_Object():
    def __init__(self, x: int, y: int, tag: str, width: int, height: int, image_file: str):
        self.tkinter_id = None
        self.tag: str = tag
        self.x: int = x
        self.y: int = y
        self.x_offset: int = 0
        self.y_offset: int = 0
        self.width: int = width
        self.height:int = height
        self.image_file: str = "images/" + image_file

    # By default update self should do nothing
    def update_self(self, world_controller):
        return None

    # Add object to given canvas, otherwise update canvas with objects current positon relative to the screen's position
    def draw_self(self, zoom, screen_x, screen_y, canvas, mode, image_list):
        if (self.tkinter_id == None):
            # This is a new object that needs to get added
            object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
            self.tkinter_id = canvas.create_image(
                    int(zoom / 100 * ((self.x + (self.y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x) + self.x_offset), 
                    int(zoom / 100 * (self.y * CONSTANTS.TILE_HEIGHT + screen_y) + self.y_offset), 
                    image=object_image, 
                    anchor="s", #"center",
                    tag=self.tag)
            # prevent image from being garbage collected
            # TODO - Currently should just use self, if they are all individual images
            image_list[self.tkinter_id] = object_image
        else:
            # Update Objects
            canvas.coords(
                self.tkinter_id, 
                int(zoom / 100 * ((self.x + (self.y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x) + self.x_offset), 
                int(zoom / 100 * (self.y * CONSTANTS.TILE_HEIGHT + screen_y)) + self.y_offset)
            # zoom images
            if (mode == "zoom screen"):
                object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
                canvas.itemconfig(self.tkinter_id, image=object_image)
                # prevent image from being garbage collected
                # TODO - Currently should just use self, if they are all individual images
                image_list[self.tkinter_id] = object_image

    # TODO - currently image will not go away on deletion of object but can't use __del__ since object does not know canvas
    # Deleting image from canvas before delting the object works but a better longterm solution would be preffered  
    def clear_image(self, canvas):
        canvas.delete(self.tkinter_id)