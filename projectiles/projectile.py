from tkinter import *
from PIL import Image, ImageTk

import constants
import drawable_object

class Projectile(drawable_object.Drawable_Object):
    def __init__(self, x, y, tag, target):
        super().__init__(x, y, tag, 50, 50, "O.png")
        self.target = target
        self.lifetime = 500
    
    def update_self(self):
        if (self.lifetime <= 0):
            return "Timeout" 
        else:
            self.lifetime -= 1

            
            #update position
            speed = 5

            target_x = ((self.target.x + (self.target.y % 2)/2) * constants.TILE_WIDTH) #- self.target.width/2
            target_y =  (self.target.y * constants.TILE_HEIGHT) - self.target.height/2
            #move in x
            if (target_x > self.x + speed):
                self.x += speed
            elif (target_x < self.x - speed):
                self.x -= speed
            else:
                self.x = target_x
            #move in y
            if (target_y > self.y + speed):
                self.y += speed
            elif (target_y < self.y - speed):
                self.y -= speed
            else:
                self.y = target_y

    #Override draw_self from drawable_object
    def draw_self(self, zoom, screen_x, screen_y, canvas, mode, image_list):
        if (self.tkinter_id == None):
            #This is a new object that needs to get added
            #Note that x and y are in pixels not tiles
            object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
            self.tkinter_id = canvas.create_image(
                    int(zoom / 100 * (self.x + screen_x)), 
                    int(zoom / 100 * (self.y + screen_y)), 
                    image=object_image, 
                    anchor="center",
                    tag=self.tag)
            #prevent image from being garbage collected
            image_list[self.tkinter_id] = object_image
        else:
            #Update Objects
            canvas.coords(
                self.tkinter_id, 
                int(zoom / 100 * (self.x + screen_x)), 
                int(zoom / 100 * (self.y + screen_y)))
            #zoom images
            if (mode == "zoom screen"):
                object_image = ImageTk.PhotoImage(Image.open(self.image_file).resize((int(zoom / 100 * self.width), int(zoom / 100 * self.height))))
                canvas.itemconfig(self.tkinter_id, image=object_image)
                #prevent image from being garbage collected
                image_list[self.tkinter_id] = object_image