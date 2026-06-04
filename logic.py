import constants
import drawable_object
import terrain.square as square
import units.unit as unit
from projectiles.projectile import Projectile

import json


class Logic():
    def __init__(self):
        self.state = {
            "0x0":square.Square(0,0), "1x0":square.Square(1,0), "2x0":square.Square(2,0), 
            "0x1":square.Square(0,1), "1x1":square.Square(1,1), "2x1":square.Square(2,1)}
        self.playerlist = []
        self.tkinter_mainloop_root = None
        self.time = 0
        self.increment_id = 0

    def set_root(self, root):
        self.tkinter_mainloop_root = root

        #Logic needs to have a clock and should probably jut use the self.root.after on the GUI of host
        self.update_world()

    def join(self, player):
        print(player["name"], " joined")
        self.playerlist.append(player)
        
        hero_unit = unit.Unit(0, 0, "Hero")
        #spawn_location = next((spot for spot in self.state if spot.x == 0 and spot.y == 0), None) 
        #spawn_location.occupied = unit
        self.state[player["name"]+" Hero"] = hero_unit
        self.state["0x0"].occupied = hero_unit

        #self.broadcast_world()
    
    def broadcast_world(self):
        #send all players a message that the world has updated
        #this should be kept in such a way that thich can be changed to a network message with new world state
        for player in self.playerlist:
            #currently generate a GUI event that has it get the world state
            (player["root"]).event_generate("<<WorldUpdated>>")
        
    def update_world(self):
        self.time = self.time + 1

        object: drawable_object.Drawable_Object
        for object in self.state.values():
            object.update_self()

        #send updated state
        self.broadcast_world()
             
        # Call update_clock again after .1 second
        self.tkinter_mainloop_root.after(100, self.update_world)  
    
    #Currently world state is just accesable, since it is required to be singleplayer
    def get_world(self):
        return self.state
    
    def create_projectile(self, tile, target):
        print("Projectile created", tile, target)
        self.state[str(self.increment_id)] = Projectile(
            x=(tile.x - (tile.y % 2)/2) * constants.TILE_WIDTH, 
            y=tile.y * constants.TILE_HEIGHT, 
            tag=str(self.increment_id), 
            target=target)
        self.increment_id += 1