from tkinter import *
from PIL import Image, ImageTk
import json

import terrain.square as square

class GUI():
    def __init__(self, world_logic):
        #variables for world
        self.world = []
        self.is_host = True
        self.world_host = None
        if self.is_host:
            self.world_host = world_logic

        #camera control
        self.tile_width = 100
        self.tile_height = 50
        self.zoom = 100
        self.screen_x = 0
        self.screen_y = 0
        #pan camera
        self.panning = False
        self.pan_up = False
        self.pan_down = False
        self.pan_right = False
        self.pan_left = False
        #zoom camera
        self.zoom_in = False
        self.zoom_out = False

        #Python will garbage collect images that tkinter needs to display on canvas
        #So save open images to prevent this 
        #(it might make more sense to have a list of static texture images loaded an only use this for animations but good enough)
        self.image_list = {}

        self.state = 0

        self.name = "Giles Corey"


        #Root window

        # create root window
        self.root = Tk()

        #getting computer screen width and height in pixels
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # root window title and default dimensions
        self.root.title("Hydros IV")
    
        # Set geometry (widthxheight)
        self.root.geometry((str)(max(150, screen_width - 50)) + "x" + (str)(max(100, screen_height - 10)))        
        #Start "fullscreen" while still allowing screen resizing
        self.root.state("zoomed")


        #Display

        self.canvas_width = screen_width - 10
        self.canvas_height = screen_height - 10

        #create canvas
        self.canvas = Canvas(self.root, bg="green", width=self.canvas_width, height=self.canvas_height, relief="groove", borderwidth=2)
        
        #topbar_size = self.root.winfo_y() - self.canvas.winfo_y()
        #self.canvas_height = self.canvas_height - topbar_size

        #display in root
        self.canvas.pack(fill="both", expand=True)

        #create home/main menu
        #main_menu = Frame(self.root, width=self.canvas_width, height=self.canvas_height, relief="groove", borderwidth=2)
        ##main_menu.grid(row=0, column=0)
        #main_menu.rowconfigure(0, weight=1)
        #main_menu.columnconfigure(0, weight=1)
        #Stuff to show in home
        #self.menu_label = Label(main_menu, text="Testing")
        #self.menu_label.pack(expand=True, fill="both")
        #.tkraise() or .lift() to choose which one is in front


        #User Interaction

        #key pressed
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<ButtonPress-1>", self.key_pressed)

        self.root.bind("<KeyRelease>", self.key_released)
        self.root.bind("<ButtonRelease-1>", self.key_released)
        
        #<Button-1>: Left mouse button click.
        #<Button-2>: Middle mouse button (scroll wheel) click.
        #<Button-3>: Right mouse button click.
        #<Double-Button-1>: Double-click with the left mouse button.
        #<ButtonRelease-1> release left mouse
        
        #window resize
        self.root.bind('<Configure>', self.window_reseize)
        #world events
        self.root.bind("<<WorldUpdated>>", self.world_changed)


        print("Created Graphical User Interface")
        # Execute Tkinter
        self.root.mainloop()

    def window_reseize(self, event):
        #The canvas is set up to automatically resize to window
        #We just need to keep track of its size to help scale things on it
        #This might get removed later if having user controlled zoom strictly  better
        #self.canvas.scale()    
        if (event.widget == self.canvas):
            self.canvas_width = self.canvas.winfo_width()
            self.canvas_height = self.canvas.winfo_height()

    def join_world(self):
        if (self.world_host == None):
            raise Exception ("Someone must host the world for you to be able to join it")
        if (self.state == 0):
            if (self.is_host == True):
                self.world_host.join({"name": self.name, "root": self.root})
                #Start updating canvas based on world
                #self.state should be expanded so this can be simplified
                self.state = 1
                self.running_world = True
                self.clock_Update_draw_world()
            else:
                raise Exception("Multiplayer fuctionality is not supported, you must be host to join a world")
        else:
            raise Exception("You can only join a world from the main menu, not a game, quit the current game first")
    
    def world_changed(self, event):
        self.world = self.world_host.get_world()
        print("World Updated:", self.world)
    
    def clock_Update_draw_world(self):
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


        #This should get called only once, an then will keep redrawing GUI
        #self.time = self.time + 1 
        #print(self.time)
        self.draw_world("clock update")

        if (self.running_world == True):
            #Call update_clock again after 1 second
            self.root.after(10, self.clock_Update_draw_world)

    def draw_world(self, mode):
        for drawable_object in self.world:
            if (drawable_object.tkinter_id == None):
                #This is a new object that needs to get added
                object_image = ImageTk.PhotoImage(Image.open(drawable_object.image_file).resize((int(self.zoom / 100 * self.tile_width), int(self.zoom / 100 * self.tile_height))))
                drawable_object.tkinter_id = self.canvas.create_image(
                        int(self.zoom / 100 * ((drawable_object.x + (drawable_object.y % 2)/2) * self.tile_width + self.screen_x)), 
                        int(self.zoom / 100 * (drawable_object.y * self.tile_height + self.screen_y)), 
                        image=object_image, 
                        anchor="center",
                        tag=drawable_object.tag)
                #prevent image from being garbage collected
                self.image_list[drawable_object.tkinter_id] = object_image
            else:
                #Update Objects
                self.canvas.coords(
                    drawable_object.tkinter_id, 
                    int(self.zoom / 100 * ((drawable_object.x + (drawable_object.y % 2)/2) * self.tile_width + self.screen_x)), 
                    int(self.zoom / 100 * (drawable_object.y * self.tile_height + self.screen_y)))
                #zoom images
                if (mode == "zoom screen"):
                    square_image = ImageTk.PhotoImage(Image.open(drawable_object.image_file).resize((int(self.zoom / 100 * self.tile_width), int(self.zoom / 100 * self.tile_height))))
                    self.canvas.itemconfig(drawable_object.tkinter_id, image=square_image)
                    #prevent image from being garbage collected
                    self.image_list[drawable_object.world+str(drawable_object.x)+"x"+str(drawable_object.y)] = square_image
            
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
        #Convert to absolute cordinates
        x = x/(self.zoom/100)
        y = y/(self.zoom/100)
        x -= self.screen_x
        y -= self.screen_y
        #Get aprox gridspace (prioritizes being fast over being correct)
        y = round(y/self.tile_height)
        x = round(x/self.tile_width - (y % 2)/2)
        return (x, y)

    #by default is doing mouse and keys so first step is probably distingishing event type?
    #could also just bind them to different events, only downside of this is it means re-mapping controls cant switch between mouse/key nicely
    #In the end it is going to get passes to world logic if it is not a gui change so...    
    def key_pressed(self, event):
        if (self.state == 0):
            return
        else:
            if (event.type == "2"):
                #start panning screen
                if (event.keysym == "Up"):
                    self.pan_up = True
                    self.panning = True
                elif (event.keysym == "Down"):
                    self.pan_down = True
                    self.panning = True
                elif (event.keysym == "Left"):
                    self.pan_left = True
                    self.panning = True
                elif (event.keysym == "Right"):
                    self.pan_right = True
                    self.panning = True
                elif (event.keysym == "plus"):
                    self.zoom_in = True
                elif (event.keysym == "minus"):
                    self.zoom_out = True
                else:
                    print(self.get_grid_square(event.x, event.y))
                

            
    def key_released(self, event):
        if (self.state == 0):
            #handle main menu
            print(event)
            if (event.type == "3"):
                #Key event
                if (event.keysym == "Return"):
                    print("joining world")
                    self.join_world()
        else:
            if (event.type == "3"):
                #stop pan screen (arrow keys for now)
                if (event.keysym == "Up"):
                    self.pan_up = False
                    self.panning = False
                elif (event.keysym == "Down"):
                    self.pan_down = False
                    self.panning = False
                elif (event.keysym == "Left"):
                    self.pan_left = False
                    self.panning = False
                elif (event.keysym == "Right"):
                    self.pan_right = False
                    self.panning = False
                elif (event.keysym == "plus"):
                    self.zoom_in = False
                elif (event.keysym == "minus"):
                    self.zoom_out = False

        
