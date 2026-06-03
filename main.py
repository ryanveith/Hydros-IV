import graphics.gui as gui
import logic

class Main():
    def __init__(self):
        print("hello world")
        #TODO, refactor such that the user interface can create world_logic as there should be none necessary
        #or it should all be a different class in main menu
        world_logic = logic.Logic()
        user_interface = gui.GUI(world_logic)
        #Since GUI runs the tkinter loop it is a blocking thing, nothing else in main will run until program is closed
        #This is fine, GUI can just call all these functions

Main()
    