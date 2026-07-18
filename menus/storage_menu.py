import drawable_object
import menus.menu_screen as menu_screen
from items.item import Item
import items.item_constructors

import math

class Storage_Menu(menu_screen.Menu_Screen):
    def __init__(
            self,
            cols: int,
            rows: int,
            x: int = 0,
            y: int = 0,
            color: str = "dark slate gray",
            slot_size: int = 50):
        self.selected_item: Item | None = None
        self.selected_index: int | None = None

        self.cols = cols
        self.rows = rows
        panel_width = cols * slot_size + 10
        panel_height = rows * slot_size + 10
        super().__init__(x, y, panel_width, panel_height, color)

        self.cols = cols
        self.rows = rows
        self.slot_size = slot_size
        self.items: list[Item | None] = [None] * (cols * rows)
        # self.items[0] = items.item_constructors.create_item_pebble()
        self.selected_index: int | None = None
        # Background + gray_box slots; item icons appended after this index
        self._slot_image_end = 1 + cols * rows

        for i in range(cols * rows):
            x_offset, y_offset = self._slot_offset(i)
            self.my_images.append(
                drawable_object.Drawable_Image(
                    x_offset, y_offset, slot_size, slot_size, "inventory/inventory_slot_32.png"))

        self._refresh_item_images()
        # Unbound so GUI can call handle_click(self=screen, click_x=..., click_y=...)
        self.handle_click = Storage_Menu.handle_click

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
        i: int
        item: Item
        for i, item in enumerate(self.items):
            if item is not None:
                x_offset, y_offset = self._slot_offset(i)
                self.my_images.append(item.get_display_image(x_offset, y_offset))

    def _item_fits_in_slot(self,  item_width: int, item_height: int, slot_index: int):
        print("test ", item_width, item_height, slot_index)
        index_row = int(slot_index / self.rows)
        index_col = slot_index % self.rows
        print("slot: "+str(slot_index)+" row: "+str(index_row)+" col: "+str(index_col))
        for row in range(item_width):
            for col in range(item_height):
                print("make it here")
                slot = slot_index + row * self.rows + col
                print("slot: ", int(slot))
                print("good?", row + index_row > self.rows, col + index_col > self.cols)
                if (
                    row + index_row > self.rows or
                    col + index_col > self.cols or
                    self.items[slot] != None):
                    return False
        return True
    
    def _set_slot_to_item(self,  item_width: int, item_height: int, slot_index: int, item: Item | None):
        for row in range(item_width):
            for col in range(item_height):
                self.items[slot_index + row * self.rows + col] = item

    def add_item(self, item: Item, index: int | None = None) -> bool:
        if index is None:
            for slot_index, slot in enumerate(self.items):
                if (slot == None):
                    #if (item.item_width == 1 and item.item_height == 1):
                    #    self.items[slot] = item
                    #    self._refresh_item_images()
                    #    return True
                    item_fits = self._item_fits_in_slot(item_width = item.item_slot_width, item_height = item.item_slot_height, slot_index = slot_index)
                    if (item_fits):
                        #self.items[slot_index] = item
                        self._set_slot_to_item(item_width = item.item_slot_width, item_height = item.item_slot_height, slot_index = slot_index, item = item)
                        self._refresh_item_images()
                        return True
            return False
            #try:
            #    index = self.items.index(None)
            #except ValueError:
            #    return False
        if index < 0 or index >= len(self.items) or self._item_fits_in_slot(
            item_width = item.item_slot_width, 
            item_height = item.item_slot_height,
            slot_index = index) is not None:
            # Only the index < 0 check should be needed since item fits in slot can handle overflow
            # TODO make item fits in slot funciton handle all invalid input by returning false
            return False
        # Add item there
        #self.items[index] = item
        self._set_slot_to_item(
            item_width = item.item_slot_width, 
            item_height = item.item_slot_height,
            slot_index = index,
            item = item
        )
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
        self.items[index] = None
        if self.selected_index == index:
            self.selected_index = None
        self._refresh_item_images()
        return item

    def handle_click(self, click_x: int, click_y: int) -> bool:
        # If not withing inventory clear selection and return
        index = self._slot_index(click_x, click_y)
        if index is None:
            # TODO "put" item back so you can have item follow mouse and not actually be in a spot while moving
            self.selected_item = None
            self.selected_index = None
            return False

        print("here")
        if (self.selected_item is None or self.selected_index is None):
            print("selecting", self.selected_item, self.selected_index)
            if self.items[index] is not None:
                self.selected_index = index
                self.selected_item = self.items[index]
                print("selected")

        elif self.selected_index == index:
            # TODO, this is a temproary case that will become a normal put item there once you can actualy pick up item temporaily
            self.selected_index = None
            self.selected_item = self.items[index]

        else:
            print("test +++ ",self.selected_item.item_slot_width, self.selected_item.item_slot_height)
            if self._item_fits_in_slot(
                    item_width = self.selected_item.item_slot_width, 
                    item_height = self.selected_item.item_slot_height,
                    slot_index = index):
                # Clear old spot
                self._set_slot_to_item(
                    item_width = self.selected_item.item_slot_width, 
                    item_height = self.selected_item.item_slot_height,
                    slot_index = self.selected_index,
                    item = None)
                # Put in new spot
                self._set_slot_to_item(
                    item_width = self.selected_item.item_slot_width, 
                    item_height = self.selected_item.item_slot_height,
                    slot_index = index,
                    item = self.selected_item)
                # Clear selected Item
                self.selected_index = None
                self.slected_item = None
            else:
                # Currently do not have the logic to figure out if a another item is big enough to swap with 
                # TODO, implement that
                pass
        
        #else:
        #    # Move into empty slot or swap with occupied slot
        #    self.items[self.selected_index], self.items[index] = (
        #        self.items[index],
        #        self.items[self.selected_index],
        #    )
        #    self.selected_index = None
        
        self._refresh_item_images()
        return True
