import drawable_object

class Unit(drawable_object.Drawable_Object):
    def __init__(self, x, y, tag):
        super().__init__(x, y, tag, 100, 100, "elfling.png")