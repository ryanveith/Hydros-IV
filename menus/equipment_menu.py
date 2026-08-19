import drawable_object
import menus.menu_screen as menu_screen
from items.item import Item

from tkinter import *
from PIL import Image, ImageTk

_PLACEHOLDER_SLOT = "inventory/inventory_slot_32.png"
_BLUE_SLOT = "images/inventory/blue_inventory_slot_32.png"
_LEFT_HAND_SLOT = "inventory/hand_slot_32-left.png"


class Equipment_Menu(menu_screen.Menu_Screen):
    """Paper-doll equipment menu with named 1-item slots and type filtering."""

    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            color: str = "dark slate gray",
            slot_size: int = 50,
            backpack=None,
            necklace=None,
            ring=None,
            bracer=None):

        # Slot defs: (name, allowed_type, col, row, image_path_or_None, flip_horizontal)
        # Layout:
        # [backpack] [helm]  [necklace]
        # [handL]    [chest] [handR]
        # [bracer]   [legs]  [ring]
        #            [feet]
        slot_defs = [
            ("helm", "helm", 1, 0, "inventory/helm_slot_32.png", False),
            ("chest", "chest", 1, 1, "inventory/chest_slot_32.png", False),
            ("legs", "legs", 1, 2, "inventory/legs_slot_32.png", False),
            ("feet", "feet", 1, 3, "inventory/feet_slot_32.png", False),
            ("hand_left", "hand", 0, 1, _LEFT_HAND_SLOT, False),
            ("hand_right", "hand", 2, 1, _LEFT_HAND_SLOT, True),
        ]

        optional = [
            ("backpack", "backpack", 0, 0, backpack),
            ("necklace", "necklace", 2, 0, necklace),
            ("bracer", "bracer", 0, 2, bracer),
            ("ring", "ring", 2, 2, ring),
        ]
        for name, allowed, col, row, opt in optional:
            if opt is None:
                continue
            image_path = opt if isinstance(opt, str) else _PLACEHOLDER_SLOT
            slot_defs.append((name, allowed, col, row, image_path, False))

        # Sort by row then col so image indices stay stable and hit-testing is predictable
        slot_defs.sort(key=lambda s: (s[3], s[2]))

        max_col = max(s[2] for s in slot_defs)
        max_row = max(s[3] for s in slot_defs)
        self.num_cols = max_col + 1
        self.num_rows = max_row + 1

        panel_width = self.num_cols * slot_size + 10
        panel_height = self.num_rows * slot_size + 10
        super().__init__(x, y, panel_width, panel_height, color)

        self.selected_item: Item | None = None
        self.selected_index: int | None = None
        self.slot_size = slot_size

        # Active slot metadata parallel to self.items
        self.slots: list[dict] = []
        self.items: list[Item | None] = []
        # Cached PhotoImages for restoring slot art after selection highlight
        self._slot_photos: list[ImageTk.PhotoImage] = []

        for name, allowed, col, row, image_path, flip in slot_defs:
            self.slots.append({
                "name": name,
                "allowed_type": allowed,
                "col": col,
                "row": row,
                "image_path": image_path,
                "flipped": flip,
            })
            self.items.append(None)

        self._slot_image_end = 1 + len(self.slots)

        for i, slot in enumerate(self.slots):
            x_offset, y_offset = self._slot_offset(i)
            drawable = drawable_object.Drawable_Image(
                x_offset, y_offset, slot_size, slot_size, slot["image_path"])
            photo = self._make_slot_photo(slot)
            drawable._menu_photo = photo
            self._slot_photos.append(photo)
            self.my_images.append(drawable)

        self._refresh_item_images()
        self.handle_click = Equipment_Menu.handle_click

    def _make_slot_photo(self, slot: dict) -> ImageTk.PhotoImage:
        path = slot["image_path"]
        if not path.startswith("images/"):
            path = "images/" + path
        img = Image.open(path).resize((self.slot_size, self.slot_size))
        if slot["flipped"]:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return ImageTk.PhotoImage(img)

    def _slot_offset(self, index: int) -> tuple[int, int]:
        slot = self.slots[index]
        col = slot["col"]
        row = slot["row"]
        x_offset = int((col - (self.num_cols - 1) / 2) * self.slot_size)
        y_offset = int((row - (self.num_rows - 1) / 2) * self.slot_size)
        return x_offset, y_offset

    def _click_in_panel(self, click_x: int, click_y: int) -> bool:
        half_w = self.my_images[0].width / 2
        half_h = self.my_images[0].height / 2
        return (
            self.tile_x - half_w <= click_x <= self.tile_x + half_w
            and self.tile_y - half_h <= click_y <= self.tile_y + half_h
        )

    def _slot_index(self, click_x: int, click_y: int) -> int | None:
        """Return slot index for a click, or None if outside panel / empty grid cell."""
        if not self._click_in_panel(click_x, click_y):
            return None

        half_w = self.my_images[0].width / 2
        half_h = self.my_images[0].height / 2
        local_x = click_x - (self.tile_x - half_w)
        local_y = click_y - (self.tile_y - half_h)
        col = int(local_x // self.slot_size)
        row = int(local_y // self.slot_size)
        if col < 0 or col >= self.num_cols or row < 0 or row >= self.num_rows:
            return None

        for i, slot in enumerate(self.slots):
            if slot["col"] == col and slot["row"] == row:
                return i
        return None

    def _slot_accepts(self, item: Item, index: int) -> bool:
        if item is None or item.equipment_type is None:
            return False
        if index < 0 or index >= len(self.slots):
            return False
        return self.slots[index]["allowed_type"] == item.equipment_type

    def _refresh_item_images(self):
        self.my_images = self.my_images[: self._slot_image_end]
        for i, item in enumerate(self.items):
            if item is not None:
                x_offset, y_offset = self._slot_offset(i)
                self.my_images.append(item.get_display_image(x_offset, y_offset))

    def _set_slot_photo(self, index: int, photo: ImageTk.PhotoImage):
        # Slot drawables are at my_images[1 .. len(slots)]
        self.my_images[index + 1]._menu_photo = photo

    def add_item(self, item: Item, index: int | None = None) -> bool:
        if index is None:
            for slot_index in range(len(self.items)):
                if self.items[slot_index] is None and self._slot_accepts(item, slot_index):
                    self.items[slot_index] = item
                    self._refresh_item_images()
                    return True
            return False

        if (
            index < 0
            or index >= len(self.items)
            or self.items[index] is not None
            or not self._slot_accepts(item, index)
        ):
            return False
        self.items[index] = item
        self._refresh_item_images()
        return True

    def remove_item(self, index: int | None = None) -> Item | None:
        if index is None:
            index = self.selected_index
        if index is None or index < 0 or index >= len(self.items):
            return None
        item = self.items[index]
        if item is None:
            return None
        if self.selected_item == item:
            self._select(None)
        self.items[index] = None
        self._refresh_item_images()
        return item

    def _select(self, index):
        if self.selected_index is not None:
            self._set_slot_photo(self.selected_index, self._slot_photos[self.selected_index])

        if index is None or self.items[index] is None:
            self.selected_index = None
            self.selected_item = None
            return

        self.selected_item = self.items[index]
        self.selected_index = index
        highlight = ImageTk.PhotoImage(
            Image.open(_BLUE_SLOT).resize((self.slot_size, self.slot_size)))
        # Keep a ref so Tk does not GC the highlight photo
        self._highlight_photo = highlight
        self._set_slot_photo(index, highlight)
        self._refresh_item_images()

    def handle_click(
            self,
            click_x: int,
            click_y: int,
            click_type="interact",
            incoming_item: Item | None = None
            ) -> tuple[bool, Item | None, int | None]:
        if not self._click_in_panel(click_x, click_y):
            return (False, self.selected_item, None)

        index = self._slot_index(click_x, click_y)
        # Click in panel but on a gap (no slot)
        if index is None:
            self._select(None)
            return (True, None, None)

        if self.selected_item is not None and self.selected_index is not None:
            if self.selected_index == index:
                self._select(None)
            else:
                dest_item = self.items[index]
                if dest_item is None:
                    if self._slot_accepts(self.selected_item, index):
                        self.items[self.selected_index] = None
                        self.items[index] = self.selected_item
                        self._select(index)
                    else:
                        self._select(None)
                else:
                    src = self.selected_index
                    if (
                        self._slot_accepts(self.selected_item, index)
                        and self._slot_accepts(dest_item, src)
                    ):
                        self.items[src], self.items[index] = self.items[index], self.items[src]
                        self._select(index)
                    else:
                        self._select(None)
            self._refresh_item_images()
            return (True, self.selected_item, None)

        if self.items[index] is not None:
            self._select(index)
            self._refresh_item_images()
            return (True, self.selected_item, None)

        if incoming_item is not None:
            return (True, None, index)

        return (True, None, None)
