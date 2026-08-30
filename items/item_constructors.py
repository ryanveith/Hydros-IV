from items.item import Item
#name, item_width, item_height, image_file

def create_item_pebble():
    return Item(name = "pebble", item_slot_width = 1, item_slot_height = 1, image_file = "items/pebble.png")

def create_item_stick():
    return Item(name = "stick", item_slot_width = 1, item_slot_height = 2, image_file = "items/stick.png", equipment_type="helm")

def create_item_gold_ore():
    return Item(name = "gold_ore", item_slot_width = 2, item_slot_height = 2, image_file = "items/gold_ore.png")

def create_item_bow():
    return Item(
        name="bow",
        item_slot_width=1,
        item_slot_height=2,
        image_file="placeholder.png",
        equipment_type="hand",
        weapon_type="bow",
    )