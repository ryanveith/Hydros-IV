from tkinter import *
from PIL import Image, ImageTk

import utility.constants as CONSTANTS

class Drawable_Image:
    def __init__(self, x_offset: int, y_offset: int, width: int, height: int, image_file:str, image: None | Image = None, drawable_type = 0):
        self.type = drawable_type

        # Statistics for the image in pixels
        self.x_offset: int = x_offset
        self.y_offset: int = y_offset
        self.width: int = width
        self.height: int = height

        self.pillow_image: None | Image = image
        # Location of image file in images/ directory
        if (self.type == 0):
            self.image_file: str = "images/"+image_file
        else:
            self.image_file: str = image_file
        # Tkinter_id of image displayed on canvas (once added)
        self.tkinter_id: None | int = None

class Drawable_Object():
    def __init__(self, tile_x: int, tile_y: int, key: str, tag: str, width: int, height: int, image_file: str, drawable_type = 0):
        # There should always be 1 image in the list at 0, 0 with correct width and height so other images can be based of those values 
        self.my_images = [Drawable_Image(0, 0, width, height, image_file, drawable_type=drawable_type)]
        
    
        # Key for finding this object in the dict that represents world (none is not in world)
        self.key: None |str = key
        self.tag: str = tag
        
        # Tile cordinates
        self.tile_x: int = tile_x
        self.tile_y: int = tile_y
        # Pixel offset from tile coordinates
        self.x_offset: int = 0
        self.y_offset: int = 0

    # By default update self should do nothing
    def update_self(self, world_controller):
        return None

    # Add object to given canvas, otherwise update canvas with objects current positon relative to the screen's position
    # TODO - mode is ignored because we have to redraw everything anyways so ignore it
    def draw_self(self, zoom: int, screen_x: int, screen_y: int, canvas: Canvas, mode: str, tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        for image in self.my_images:
            if (image.tkinter_id == None):
                # This is a new object that needs to get added

                if (image.type == 0):
                    # Create a normal image
                    if (tkinter_image_list.get(image.image_file) == None):
                        # Add image to list if this is the first time we are doing this image
                        # (Image, Original Width, Original Height)
                        tkinter_image_list[image.image_file] = (ImageTk.PhotoImage(Image.open(image.image_file).resize( (int(zoom / 100 * image.width), int(zoom / 100 * image.height)) )), image.width, image.height)
                        
                    image.tkinter_id = canvas.create_image(
                            int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset)), 
                            int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset)), 
                            image = tkinter_image_list[image.image_file][0], 
                            anchor = "s", #"center",
                            tags = self.tag)
                elif (image.type == 1):
                    x = int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset))
                    y = int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset))
                            
                    image.tkinter_id = canvas.create_rectangle(
                        int(x - image.width/2),
                        int(y - image.height/2),
                        int(x + image.width/2), 
                        int(y + image.height/2), 
                        fill = image.image_file,
                        tags = self.tag)
                else:
                    image.tkinter_id = canvas.create_text(
                            int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset)), 
                            int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset)), 
                            text = image.image_file,
                            tags = self.tag)
                    #x = int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset))
                    #y = int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset))
                            
                    #image.tkinter_id = canvas.create_text(
                    #    int(x - image.width/2),
                    #    int(y - image.height/2),
                    #    int(x + image.width/2), 
                    #    int(y + image.height/2), 
                    #    fill = image.image_file,
                    #    tags = self.tag)

            else:
                # Update Objects
                if (image.type == 1):
                    #updating rectangles
                    x = int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset))
                    y = int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset))
                    canvas.coords(
                        image.tkinter_id, 
                        int(x - image.width/2),
                        int(y - image.height/2),
                        int(x + image.width/2),
                        int(y + image.height/2)
                    ) 
                else:
                    canvas.coords(
                        image.tkinter_id, 
                        int(zoom / 100 * ((self.tile_x + (self.tile_y % 2)/2) * CONSTANTS.TILE_WIDTH + screen_x + self.x_offset + image.x_offset)), 
                        int(zoom / 100 * (self.tile_y * CONSTANTS.TILE_HEIGHT + screen_y + self.y_offset + image.y_offset)))
                    # zoom images
                    if (image.type == 0 and mode == "zoom screen"):
                        canvas.itemconfig(image.tkinter_id, image = tkinter_image_list[image.image_file][0])
    
                        

    # TODO - currently image will not go away on deletion of object but can't use __del__ since object does not know canvas
    # Deleting image from canvas before delting the object works but a better longterm solution would be preffered  
    def clear_image(self, canvas):
        #This should only get called when no loger a part of the world, so also indicate that this is not being shown on the world
        self.key = None
        for image in self.my_images:
            canvas.delete(image.tkinter_id)