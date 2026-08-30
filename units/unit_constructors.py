from units.humanoid import Humanoid


def create_humanoid(
    tile_x: int,
    tile_y: int,
    name: str,
    image: str | None = None,
    gender: str = "male",
    variation: int = 1,
    hairstyle: int = 1,
):
    return Humanoid(
        tile_x, tile_y, name, name,
        image=image,
        gender=gender,
        variation=variation,
        hairstyle=hairstyle,
    )
