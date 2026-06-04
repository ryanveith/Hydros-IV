from tkinter import *
from PIL import Image, ImageTk

import constants

class Drawable_Object():
    def __init__(self, x, y, tag, width, height, image_file):
        self.tkinter_id = None
        self.tag = tag
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image_file="images/"+image_file

    def update_self(self):
        pass

    def draw_self(self, zoom, screen_x, screen_y, canvas, mode, image_list):
        if (self.tkinter_id == None):
            #save canvas

            #This is a new object that needs to get added
            object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
            self.tkinter_id = canvas.create_image(
                    int(zoom / 100 * ((self.x + (self.y % 2)/2) * constants.TILE_WIDTH + screen_x)), 
                    int(zoom / 100 * (self.y * constants.TILE_HEIGHT + screen_y)), 
                    image=object_image, 
                    anchor="s", #"center",
                    tag=self.tag)
            #prevent image from being garbage collected
            image_list[self.tkinter_id] = object_image
        else:
            #Update Objects
            canvas.coords(
                self.tkinter_id, 
                int(zoom / 100 * ((self.x + (self.y % 2)/2) * constants.TILE_WIDTH + screen_x)), 
                int(zoom / 100 * (self.y * constants.TILE_HEIGHT + screen_y)))
            #zoom images
            if (mode == "zoom screen"):
                object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
                canvas.itemconfig(self.tkinter_id, image=object_image)
                #prevent image from being garbage collected
                image_list[self.tkinter_id] = object_image

    def clear_image(self, canvas):
        canvas.delete(self.tkinter_id)