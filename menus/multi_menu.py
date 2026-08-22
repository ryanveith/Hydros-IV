import menus.menu_screen as menu_screen
from menus.storage_menu import Storage_Menu
from menus.equipment_menu import Equipment_Menu
from items.item import Item

from tkinter import *
from PIL import ImageTk


class Multi_Menu(menu_screen.Menu_Screen):
    """Owns equipment (left) and storage (right); routes clicks and transfers items."""

    def __init__(
            self,
            storage: Storage_Menu,
            equipment: Equipment_Menu,
            x: int = 0,
            y: int = 0):
        super().__init__(x, y, 1, 1, "dark slate gray")
        self.storage = storage
        self.equipment = equipment
        self.selected_item: Item | None = None
        self.selected_menu: Storage_Menu | Equipment_Menu | None = None
        self.handle_click = Multi_Menu.handle_click

    @property
    def items(self) -> list[Item | None]:
        return self.storage.items

    def add_item(self, item: Item, index: int | None = None) -> bool:
        return self.storage.add_item(item, index)

    def remove_item(self, index: int | None = None) -> Item | None:
        if self.selected_menu is None:
            return None
        item = self.selected_menu.remove_item(index)
        self.selected_item = None
        self.selected_menu = None
        return item

    def _layout_children(self):
        gap = 20
        eq_w = self.equipment.my_images[0].width
        st_w = self.storage.my_images[0].width
        self.equipment.tile_x = int(self.tile_x - (eq_w / 2 + gap / 2))
        self.storage.tile_x = int(self.tile_x + (st_w / 2 + gap / 2))
        self.equipment.tile_y = self.tile_y
        self.storage.tile_y = self.tile_y

    def _other_menu(self, menu):
        if menu is self.equipment:
            return self.storage
        return self.equipment

    def _clear_selection(self):
        self.equipment._select(None)
        self.storage._select(None)
        self.selected_item = None
        self.selected_menu = None

    def draw_self(
            self,
            zoom: int,
            screen_x: int,
            screen_y: int,
            canvas: Canvas,
            mode: str,
            tkinter_image_list: dict[str, ImageTk.PhotoImage]):
        self._layout_children()
        self.equipment.draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)
        self.storage.draw_self(zoom, screen_x, screen_y, canvas, mode, tkinter_image_list)

    def clear_image(self, canvas):
        self.equipment.clear_image(canvas)
        self.storage.clear_image(canvas)
        for image in self.equipment.my_images:
            image.tkinter_id = None
        for image in self.storage.my_images:
            image.tkinter_id = None
        super().clear_image(canvas)

    def handle_click(self, click_x: int, click_y: int, click_type="interact") -> bool:
        self._layout_children()

        for dest in (self.equipment, self.storage):
            incoming = None
            if self.selected_menu is not None and self.selected_menu is not dest:
                incoming = self.selected_item

            consumed, _selected, empty_index = dest.handle_click(
                self=dest,
                click_x=click_x,
                click_y=click_y,
                click_type=click_type,
                incoming_item=incoming)

            if not consumed:
                continue

            other = self._other_menu(dest)

            if (
                empty_index is not None
                and self.selected_menu is not None
                and self.selected_menu is not dest
            ):
                source = self.selected_menu
                item = source.remove_item()
                if item is None:
                    self.selected_item = None
                    self.selected_menu = None
                    return True
                if dest.add_item(item, empty_index):
                    self.selected_item = None
                    self.selected_menu = None
                else:
                    source.add_item(item)
                    self.selected_item = None
                    self.selected_menu = None
                return True

            if dest.selected_item is not None:
                other._select(None)
                self.selected_item = dest.selected_item
                self.selected_menu = dest
            elif self.selected_menu is dest:
                self.selected_item = None
                self.selected_menu = None
            return True

        self._clear_selection()
        return False
