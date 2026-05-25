class Square():
    def __init__(self, x, y):
        self.world = "Hydros"
        self.x = x
        self.y = y
        self.terrain="ground"
        self.image_file="images/"+"gray_box.png"
        self.occupied=None