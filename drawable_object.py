class Drawable_Object():
    def __init__(self, x, y, tag, image_file):
        self.tkinter_id = None
        self.tag = tag
        self.x = x
        self.y = y
        self.image_file="images/"+image_file