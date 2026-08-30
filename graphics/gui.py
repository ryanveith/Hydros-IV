from tkinter import *
from PIL import Image, ImageTk
import json

import drawable_object
from graphics import keybinds
from units import unit
import drawable_object
import menus.menu_screen as menu_screen
import terrain.square as square
from terrain.square import get_adjacent_tiles
from buildings.storage_box import Storage_Box
import utility.constants as CONSTANTS
import utility.action_variables as ACTIONS
from utility.shadow_tint import load_tinted_shadow

class GUI():
    def __init__(self, world_logic):
        # Variables for World
        self.world = {}
        self.menu = []
        self.open_inventory = None
        
        self.is_host = True
        self.world_host = None
        if self.is_host:
            self.world_host = world_logic

        # camera control
        self.zoom = 100
        self.screen_x = 0
        self.screen_y = 0
        # pan camera
        self.panning = False
        self.pan_up = False
        self.pan_down = False
        self.pan_right = False
        self.pan_left = False
        # zoom camera
        self.zoom_in = False
        self.zoom_out = False

        self.keybindings = keybinds.Keybinds()

        self.selected = []
        self.multiselect = False

        self.time = 0

        # Python will garbage collect images that tkinter needs to display on canvas
        # So save open images to prevent this 
        # (it might make more sense to have a list of static texture images loaded an only use this for animations but good enough)
        self.photo_image_list: dict[str, ImageTk.PhotoImage] = {}

        self.pillow_image_list = {}

        self.state = 0

        self.name = "Giles Corey"


        #Root window

        # create root window
        self.root = Tk()
        # getting computer screen width and height in pixels
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # root window title and default dimensions
        self.root.title("Hydros IV")
        # Set geometry (widthxheight)
        self.root.geometry((str)(max(150, screen_width - 50)) + "x" + (str)(max(100, screen_height - 10)))        
        # Start "fullscreen" while still allowing screen resizing
        self.root.state("zoomed")


        #Display

        self.canvas_width = screen_width - 10
        self.canvas_height = screen_height - 10
        # create canvas
        self.canvas = Canvas(self.root, bg="green", width=self.canvas_width, height=self.canvas_height, relief = "groove", borderwidth = 2)
        # display in root
        self.canvas.pack(fill="both", expand=True)


        # TODO - create home/main menu
        # Lambda has to have the class passed into it so it uses menu_screen rather then where it is createed
        self.menu.append(
            menu_screen.Menu_Screen(
                int(self.canvas_width/2), int(self.canvas_height/2), 
                400, 400, "blue", 
                text = "Testing - only interaction is enter key", 
                handle_click = lambda self, click_x, click_y, click_type="interact": 
                True if (
                    click_x > self.tile_x - self.my_images[0].width and 
                    click_x < self.tile_x + self.my_images[0].width and 
                    click_x > self.tile_y - self.my_images[0].width and 
                    click_x < self.tile_y + self.my_images[0].height)
                else
                False))
        


        #User Interaction

        # Key/Mouse 
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<ButtonPress>", self.button_pressed)
        self.root.bind("<KeyRelease>", self.key_released)
        self.root.bind("<ButtonRelease>", self.button_released)
        # Window resize
        self.root.bind('<Configure>', self.window_reseize)
        # World events
        self.root.bind("<<WorldUpdated>>", self.world_changed)

        # Setting root also starts world updates
        # This is requred since using same root for logic as host's tkinter mainloop
        world_logic.set_root(self.root)

        # Draw everything since even in loop nonthing will update based on time until clock_update_draw_world() is called when joining
        self.draw_world("none")
        # Execute Tkinter Mainloop
        self.root.mainloop()

    def window_reseize(self, event):
        # The canvas is set up to automatically resize to window
        # We just need to keep track of its size to help scale things on it
        # This might get removed later if having user controlled zoom strictly better
        # self.canvas.scale()    
        if (event.widget == self.canvas):
            self.canvas_width = self.canvas.winfo_width()
            self.canvas_height = self.canvas.winfo_height()

    def join_world(self):
        if (self.world_host == None):
            raise Exception ("Someone must host the world for you to be able to join it")
        # The 0 state is currnlty main menu but this is a TODO and not finished
        if (self.state == 0):
            if (self.is_host == True):
                self.world_host.join({"name": self.name, "root": self.root})
                # Clear the main menu stuff from menu and then populate it with other stuff like resource bars
                menu_item: menu_screen.Menu_Screen
                for menu_item in self.menu:
                    menu_item.clear_image(self.canvas)
                self.menu = []
                # TODO resource bars or any other default menu type things that show in game

                # Start updating canvas based on world
                # self.state should be expanded so this can be simplified
                self.state = 1
                self.running_world = True
                self.clock_Update_draw_world()
            else:
                raise Exception("Multiplayer fuctionality is not supported, you must be host to join a world")
        else:
            raise Exception("You can only join a world from the main menu, not a game, quit the current game first")
    
    def world_changed(self, event):
        #TODO
        # The entire world should not get overwritten each tick
        # Only what has been changed should need to get updated
        self.world = self.world_host.get_world()
    
    # This should get called only once, an then will keep redrawing GUI
    def clock_Update_draw_world(self):
        self.time = self.time + 1 
        
        #Do pan/zoom stuff
        if (self.panning):
            if (self.pan_up):
                self.pan_screen("Up", 2)
            if (self.pan_down):
                self.pan_screen("Down", 2)
            if (self.pan_right):
                self.pan_screen("Right", 2)
            if (self.pan_left):
                self.pan_screen("Left", 2)
        if (self.zoom_in):
            self.zoom = min(self.zoom + 2, 300)
            #self.zoom_screen("In", 5)
        elif (self.zoom_out):
            self.zoom = max(self.zoom - 2, 50)
            #self.zoom_screen("Out", 5)

        # Redraw the canvas screen    

        # TODO - remaking all the images takes a noticible amount of time, but is requried for things like zooming or healthbar updates
        if (self.time % 10 == 0):
            self.draw_world("zoom screen")
        else:    
            self.draw_world("clock update")

        # While the world is running keep redrawing it regularly
        # Instead of just redwaring it when the world updates
        # This makes for much smoother panning/zooming and should hopefully do the same for solo menus
        if (self.running_world == True):
            # Call update_clock again after 0.01 second
            self.root.after(10, self.clock_Update_draw_world)

    def draw_world(self, mode):
        if (mode == "zoom screen"): 
            # If we are zooming the screen zoom all images in use
            for file_path, (tkinter_image, width, height) in list(self.photo_image_list.items()):
                # Image can be none, and will for rectangles which will not have a viable file path
                if (tkinter_image != None):
                    if "::" in file_path:
                        base_path, color = file_path.rsplit("::", 1)
                        self.photo_image_list[file_path] = (
                            load_tinted_shadow(base_path, color, width, height, self.zoom),
                            width,
                            height,
                        )
                    else:
                        self.photo_image_list[file_path] = (ImageTk.PhotoImage(Image.open(file_path).resize((int(self.zoom / 100 * width), int(self.zoom / 100 * height)))), width, height)

        # Everything we are drawing should be a child of Drawable_Object
        # Therefore just call draw_self on them
        object_to_draw: drawable_object.Drawable_Object
        for object_to_draw in self.world.values():
            object_to_draw.draw_self(self.zoom, self.screen_x, self.screen_y, self.canvas, mode, self.photo_image_list)

        # Draw halos for everything that is selected?
        # Halos should be a drawable object or extension/child of it though
        if (self.selected != None):
            unit: drawable_object.Drawable_Object
            for unit, halo in self.selected:
                halo.tile_x = unit.tile_x
                halo.tile_y = unit.tile_y
                halo.draw_self(self.zoom, self.screen_x, self.screen_y, self.canvas, mode, self.photo_image_list)

        # Draw menu items last so by default they are drawn over the top of things
        # This does not quite work since unit can be created after menu and then would be on top so use tkinter.raise
        object_to_draw: drawable_object.Drawable_Object
        for object_to_draw in self.menu:
            object_to_draw.draw_self(self.zoom, self.screen_x, self.screen_y, self.canvas, mode, self.photo_image_list)
        self.canvas.tag_raise("menu")
        
            
    def _create_selection_halo(self, selected_unit: unit.Unit) -> drawable_object.Drawable_Object:
        halo = drawable_object.Drawable_Object(
            selected_unit.tile_x,
            selected_unit.tile_y,
            None,
            "halo",
            CONSTANTS.TILE_WIDTH,
            int(CONSTANTS.TILE_HEIGHT / 2),
            "shadow.png",
        )
        halo.my_images[0].tint_color = selected_unit.team.color if selected_unit.team else None
        return halo

    def pan_screen(self, direction, amount):
        if (direction == "Up"):
            self.screen_y += amount
        elif (direction == "Down"):
            self.screen_y -= amount
        elif (direction == "Left"):
            self.screen_x += amount
        elif (direction == "Right"):
            self.screen_x -= amount
        else:
            return
        self.draw_world("pan screen")

    def zoom_screen(self, direction, amount):
        if (direction == "In"):
            self.zoom += amount
            if (self.zoom > 300):
                self.zoom = 300
        elif (direction == "Out"):
            self.zoom -= amount
            if (self.zoom < 50):
                self.zoom = 50
        else:
            return
        self.draw_world("zoom screen")

    def get_grid_square(self, x, y):
        # Convert to absolute cordinates
        x = x/(self.zoom/100)
        y = y/(self.zoom/100)
        x -= self.screen_x
        y -= self.screen_y
        # Get aprox gridspace (prioritizes being fast over being correct)
        y: int = round(y/CONSTANTS.TILE_HEIGHT + 0.5)
        x = round(x/CONSTANTS.TILE_WIDTH - (y % 2)/2)
        return (int(x), int(y))

    def handle_menu_click(self, event):
        # Iterate though all menu screens on click to deterimne if they are clicked and if so hanlde it
        # Returns True if any menu consumed the click
        click_type = "shift" if (event.state & 0x0001) else "interact"
        for screen in self.menu:
            did_something = screen.handle_click(
                self = screen, click_x = event.x, click_y = event.y, click_type = click_type)
            if did_something:
                print(screen)
                return True
        return False

    def close_inventory(self):
        if self.open_inventory is None:
            return
        # clear_image also clears linked_storage canvas ids while it is still attached
        self.open_inventory.clear_image(self.canvas)
        for image in self.open_inventory.my_images:
            image.tkinter_id = None
        if getattr(self.open_inventory, "linked_storage", None) is not None:
            linked = self.open_inventory.linked_storage
            for image in linked.my_images:
                image.tkinter_id = None
            self.open_inventory.linked_storage = None
        if self.open_inventory in self.menu:
            self.menu.remove(self.open_inventory)
        self.open_inventory = None

    def open_unit_inventory(self, selected_unit: unit.Unit):
        self.close_inventory()
        inventory = selected_unit.inventory
        inventory.linked_storage = None
        for tile in get_adjacent_tiles(self.world, selected_unit.tile_x, selected_unit.tile_y):
            if isinstance(tile.occupied, Storage_Box):
                inventory.linked_storage = tile.occupied.storage
                inventory.linked_storage._select(None)
                break
        inventory.tile_x = int(self.canvas_width / 2)
        # Shift unit inventory up a bit when a box panel will sit below it
        if inventory.linked_storage is not None:
            inventory.tile_y = int(self.canvas_height / 2 - 80)
        else:
            inventory.tile_y = int(self.canvas_height / 2)
        self.menu.append(inventory)
        self.open_inventory = inventory

    # Button events do not have a keysym so add one and then let key_pressed handle it
    def button_pressed(self, event):
        event.keysym = "mouse_"+str(event.num)
        self.key_pressed(event)

    # Based on what the game state Handle key or mouse input
    def key_pressed(self, event):
        # Currently only way of interacting with main menu is releasing enter key
        if (self.state == 0):
            # In main menu there is no main loop so interacing with it needs to call draw world to display any changes
            self.draw_world("none")
            self.handle_menu_click(event)
            return
        else:
            # First there should be a check that a gui element is not been clicked
            # This is because multiple "actions" can have the same keybind (think interact and select unit which are both left click)
            # TODO - decide on handling for upper/lower case keysym - should they be treated as distinct or not

            # Start panning screen
            if (event.keysym == self.keybindings.pan_screen_up):
                self.pan_up = True
                self.panning = True
            elif (event.keysym == self.keybindings.pan_screen_down):
                self.pan_down = True
                self.panning = True
            elif (event.keysym == self.keybindings.pan_screen_left):
                self.pan_left = True
                self.panning = True
            elif (event.keysym == self.keybindings.pan_screen_right):
                self.pan_right = True
                self.panning = True
            # Start zooming screen
            elif (event.keysym == self.keybindings.zoom_screen_in):
                self.zoom_in = True
            elif (event.keysym == self.keybindings.zoom_screen_out):
                self.zoom_out = True
            # Hold multiselect
            elif (event.keysym == self.keybindings.multiselect_toggle):
                self.multiselect = True
            # Toggle inventory: close if open, else open first selected unit's inventory
            elif (event.keysym == self.keybindings.toggle_inventory or event.keysym.lower() == self.keybindings.toggle_inventory):
                if self.open_inventory is not None:
                    self.close_inventory()
                elif len(self.selected) > 0:
                    self.open_unit_inventory(self.selected[0][0])
            # Pickup first ground item on the selected unit's tile
            elif (event.keysym == self.keybindings.pickup_item or event.keysym.lower() == self.keybindings.pickup_item):
                if len(self.selected) > 0:
                    selected_unit: unit.Unit = self.selected[0][0]
                    tile: square.Square = self.world.get(str(selected_unit.tile_x)+"x"+str(selected_unit.tile_y))
                    if (tile is not None and len(tile.resources) > 0 and None in selected_unit.inventory.items):
                        if (selected_unit.inventory.add_item(tile.resources[0])):
                            item = tile.resources.pop(0)
                            item.clear_image(self.canvas)
                            for image in item.my_images:
                                image.tkinter_id = None
            # Drop selected inventory item onto the selected unit's tile
            elif (event.keysym == self.keybindings.drop_item or event.keysym.lower() == self.keybindings.drop_item):
                if len(self.selected) > 0:
                    selected_unit: unit.Unit = self.selected[0][0]
                    tile: square.Square = self.world.get(str(selected_unit.tile_x)+"x"+str(selected_unit.tile_y))
                    if tile is not None:
                        item = selected_unit.inventory.remove_item()
                        if item is not None:
                            self.world_host.place_ground_item(tile, item)
                        # the above is about tile.resources.append(item)
                        # this does need to end up as a call that changes would state though like movement
                        # so this should all be a drop item call to logic
                    else:
                        raise Exception("No tile to drop item to, and you may not drop items in the void")
            # Unit Select
            elif(event.keysym == self.keybindings.select):
                # Prefer menu clicks (e.g. inventory) over world selection
                if len(self.menu) > 0 and self.handle_menu_click(event):
                    return
                # Get square clicked on
                square_clicked_x, square_clicked_y = self.get_grid_square(event.x, event.y)
                # Check square exists
                # For now only one world, no multiple moving parts - in future get_grid_square prob has to return world
                clicked_tile: square.Square = self.world.get(str(square_clicked_x)+"x"+str(square_clicked_y))
                if (clicked_tile != None):
                    # If there is something on that tile select it
                    clicked_unit = clicked_tile.occupied
                    # Multiselect means add it to selected list, not means replace selected with it
                    if (self.multiselect):
                        if (clicked_unit != None and isinstance(clicked_unit, unit.Unit) and self.world_host.player_team.contains(clicked_unit)):
                            # Append the selected unit to list
                            self.selected.append( (clicked_unit, self._create_selection_halo(clicked_unit)) )
                    else:
                        # Clear images from canvas (since this does not happen during garbage collection)
                        for selected_unit, halo in self.selected:
                            halo.clear_image(self.canvas)
                        if (clicked_unit != None and isinstance(clicked_unit, unit.Unit) and self.world_host.player_team.contains(clicked_unit)):
                            self.selected = [ (clicked_unit, self._create_selection_halo(clicked_unit)) ]
                        else:
                            self.selected = []
            #Move all selected units to destination
            elif(event.keysym == self.keybindings.move_unit or event.keysym.lower() == self.keybindings.move_unit):
                x, y = self.get_grid_square(event.x, event.y)
                if (self.world.get(str(x)+"x"+str(y)) != None):
                    # TODO - don't have a way to handle that multiple units can't actually be in the same space when doing multi unit pathfinding
                    if (len(self.selected) > 0):
                        moveable_unit: unit.Unit
                        #multiselect means queue movement, normal means override
                        if (self.multiselect == True):
                            for moveable_unit, halo in self.selected:
                                moveable_unit.queue_command(ACTIONS.MOVE, str(x)+"x"+str(y))
                        else:
                            for moveable_unit, halo in self.selected:
                                moveable_unit.set_command(ACTIONS.MOVE, str(x)+"x"+str(y))
            elif(event.keysym == self.keybindings.attack_unit or event.keysym.lower() == self.keybindings.attack_unit):
                x, y = self.get_grid_square(event.x, event.y)
                clicked_tile: square.Square = self.world.get(str(x)+"x"+str(y))
                if (clicked_tile != None):
                    target = clicked_tile.occupied
                    if (target != None and isinstance(target, unit.Unit)):
                        selected_units = [selected_unit for selected_unit, halo in self.selected]
                        if (target not in selected_units and len(self.selected) > 0):
                            if (self.multiselect == True):
                                for attacking_unit, halo in self.selected:
                                    if target.team is attacking_unit.team:
                                        continue
                                    attacking_unit.queue_command(ACTIONS.ATTACK, target.key)
                            else:
                                for attacking_unit, halo in self.selected:
                                    if target.team is attacking_unit.team:
                                        continue
                                    attacking_unit.set_command(ACTIONS.ATTACK, target.key)

            else:
                # Debug message for what key was hit
                print(event, event.keysym)
               
    # button events do not have a keysym so add one and then let key_released handle it
    def button_released(self, event):
        event.keysym = "mouse_"+str(event.num)
        self.key_released(event)
            
    # Based on what the game state Handle key or mouse input
    # Usually used for ending thing that are only supposed to happen when a key is held down / instead of toggled
    def key_released(self, event):
        if (self.state == 0):
            # Handle main menu - Enter key is only way to escape
            if (event.keysym == "Return"):
                print("joining world")
                self.join_world()
        else:
            # Stop pan screen (arrow keys by default)
            if (event.keysym == self.keybindings.pan_screen_up):
                self.pan_up = False
                self.panning = False
            elif (event.keysym == self.keybindings.pan_screen_down):
                self.pan_down = False
                self.panning = False
            elif (event.keysym == self.keybindings.pan_screen_left):
                self.pan_left = False
                self.panning = False
            elif (event.keysym == self.keybindings.pan_screen_right):
                self.pan_right = False
                self.panning = False
            # Stop Zoom screen
            elif (event.keysym == self.keybindings.zoom_screen_in):
                self.zoom_in = False
            elif (event.keysym == self.keybindings.zoom_screen_out):
                self.zoom_out = False
            # Hold multiselect
            elif (event.keysym == self.keybindings.multiselect_toggle):
                self.multiselect = False
            
            #Debug
            elif (event.keysym == "Return"):
                target = self.world.get("Giles Corey Hero")
                if (target != None):
                    self.world_host.create_projectile(self.world["2x1"], target)
        
