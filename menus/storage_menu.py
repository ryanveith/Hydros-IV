import drawable_object
import menus.menu_screen as menu_screen
from items.item import Item
import items.item_constructors

from tkinter import *
from PIL import Image, ImageTk

# Storage menu is a menu that holds a grid of items different sizes
class Storage_Menu(menu_screen.Menu_Screen):
    def __init__(
                self,
                cols: int,
                rows: int,
                x: int = 0,
                y: int = 0,
                color: str = "dark slate gray",
                slot_size: int = 50):
    
        # Screen should be a bit bigger then slots
        panel_width = cols * slot_size + 10
        panel_height = rows * slot_size + 10
        super().__init__(x, y, panel_width, panel_height, color)

        # Keep track of selected item for moving items around
        self.selected_item: Item | None = None
        self.selected_index: int | None = None

        # Keep track of rows, cols for inventory management
        self.num_cols = cols
        self.num_rows = rows
        self.items: list[Item | None] = [None] * (cols * rows)
        
        # Pixel size for "boxs" or each inventory slot
        self.slot_size = slot_size
        
        # Background + gray_box slots; item icons appended after this index
        # This is because this is set up to ask for a new image when it thinks it needs a refresh 
        # So it just goes though all of them
        # 1 + is because slot 0 in self.images is the base box drawn for the menu
        self._slot_image_end = 1 + cols * rows

        # Create images for all inventory slots
        for i in range(cols * rows):
            x_offset, y_offset = self._slot_offset(i)
            self.my_images.append(
                drawable_object.Drawable_Image(
                    x_offset, y_offset, slot_size, slot_size, "inventory/inventory_slot_32.png"))

        self._refresh_item_images()
        
        # Override the passed in funciton for super with this classes version of handle_click
        # Unbound so GUI can call handle_click(self=screen, click_x=..., click_y=...)
        self.handle_click = Storage_Menu.handle_click

    # Given a index, return the x and y offset required for the drawable object that is that slot
    def _slot_offset(self, index: int, item_width: int = 1, item_height: int = 1) -> tuple[int, int]:
        col = index % self.num_cols
        row = index // self.num_cols
        x_offset = int((col - (self.num_cols - 1) / 2) * self.slot_size)
        y_offset = int((row - (self.num_rows - 1) / 2) * self.slot_size)
        # Modify offset based on item size to allow for bigger items
        x_offset = int(x_offset + self.slot_size * (item_width - 1)/2)
        y_offset = int(y_offset + self.slot_size * (item_height - 1)/2)
        return x_offset, y_offset

    # Given an x, y cordinate on the screen return the array location of that spot in inventory
    # If x, y is not in inventory return None
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
        if col < 0 or col >= self.num_cols or row < 0 or row >= self.num_rows:
            return None
        return row * self.num_cols + col

    # Remakes drawable objects representing items after the boxes
    # Will cause problems if there are non-item drawables that don't have get_display_image after self._slot_image_end in self.my_images
    def _refresh_item_images(self):
        # Keep background + gray boxes; rebuild item icon layers
        self.my_images = self.my_images[: self._slot_image_end]
        i: int
        item: Item
        for i, item in enumerate(self.items):
            if item is not None:
                part_of_row = (i - 1 >= 0 and self.items[i - 1] == item)
                part_of_col = (i - self.num_cols >= 0 and self.items[i - self.num_cols] == item)
                if ((not part_of_row) and (not part_of_col)):
                    x_offset, y_offset = self._slot_offset(i, item_width = item.item_slot_width, item_height = item.item_slot_height)
                    self.my_images.append(item.get_display_image(x_offset, y_offset))

    # Given a index in inventory and a width and height of slots to check from it return if all checked slots are empty
    def _item_fits_in_slot(self, item_width: int, item_height: int, slot_index: int):
        if (slot_index < 0):
            return False
        # Get row, col of slot from index in list
        index_row = int(slot_index / self.num_rows)
        index_col = slot_index % self.num_rows
        # Iterate though all slots that the item would take based on its size
        for row in range(item_width):
            for col in range(item_height):
                slot = slot_index + col * self.num_rows + row
                # Extra bounds checking since we seem to get list index out of range even if row and col are theoretically fine
                if (slot < 0 or slot >= len(self.items)):
                    return False
                # If that slot does not exist or is full it does not fit
                if (
                    row + index_row > self.num_rows or
                    col + index_col > self.num_cols or
                    self.items[slot] != None):
                    return False
        # All spots are open so item fits
        return True
    
    # Given a slot and item, add that item to teh slot, taking up as much spaces adjacent as it needs to fit
    # ONLY to be used after checking if space is open since it Will override other items
    def _set_slot_to_item(self, slot_index: int, item: Item | None):
        # TODO make this seciton to as repetative code wise
        if (item != None):
            for row in range(item.item_slot_width):
                for col in range(item.item_slot_height):
                    self.items[slot_index + col * self.num_rows + row] = item
        elif(self.items[slot_index] != None):
            item_to_remove = self.items[slot_index]
            for row in range(item_to_remove.item_slot_width):
                for col in range(item_to_remove.item_slot_height):
                    self.items[slot_index + col * self.num_rows + row] = item

    # Add item to inventory(storage_menu) at specified index
    # If index is None it will try and add the item in the first open slot where it fits
    # Returns true if it fit or false if it fails
    def add_item(self, item: Item, index: int | None = None) -> bool:
        if index is None:
            # Try and put item in first slot where it fits
            for slot_index, slot in enumerate(self.items):
                if (slot == None):
                    item_fits = self._item_fits_in_slot(item_width = item.item_slot_width, item_height = item.item_slot_height, slot_index = slot_index)
                    if (item_fits):
                        self._set_slot_to_item(slot_index = slot_index, item = item)
                        self._refresh_item_images()
                        return True
            # Item did not fit in any spot so return false to mark that this was unsucessfuls
            return False
        if index < 0 or index >= len(self.items) or self._item_fits_in_slot(
            item_width = item.item_slot_width, 
            item_height = item.item_slot_height,
            slot_index = index) is not None:
            # Only the index < 0 check should be needed since item fits in slot can handle overflow
            # TODO make item fits in slot funciton handle all invalid input by returning false
            return False
        # Add item to specified slot
        self._set_slot_to_item(slot_index = index, item = item)
        self._refresh_item_images()
        return True

    # Remove item at index from inventory, defaults to selected item
    # Use index at top left of item to remove them (this is automatically selected index)
    # Returns item removed or None if not item was removed
    def remove_item(self, index: int | None = None) -> Item | None:
        # Default item to remove if none are passed in is selected item
        if index is None:
            index = self.selected_index
        # If invalid index or nothing there, return none
        if index is None or index < 0 or index >= len(self.items):
            return None
        item = self.items[index]        
        if item is None:
            return None
        # If this is the selected item, unselect it
        if self.selected_item == item:
            self._select(None)
        # Remove item
        self._set_slot_to_item(slot_index = index, item = None)
        self._refresh_item_images()
        return item

    # Unselect the current selected item and select the item at given 
    # If index = None only unselects current item
    # This also modifies the pictures of inventory slots to mark which ones are under selected item
    # (and unmodifies them when unselecting previous)
    def _select(self, index):
        # If we had a previous selected remove "highlight"
        if (self.selected_index != None):
            for row in range(self.selected_item.item_slot_width):
                for col in range(self.selected_item.item_slot_height):
                    self.my_images[(self.selected_index + col * self.num_rows + row) + 1]._menu_photo = ImageTk.PhotoImage(Image.open("images/inventory/inventory_slot_32.png").resize((self.slot_size, self.slot_size)))
        # If no item selected return
        if (index == None or self.items[index] == None):
            self.selected_index = None
            self.selected_item = None
            return
        # Otherwise select new thing at index
        self.selected_item = self.items[index]
        # self.selected_index = index
        # When selecting an item make sure that top, left corner is selected
        for row in range(self.selected_item.item_slot_width):
            for col in range(self.selected_item.item_slot_height):
                if (index - col * self.num_rows - row >= 0 and self.items[index - col * self.num_rows - row] == self.selected_item):
                    self.selected_index = index - col * self.num_rows - row 
        
        # Highlight new selected
        for row in range(self.selected_item.item_slot_width):
                for col in range(self.selected_item.item_slot_height):
                    self.my_images[(self.selected_index + col * self.num_rows + row) + 1]._menu_photo = ImageTk.PhotoImage(Image.open("images/inventory/blue_inventory_slot_32.png").resize((self.slot_size, self.slot_size)))
        self._refresh_item_images()

    # Handle clicks within inventory, reutrns False if click was not in invenotry
    # Otherwise handle moving items around and whatnot
    def handle_click(self, click_x: int, click_y: int, click_type = "interact") -> bool:
        # If click not within inventory clear selection and return
        index = self._slot_index(click_x, click_y)
        if index is None:
            self._select(None)
            return False

        # Handle normal click

        # If no selected select clicked item
        if (self.selected_item is None or self.selected_index is None):
            if self.items[index] is not None:
                self._select(index)
        # If clicked selected item unselect
        elif self.selected_index == index:
            self._select(None)
        # Else move selected item to clicked spot if free
        else:
            # Check spot free
            if self._item_fits_in_slot(
                    item_width = self.selected_item.item_slot_width, 
                    item_height = self.selected_item.item_slot_height,
                    slot_index = index):
                # Clear item from old spot
                self._set_slot_to_item(slot_index = self.selected_index, item = None)
                # Put item in new spot
                self._set_slot_to_item(slot_index = index, item = self.selected_item)
                # Clear selected Item
                self._select(index)
            else:
                # Currently do not have the logic to figure out if a another item is big enough to swap with 
                # TODO, implement that
                self._select(None)
        
        #else:
        #    # Move into empty slot or swap with occupied slot
        #    self.items[self.selected_index], self.items[index] = (
        #        self.items[index],
        #        self.items[self.selected_index],
        #    )
        #    self.selected_index = None

        self._refresh_item_images()
        return True
