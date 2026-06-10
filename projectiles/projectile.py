import math
from tkinter import *
from PIL import Image, ImageTk

import utility.constants as CONSTANTS
import utility.action_variables as ACTIONS
import drawable_object

class Projectile(drawable_object.Drawable_Object):
    def __init__(self, tile_x: int, tile_y: int, key: str, tag: str, target: drawable_object.Drawable_Object):
        #TODO - Tile_x is misleading since projectiles are not bound to tile system so it is in pixels, but shoudl not loose anythign from drawable so...
        super().__init__(tile_x, tile_y, key, tag, 50, 50, "O.png")
        self.target: drawable_object.Drawable_Object = target
        self.lifetime: int = 500
        
        self.speed: int = 10
        self.damage: int = 10
    
    def update_self(self, world_logic):
        if (self.lifetime <= 0):
            # TODO - add handling for a projectile timing out
            # Currently it is just deleted from world, and so there is no image to draw since it is self.image for projectiles
            return (ACTIONS.TIMEOUT, "")
        else:
            self.lifetime -= 1

            # Update position
            target_x: int = ((self.target.tile_x + (self.target.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH)
            target_y: int =  (self.target.tile_y * CONSTANTS.TILE_HEIGHT) - self.target.my_images[0].height/2
            
            # Data for preventing overshooting target
            if (self.tile_x < target_x):
                smaller_x = True
            else:
                smaller_x = False
            # Do not currenlty need to check x since we are facing desination perfectly so if we overshoot one we have arrived
            # if (self.y < target_y):
            #    smaller_y = True
            # else:
            #    smaller_y = True

            # By default projectiles directly twoards the target
            angle = math.atan2(target_y - self.tile_y, target_x - self.tile_x)

            change_x = self.speed * math.cos(angle)
            change_y = self.speed * math.sin(angle)

            self.tile_x += change_x
            self.tile_y += change_y

            # TODO - decide if this should use targets offset at all and if it should do collison here
            if (smaller_x and self.tile_x >= target_x):
                self.tile_x = target_x
                self.tile_y = target_y
                return (ACTIONS.COLLISION, self.key)
            elif ((not smaller_x) and self.tile_x <= target_x):
                self.tile_x = target_x
                self.tile_y = target_y
                return (ACTIONS.COLLISION, self.key)

    # Override draw_self from drawable_object
    # This is needed since this does not stay on the grid system or have a grid space but rather measure xy in pixels
    def draw_self(self, zoom, screen_x, screen_y, canvas, mode, tkinter_image_list):
        for image in self.my_images:
            if (image.tkinter_id == None):
                # This is a new object that needs to get added
                # Note that x and y are in pixels not tiles
                if (tkinter_image_list.get(image.image_file) == None):
                    # (Image, Original Width, Original Height)
                    tkinter_image_list[image.image_file] = (ImageTk.PhotoImage(Image.open(image.image_file).resize( (int(zoom / 100 * image.width), int(zoom / 100 * image.height)) )), image.width, image.height)
                
                image.tkinter_id = canvas.create_image(
                        int(zoom / 100 * (self.tile_x + screen_x + image.x_offset)), 
                        int(zoom / 100 * (self.tile_y + screen_y + image.y_offset)), 
                        image = tkinter_image_list[image.image_file][0], 
                        anchor = "center",
                        tag = self.tag)
            else:
                # Update Existing Objects
                canvas.coords(
                    image.tkinter_id, 
                    int(zoom / 100 * (self.tile_x + screen_x)), 
                    int(zoom / 100 * (self.tile_y + screen_y)))
                # Zoom images
                if (mode == "zoom screen"):
                    canvas.itemconfig(image.tkinter_id, image = tkinter_image_list[image.image_file][0])
                