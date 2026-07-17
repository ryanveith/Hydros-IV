import drawable_object
from tkinter import *
from PIL import Image, ImageTk

class Menu_Screen(drawable_object.Drawable_Object):
    #tile_x: int, tile_y: int, key: str, tag: str, width: int, height: int, image_file: str, drawable_type = 0):
    def __init__(
            self, x:int, y: int, width: int, height: int, 
            color: str, text: str = "", image_file: str = "", 
            handle_click = lambda self, click_x, click_y: False):
        
        super().__init__(x, y, "", "menu", width, height, color, drawable_type = 1)
        self.handle_click = handle_click
    
        if (image_file != ""):
            self.my_images.append(drawable_object.Drawable_Image(0, 0, 100, 100, image_file))
        if (text != ""):
            self.my_images.append(drawable_object.Drawable_Image(0, 0, 100, 100, text, drawable_type = 2))

    def _get_menu_photo(self, image: drawable_object.Drawable_Image) -> ImageTk.PhotoImage:
        # Screen-space menus must keep a stable PhotoImage. The shared world cache is
        # replaced every few ticks on "zoom screen", which GCs any canvas ref that isn't updated.
        if getattr(image, "_menu_photo", None) is None:
            image._menu_photo = ImageTk.PhotoImage(
                Image.open(image.image_file).resize((image.width, image.height)))
        return image._menu_photo
    
    # Override  draw as menu should be unbound to grid, and also not resize like non GUI components
    # Add object to given canvas - currenlty do not need to update since no animated menu items
    def draw_self(self, zoom: int, screen_x: int, screen_y: int, canvas: Canvas, mode: str, tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        for image in self.my_images:
            if (image.tkinter_id == None):
                # This is a new object that needs to get added

                if (image.type == 0):
                    # Create a normal image (stable photo, centered to match type-1 background)
                    photo = self._get_menu_photo(image)
                    image.tkinter_id = canvas.create_image(
                            self.tile_x + image.x_offset,
                            self.tile_y + image.y_offset,
                            image = photo, 
                            anchor = "center",
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
                # Keep menu images bound to stable PhotoImage across world zoom cache rebuilds
                if (image.type == 0):
                    photo = self._get_menu_photo(image)
                    canvas.itemconfig(image.tkinter_id, image=photo)
                    canvas.coords(
                        image.tkinter_id,
                        self.tile_x + image.x_offset,
                        self.tile_y + image.y_offset)
