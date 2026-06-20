import drawable_object
from tkinter import *
from PIL import Image, ImageTk

class Menu_Screen(drawable_object.Drawable_Object):
    #tile_x: int, tile_y: int, key: str, tag: str, width: int, height: int, image_file: str, drawable_type = 0):
    def __init__(self, x:int, y: int, width: int, height: int, color: str, text: str = "", image_file: str = ""):
        super().__init__(x, y, "", "menu", width, height, color, drawable_type = 1)
        if (image_file != ""):
            self.my_images.append(drawable_object.Drawable_Image(0, 0, 100, 100, image_file))
        if (text != ""):
            self.my_images.append(drawable_object.Drawable_Image(0, 0, 100, 100, text, drawable_type = 2))
    
    # Override  draw as menu should be unbound to grid, and also not resize like non GUI components
    # Add object to given canvas - currenlty do not need to update since no animated menu items
    def draw_self(self, zoom: int, screen_x: int, screen_y: int, canvas: Canvas, mode: str, tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        for image in self.my_images:
            if (image.tkinter_id == None):
                # This is a new object that needs to get added

                if (image.type == 0):
                    # Create a normal image
                    if (tkinter_image_list.get(image.image_file) == None):
                        # Add image to list if this is the first time we are doing this image
                        # (Image, Original Width, Original Height)
                        tkinter_image_list[image.image_file] = (ImageTk.PhotoImage(Image.open(image.image_file).resize( (zoom / 100 * image.width, zoom / 100 * image.height) )), image.width, image.height)
                        
                    image.tkinter_id = canvas.create_image(
                            self.tile_x + image.x_offset,
                            self.tile_y + image.y_offset,
                            image = tkinter_image_list[image.image_file][0], 
                            anchor = "s", #"center",
                            tags = self.tag)
                elif (image.type == 1):
                    x = self.tile_x
                    y = self.tile_y
                            
                    image.tkinter_id = canvas.create_rectangle(
                        int(x - image.width/2),
                        int(y - image.height/2),
                        int(x + image.width/2), 
                        int(y + image.height/2), 
                        fill = image.image_file,
                        tags = self.tag)
                else:
                    image.tkinter_id = canvas.create_text(
                            self.tile_x + image.x_offset,
                            self.tile_y + image.y_offset,
                            text = image.image_file,
                            tags = self.tag)
            else:
                # Update Objects (or not since no animaiton)
                pass

    # Menu will need a way to be clicked on, this might not be how I want to finally implement that though
    def handle_click():
        pass