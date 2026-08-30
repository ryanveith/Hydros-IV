from PIL import Image, ImageTk, ImageColor


def get_shadow_cache_key(base_path: str, color: str | None) -> str:
    if color is None:
        return base_path
    return f"{base_path}::{color}"


def load_tinted_shadow(base_path: str, color: str | None, width: int, height: int, zoom: int) -> ImageTk.PhotoImage:
    img = Image.open(base_path).convert("RGBA")
    if color is not None:
        r, g, b = ImageColor.getcolor(color, "RGB")
        pixels = []
        for pixel in img.getdata():
            if pixel[3] > 0:
                pixels.append((r, g, b, pixel[3]))
            else:
                pixels.append(pixel)
        img.putdata(pixels)
    resized = img.resize((int(zoom / 100 * width), int(zoom / 100 * height)))
    return ImageTk.PhotoImage(resized)
