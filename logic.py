import terrain.square as square
import units.unit as unit

import json

class Logic():
    def __init__(self):
        self.state = {
            "0x0":square.Square(0,0), "1x0":square.Square(1,0), "2x0":square.Square(2,0), 
            "0x1":square.Square(0,1), "1x1":square.Square(1,1), "2x1":square.Square(2,1)}
        self.playerlist = []

        #Logic needs to have a clock and should probably jut use the self.root.after on the GUI of host
        #clock
        #def update_clock():
        #    self.time = self.time + 1 
        #    print(self.time)
        #    # Call update_clock again after 1 second
        #    self.root.after(1000, update_clock)  
        #update_clock()

    def join(self, player):
        print(player["name"], " joined")
        self.playerlist.append(player)
        
        hero_unit = unit.Unit(0, 0, "Hero")
        #spawn_location = next((spot for spot in self.state if spot.x == 0 and spot.y == 0), None) 
        #spawn_location.occupied = unit
        self.state[player["name"]+" Hero"] = hero_unit

        self.broadcast_world()
    
    def broadcast_world(self):
        #send all players a message that the world has updated
        #this should be kept in such a way that thich can be changed to a network message with new world state
        for player in self.playerlist:
            #currently generate a GUI event that has it get the world state
            (player["root"]).event_generate("<<WorldUpdated>>")
    
    #Currently world state is just accesable, since it is required to be singleplayer
    def get_world(self):
        return self.state