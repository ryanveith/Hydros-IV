import drawable_object
import constants

class Square(drawable_object.Drawable_Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Static Terrain", constants.TILE_WIDTH,  constants.TILE_HEIGHT, "diamond.png")
        self.world = "Hydros"        
        self.terrain="ground"
        self.occupied=None