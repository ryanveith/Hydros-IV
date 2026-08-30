from buildings.building import Building
from menus.storage_menu import Storage_Menu


class Storage_Box(Building):
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
        self.storage = Storage_Menu(3, 3)
