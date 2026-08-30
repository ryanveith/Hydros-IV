import drawable_object


class Building(drawable_object.Drawable_Object):
    def __init__(
            self,
            tile_x: int,
            tile_y: int,
            key: str,
            tag: str,
            x_width: int = 50,
            y_height: int = 50,
            image: str = "placeholder.png"):
        super().__init__(tile_x, tile_y, key, tag, x_width, y_height, image)
