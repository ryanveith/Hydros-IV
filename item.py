import drawable_object
import utility.constants as CONSTANTS


class Item(drawable_object.Drawable_Object):
    def __init__(self, item_width: int = CONSTANTS.TILE_HEIGHT, item_height: int = CONSTANTS.TILE_HEIGHT, image_file: str = "O.png", name: str = ""):
        super().__init__(0, 0, name, "item", item_width, item_height, image_file)
        self.item_width = item_width
        self.item_height = item_height

    def get_display_image(self, x_offset: int, y_offset: int) -> drawable_object.Drawable_Image:
        """Build a new Drawable_Image for inventory display at the given slot offsets."""
        source = self.my_images[0]
        image_file = source.image_file
        if source.type == 0 and image_file.startswith("images/"):
            image_file = image_file[len("images/"):]
        return drawable_object.Drawable_Image(
            x_offset,
            y_offset,
            source.width,
            source.height,
            image_file,
            image = source.pillow_image,
            drawable_type = source.type,
        )
