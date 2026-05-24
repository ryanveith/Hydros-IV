from tkinter import *
import json

class GUI():
    def __init__(self, world_logic):
        self.world = []
        self.is_host = True
        self.world_host = None
        if self.is_host:
            self.world_host = world_logic

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
        self.root.bind("<KeyRelease>", self.key_pressed)
        self.root.bind("<Button-1>", self.key_pressed)
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
            else:
                raise Exception("Multiplayer fuctionality is not supported, you must be host to join a world")
        else:
            raise Exception("You can only join a world from the main menu, not a game, quit the current game first")
    
    def world_changed(self, event):
        print(event)
        self.world = self.world_host.get_world()
        print("World Updated:", self.world)

    def key_pressed(self, event):
        if (self.state == 0):
            #handle main menu
            print(event)
            if (event.type == "3"):
                #Key event
                if (event.keysym == "Return"):
                    print("joining world")
                    self.join_world()
        else:
            return
        #by default is doing mouse and keys so first step is probably distingishing event type?
        #could also just bind them to different events, only downside of this is it means re-mapping controls cant switch between mouse/key nicely
        #In the end it is going to get passes to world logic if it is not a gui change so...

        #print(event.keysym)
        #if (event.keysym == "Return"):