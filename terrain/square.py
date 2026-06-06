import drawable_object
import utility.constants as CONSTANTS

class Square(drawable_object.Drawable_Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Static Terrain", CONSTANTS.TILE_WIDTH,  CONSTANTS.TILE_HEIGHT, "diamond.png")
        self.world = "Hydros"        
        self.terrain= "ground"
        self.occupied= None