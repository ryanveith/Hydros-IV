import drawable_object
import utility.constants as CONSTANTS
from units.unit import Unit


class Humanoid(Unit):
    SPRITE_SIZE = 100
    HAIR_X_OFFSET = 0
    HAIR_Y_OFFSET = -5

    def __init__(
        self,
        tile_x: int,
        tile_y: int,
        key: str,
        tag: str,
        image: str | None = None,
        gender: str = "male",
        variation: int = 1,
        hairstyle: int = 1,
    ):
        self.gender = gender
        self.variation = variation
        self.hairstyle = hairstyle

        body_path = image if image is not None else f"humanoids/{gender}_{variation}.png"
        hairstyle_path = f"humanoids/hairstyles/{hairstyle}.png"

        super().__init__(
            tile_x, tile_y, key, tag,
            image_file=body_path,
            width=self.SPRITE_SIZE,
            height=self.SPRITE_SIZE,
        )

        body_y_offset = -int(CONSTANTS.TILE_HEIGHT / 2)
        sprite = self.my_images[1]
        sprite.y_offset = body_y_offset
        self.my_images[2].y_offset += body_y_offset
        self.my_images[3].y_offset += body_y_offset
        self.my_images[4].y_offset += body_y_offset

        self.my_images.insert(4, drawable_object.Drawable_Image(
            self.HAIR_X_OFFSET,
            body_y_offset + self.HAIR_Y_OFFSET,
            sprite.width,
            sprite.height,
            hairstyle_path,
        ))
