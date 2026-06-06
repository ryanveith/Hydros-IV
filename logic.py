import utility.constants as CONSTANTS
import drawable_object
import terrain.square as square
import units.unit as unit
from projectiles.projectile import Projectile
import utility.action_variables as ACTIONS

import json


class Logic():
    def __init__(self):
        self.state = {
            "0x0":square.Square(0,0), "1x0":square.Square(1,0), "2x0":square.Square(2,0), 
            "0x1":square.Square(0,1), "1x1":square.Square(1,1), "2x1":square.Square(2,1),
            "0x2":square.Square(0,2), "1x2":square.Square(1,2), "2x2":square.Square(2,2)}
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
            action = object.update_self(self)
            if (action != None):
                command, context = action

                if (command == ACTIONS.MOVE):
                    #split name of the desination tile into x y cords
                    new_locations = context.split("x")
                    new_x = int(new_locations[0])
                    new_y = int(new_locations[1])
                    
                    old_spot = self.state.get(str(object.x)+"x"+str(object.y))
                    new_spot = self.state.get(str(new_x)+"x"+str(new_y))
                    print("MOVE COMMANDS", new_locations)

                    #check spot is actually free to move into
                    
                    if(old_spot == None or new_spot == None):
                        raise IndexError("The given square cords were not withing the dict")
                    if (new_spot.occupied != None):
                        raise NotImplementedError("Do not have unit collision yet")
                    #update pointers for ocupied spots
                    old_spot.occupied = None
                    new_spot.occupied = object
                    
                    #do offsets for animating the walk
                    # 0x0   1x0   2x0
                    #    0x1   1x1   2x1
                    if (object.x > new_x or (object.x == new_x and (object.y % 2) == 1)):
                        object.x_offset += int(CONSTANTS.TILE_WIDTH/2)
                    else:
                        object.x_offset -= int(CONSTANTS.TILE_WIDTH/2)

                    if (object.y > new_y):
                        object.y_offset += int(CONSTANTS.TILE_HEIGHT/2)
                    else:
                        object.y_offset -= int(CONSTANTS.TILE_HEIGHT/2)

                    #set the units x y to be square they are walking into
                    object.x = new_x
                    object.y = new_y

                    print("context", context, type(context))
                    #This "action" was completed so remove it from list
                    object.implement_commands_list.pop(0)
                    

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
            x=(tile.x - (tile.y % 2)/2) * CONSTANTS.TILE_WIDTH, 
            y=tile.y * CONSTANTS.TILE_HEIGHT, 
            tag=str(self.increment_id), 
            target=target)
        self.increment_id += 1