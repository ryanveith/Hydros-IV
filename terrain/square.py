import drawable_object

class Square(drawable_object.Drawable_Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Static Terrain", "diamond.png")
        self.world = "Hydros"        
        self.terrain="ground"
        self.occupied=None