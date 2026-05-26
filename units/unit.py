import drawable_object

import heapq

class Unit(drawable_object.Drawable_Object):
    def __init__(self, x, y, tag):
        super().__init__(x, y, tag, 100, 100, "elfling.png")

    def pathfind    (self, world, x, y):
        print (x, y)
        pass


    def a_star(self, world, current_tile, goal_tile):
        #create the frontier as a priority queue
        #using heapq this is normal list but use heapq operations on it
        frontier = []
        
        class Node:
            def __init__(self, current_tile, path, estimated_path_cost):
                self.current_tile = current_tile
                self.path = path
                estimated_path_cost = estimated_path_cost

                up_left = world.get(str(current_tile.x)+"x"+str(current_tile.y+1))
                down_left = world.get(str(current_tile.x)+"x"+str(current_tile.y-1))
                up_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y+1))
                down_right = world.get(str(current_tile.x+1)+"x"+str(current_tile.y-1))
                self.actions = [up_left, down_left, up_right, down_right]
                self.actions = filter(lambda x: x != None), self.actions)

        #create a starting node and add it to the frontier
        starting_node = Node(world.get(str(self.x)+"x"+str(self.y)), None, self.heuristic(current_tile, goal_tile))

        #The priority = 0 (initial path cost) + heuristic function of the starting board
        priority = starting_node.path_cost + self.heuristic(current_tile, goal_tile)
        heapq.heapput(frontier, (priority, starting_node))
        #Keep track of visited nodes
        visited = {starting_node.state:starting_node.path_cost}

        #Keep expanding nodes in the frontier until we reach the goal or run out of nodes
        while len(frontier) != 0:
            priority, node_to_expand = heapq.heappop(frontier)
            if (node_to_expand.current_tile == goal_tile):
                #node to expand should contain path
                return node_to_expand
            else:
                #expand the node and add its successors to the frontier
                new_nodes = node_to_expand.actions

                for child_node in new_nodes:
                    #if it is a new node or a shorter path to an existing node handle it
                    if child_node.current_tile not in visited:
                        #mark it as visited
                        visited[child_node.current_tile] = child_node.path_cost
                        #add it to the frontier
                        if child_node not in frontier:
                            frontier.put((child_node.path_cost + self.heuristic(child_node.current_tile, goal_tile), child_node))
                        # if is already in the frontier update to the new node if it has a smaller priority
                        elif frontier[child_node] > child_node.path_cost + self.heuristic(child_node.current_tile, goal_tile):
                            #frontier.update_elem(child_node, (child_node.path_cost + h(child_node.state), child_node))
                            #TODO, implement this in heapq
                            raise NotImplementedError("See TODO")

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
    
    def heuristic(self, current, goal):
        return abs(current.x - goal.x) + abs(current.y - goal.y)
        
