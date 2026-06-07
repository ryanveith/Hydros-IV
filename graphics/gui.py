from tkinter import *
from PIL import Image, ImageTk
import json

import drawable_object
from graphics import keybinds
from units import unit
import drawable_object
import terrain.square as square
import utility.constants as CONSTANTS
import utility.action_variables as ACTIONS

class GUI():
    def __init__(self, world_logic):
        # Variables for World
        self.world = {}
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

        # Python will garbage collect images that tkinter needs to display on canvas
        # So save open images to prevent this 
        # (it might make more sense to have a list of static texture images loaded an only use this for animations but good enough)
        self.image_list = {}

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
        self.canvas = Canvas(self.root, bg="green", width=self.canvas_width, height=self.canvas_height, relief="groove", borderwidth=2)
        # display in root
        self.canvas.pack(fill="both", expand=True)

        #TODO - create home/main menu
        #main_menu = Frame(self.root, width=self.canvas_width, height=self.canvas_height, relief="groove", borderwidth=2)
        ##main_menu.grid(row=0, column=0)
        #main_menu.rowconfigure(0, weight=1)
        #main_menu.columnconfigure(0, weight=1)
        #Stuff to show in home
        #self.menu_label = Label(main_menu, text="Testing")
        #self.menu_label.pack(expand=True, fill="both")
        #.tkraise() or .lift() to choose which one is in front


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
        #self.time = self.time + 1 
        #print(self.time)

        #Do pan/zoom stuff
        if (self.panning):
            if (self.pan_up):
                self.pan_screen("Up", 1)
            if (self.pan_down):
                self.pan_screen("Down", 1)
            if (self.pan_right):
                self.pan_screen("Right", 1)
            if (self.pan_left):
                self.pan_screen("Left", 1)
        if (self.zoom_in):
            self.zoom_screen("In", 5)
        elif (self.zoom_out):
            self.zoom_screen("Out", 5)

        # Redraw the canvas screen    
        self.draw_world("clock update")

        # While the world is running keep redrawing it regularly
        # Instead of just redwaring it when the world updates
        # This makes for much smoother panning/zooming and should hopefully do the same for solo menus
        if (self.running_world == True):
            # Call update_clock again after 0.01 second
            self.root.after(10, self.clock_Update_draw_world)

    def draw_world(self, mode):
        # Everything we are drawing should be a child of Drawable_Object
        # Therefore just call draw_self on them
        object_to_draw: drawable_object.Drawable_Object
        for object_to_draw in self.world.values():
            object_to_draw.draw_self(self.zoom, self.screen_x, self.screen_y, self.canvas, mode, self.image_list)

        #Draw halos for everything that is selected?
        #Halos should be a drawable object or extension/child of it though
        if (self.selected != None):
            unit: drawable_object.Drawable_Object
            for unit, halo in self.selected:
                halo.tile_x = unit.tile_x
                halo.tile_y = unit.tile_y
                halo.draw_self(self.zoom, self.screen_x, self.screen_y, self.canvas, mode, self.image_list)
   
            
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

    # Button events do not have a keysym so add one and then let key_pressed handle it
    def button_pressed(self, event):
        event.keysym = "mouse_"+str(event.num)
        self.key_pressed(event)

    # Based on what the game state Handle key or mouse input
    def key_pressed(self, event):
        # Currently only way of interacting with main menu is releasing enter key
        if (self.state == 0):
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
            # Unit Select
            elif(event.keysym == self.keybindings.select):
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
                        if (clicked_unit != None and isinstance(clicked_unit, unit.Unit)):
                            # Append the selected unit to list
                            self.selected.append( (clicked_unit, drawable_object.Drawable_Object(clicked_unit.tile_x, clicked_unit.tile_y, None, "halo", CONSTANTS.TILE_WIDTH, int(CONSTANTS.TILE_HEIGHT / 2), "shadow.png")) )
                    else:
                        # Clear images from canvas (since this does not happen during garbage collection)
                        for selected_unit, halo in self.selected:
                            halo.clear_image(self.canvas)
                        if (clicked_unit != None and isinstance(clicked_unit, unit.Unit)):
                            self.selected = [ (clicked_unit, drawable_object.Drawable_Object(clicked_unit.tile_x, clicked_unit.tile_y, None, "halo", CONSTANTS.TILE_WIDTH, int(CONSTANTS.TILE_HEIGHT / 2), "shadow.png")) ]
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
        
