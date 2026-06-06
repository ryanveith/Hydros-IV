import drawable_object
import utility.action_variables as ACTIONS
import utility.constants as CONSTANTS

import heapq

class Unit(drawable_object.Drawable_Object):
    def __init__(self, x: int, y: int, tag):
        super().__init__(x, y, tag, 100, 100, "elfling.png")
        self.player_commands_list = []
        self.implement_commands_list = []

    def update_self(self, logic):
        #Do movement animation
        ticks_to_move = 8
        if (self.x_offset > 0):
            self.x_offset = max(self.x_offset - int (CONSTANTS.TILE_WIDTH / ticks_to_move), 0)
        elif (self.x_offset < 0):
            self.x_offset = min(self.x_offset + int (CONSTANTS.TILE_WIDTH / ticks_to_move), 0)
        if (self.y_offset > 0):
            self.y_offset = max(self.y_offset - int (CONSTANTS.TILE_HEIGHT / ticks_to_move), 0)
        elif (self.y_offset < 0):
            self.y_offset = min(self.y_offset + int (CONSTANTS.TILE_HEIGHT / ticks_to_move), 0)

        #return super().update_self()
        if (len(self.implement_commands_list) == 0):
            return None
        
        #If there is an action to preform return the required data to do that
        #command, context = self.implement_commands_list[0]
        print("moving?", self.x_offset, self.y_offset)
        if(self.x_offset == 0 and self.y_offset == 0):
            print("returned commands list", self.implement_commands_list)
            return self.implement_commands_list[0]
        #else:

    def move_unit(self, world, destination: str):
        print("moving unit")
        start_tile = world.get(str(self.x)+"x"+str(self.y))
        end_tile = world.get(destination)
        if (start_tile == None or end_tile == None):
            raise NotImplementedError("Start or End destination does not exist, and I have not decided how to handle it")
        route = self.a_star(world, start_tile, end_tile)
        if (route == None):
            raise NotImplementedError("No route found, and I have not decided how to handle it")
        
        print("Path found:")
        path_string = ""
        path_list: list[str] = []
        while(route.path != None):
            path_string = ("("+str(route.current_tile.x)+", "+str(route.current_tile.y)+"), "+path_string)
            path_list.insert(0, ""+str(route.current_tile.x)+"x"+str(route.current_tile.y)+"")
            route = route.path
            print(path_list)
        print(path_string)
        
        #clear implment comands and rebuild it
        self.implement_commands_list.clear()

        tile: str
        for tile in path_list:
            self.implement_commands_list.append((ACTIONS.MOVE, tile))

        print("starting moving")
        print(self.implement_commands_list)
        print("end test debug")

    def pathfind(self, world, x, y):
        print("pathfinding to: "+str(x)+" "+str(y)+", from: "+str(self.x)+", "+str(self.y))
        start_tile = world.get(str(self.x)+"x"+str(self.y))
        end_tile = world.get(str(x)+"x"+str(y))
        if (start_tile == None or end_tile == None):
            raise NotImplementedError("Start or End destination does not exist, and I have not decided how to handle it")
        route = self.a_star(world, start_tile, end_tile)
        if (route == None):
            raise NotImplementedError("No route found, and I have not decided how to handle it")
        
        print("Path found:")
        path_string = ""
        path_list: list[str] = []
        while(route.path != None):
            path_string = ("("+str(route.current_tile.x)+", "+str(route.current_tile.y)+"), "+path_string)
            path_list.insert(0, "("+str(route.current_tile.x)+", "+str(route.current_tile.y)+"), ")
            route = route.path
        print(path_string)
    
        return path_list


    def a_star(self, world, start_tile: drawable_object.Drawable_Object, goal_tile: drawable_object.Drawable_Object):
        #create the frontier as a priority queue
        #using heapq this is normal list but use heapq operations on it
        frontier: list[Node] = []
        
        class Node:
            def __init__(self, current_tile: drawable_object.Drawable_Object, path: None | Node, path_cost: int):
                self.current_tile = current_tile
                self.path = path
                self.path_cost = path_cost

                #From 0,0 can go to right to 0,1 and 0,-1 and left to -1,1, and -1,-1
                #But if you are on
                #0,1 you can go right to 1,0 and 1,2 and left to 0,0 and 0,2
                #I need more logic for this
                if (current_tile.y % 2 == 0):
                    up_left = world.get(str(current_tile.x-1)+"x"+str(current_tile.y+1))
                    down_left = world.get(str(current_tile.x-1)+"x"+str(current_tile.y-1))
                    up_right = world.get(str(current_tile.x)+"x"+str(current_tile.y+1))
                    down_right = world.get(str(current_tile.x)+"x"+str(current_tile.y-1))
                else:  
                    up_left = world.get(str(current_tile.x)+"x"+str(current_tile.y+1))
                    down_left = world.get(str(current_tile.x)+"x"+str(current_tile.y-1))
                    up_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y+1))
                    down_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y-1))
                self.connected_tiles = [up_left, down_left, up_right, down_right]
                self.connected_tiles: list[drawable_object.Drawable_Object] = filter((lambda x: x != None), self.connected_tiles)

            def expand(self):
                children: list[Node] = []
                for new_tile in self.connected_tiles:
                    children.append(Node(new_tile, self, Unit.heuristic(new_tile, goal_tile)))
                return children

            def equals(self, other: Node):
                return self.current_tile == other.current_tile

        #Heapq uses second value as a tiebreaker if first are equal
        #Standard solution is apparantly a incremnting value to handle this
        #I kinda want to just override < in node since it is abitrary here and node is only used here
        a = 0

        #create a starting node and add it to the frontier
        starting_node = Node(start_tile, None, Unit.heuristic(start_tile, goal_tile))
        starting_priority = starting_node.path_cost + Unit.heuristic(start_tile, goal_tile)
        heapq.heappush(frontier, (starting_priority, a, starting_node))
        a+=1

        #Keep track of visited nodes
        visited = {starting_node.current_tile:starting_node.path_cost}

        #Keep expanding nodes in the frontier until we reach the goal or run out of nodes
        while len(frontier) != 0:
            priority, increment, node_to_expand = heapq.heappop(frontier)
            if (node_to_expand.current_tile == goal_tile):
                #node to expand should contain path
                #this is currenly partial single linked list of nodes but can be redone
                return node_to_expand
            else:
                #expand the node and add its successors to the frontier
                new_nodes = node_to_expand.expand()

                for connected_node in new_nodes:
                    #if it is a new node or a shorter path to an existing node handle it
                    if connected_node.current_tile not in visited:
                        #mark it as visited
                        visited[connected_node.current_tile] = connected_node.path_cost
                        #add it to the frontier
                        if connected_node not in frontier:
                            heapq.heappush(frontier, (int(connected_node.path_cost + Unit.heuristic(connected_node.current_tile, goal_tile)), a, connected_node))
                            a+=1
                        # if is already in the frontier update to the new node if it has a smaller priority
                        else:
                            duplicate_priority, duplicate_node = next(node for node in frontier if node.equals(connected_node)) 
                            if duplicate_priority > connected_node.path_cost + Unit.heuristic(connected_node.current_tile, goal_tile):
                                frontier.remove((duplicate_priority, duplicate_node))
                                frontier.append((connected_node.path_cost + Unit.heuristic(connected_node.current_tile, goal_tile), a, connected_node))
                                a+=1
                                heapq.heapify(frontier)
        #No path to goal was found
        return None

    #I was thinking of impementing somethign like A* for this, but dont have the time now
    # def path(self, world, current_tile, goal_tile, path, path_cost, visited): 
    #     if (current_tile == goal_tile):
    #         return path
    #     else:
    #         #add all connections to frontier
    #         up_left = world.get(str(current_tile.x)+"x"+str(current_tile.y+1))
    #         down_left = world.get(str(current_tile.x)+"x"+str(current_tile.y-1))
    #         up_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y+1))
    #         down_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y-1))
    #         new_connections = [up_left, down_left, up_right, down_right]
    #         for connection in new_connections:
    #             if (connection != None):
    #                 #todo ran out of time
    #                 return                
    
    @staticmethod
    def heuristic(current, goal):
        return abs(current.x - goal.x) + abs(current.y - goal.y)
        
