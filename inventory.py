import drawable_object
import menu_screen
from item import Item


class Inventory(menu_screen.Menu_Screen):
    def __init__(
            self,
            cols: int,
            rows: int,
            x: int = 0,
            y: int = 0,
            color: str = "gray",
            slot_size: int = 50):
        panel_width = cols * slot_size
        panel_height = rows * slot_size
        super().__init__(x, y, panel_width, panel_height, color)

        self.cols = cols
        self.rows = rows
        self.slot_size = slot_size
        self.items: list[Item | None] = [None] * (cols * rows)
        self.items[0] = Item()
        self.selected_index: int | None = None
        # Background + gray_box slots; item icons appended after this index
        self._slot_image_end = 1 + cols * rows

        for i in range(cols * rows):
            x_offset, y_offset = self._slot_offset(i)
            self.my_images.append(
                drawable_object.Drawable_Image(
                    x_offset, y_offset, slot_size, slot_size, "gray_box.png"))

        self._refresh_item_images()
        # Unbound so GUI can call handle_click(self=screen, click_x=..., click_y=...)
        self.handle_click = Inventory.handle_click

    def _slot_offset(self, index: int) -> tuple[int, int]:
        col = index % self.cols
        row = index // self.cols
        x_offset = int((col - (self.cols - 1) / 2) * self.slot_size)
        y_offset = int((row - (self.rows - 1) / 2) * self.slot_size)
        return x_offset, y_offset

    def _slot_index(self, click_x: int, click_y: int) -> int | None:
        half_w = self.my_images[0].width / 2
        half_h = self.my_images[0].height / 2
        if not (
            self.tile_x - half_w <= click_x <= self.tile_x + half_w
            and self.tile_y - half_h <= click_y <= self.tile_y + half_h
        ):
            return None

        local_x = click_x - (self.tile_x - half_w)
        local_y = click_y - (self.tile_y - half_h)
        col = int(local_x // self.slot_size)
        row = int(local_y // self.slot_size)
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return None
        return row * self.cols + col

    def _refresh_item_images(self):
        # Keep background + gray boxes; rebuild item icon layers
        self.my_images = self.my_images[: self._slot_image_end]
        for i, item in enumerate(self.items):
            if item is not None:
                x_offset, y_offset = self._slot_offset(i)
                self.my_images.append(item.get_display_image(x_offset, y_offset))

    def add_item(self, item: Item, index: int | None = None) -> bool:
        if index is None:
            try:
                index = self.items.index(None)
            except ValueError:
                return False
        if index < 0 or index >= len(self.items) or self.items[index] is not None:
            return False
        self.items[index] = item
        self._refresh_item_images()
        return True

    def handle_click(self, click_x: int, click_y: int) -> bool:
        index = self._slot_index(click_x, click_y)
        if index is None:
            return False

        if self.selected_index is None:
            if self.items[index] is not None:
                self.selected_index = index
        elif self.selected_index == index:
            self.selected_index = None
        else:
            # Move into empty slot or swap with occupied slot
            self.items[self.selected_index], self.items[index] = (
                self.items[index],
                self.items[self.selected_index],
            )
            self.selected_index = None
            self._refresh_item_images()

        return True
