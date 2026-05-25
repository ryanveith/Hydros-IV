import square

import json

class Logic():
    def __init__(self):
        self.state = [square.Square(0,0), square.Square(1,0), square.Square(2,0)]
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