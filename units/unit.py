import drawable_object
import utility.action_variables as ACTIONS
import utility.constants as CONSTANTS
from menus.storage_menu import Storage_Menu
from menus.equipment_menu import Equipment_Menu
from menus.multi_menu import Multi_Menu
from terrain.square import get_adjacent_tiles

import heapq

class Unit(drawable_object.Drawable_Object):
    def __init__(self, tile_x: int, tile_y: int, key: str, tag: str,
                 image_file: str = "elfling.png", width: int = 100, height: int = 100):
        super().__init__(tile_x, tile_y, key, tag, width, height, image_file)
        self.player_commands_list: list[tuple[int, str]] = []
        self.implement_commands_list: list[tuple[int, str]] = []
        
        self.name = key
        self.team = None

        # Ground shadow drawn under the sprite (tint set when joining a team)
        self.my_images.insert(0, drawable_object.Drawable_Image(
            0, -int(CONSTANTS.TILE_HEIGHT / 4),
            int(CONSTANTS.TILE_WIDTH * 3/4), int(CONSTANTS.TILE_HEIGHT / 2),
            "shadow.png",
        ))
        self.shadow_image = self.my_images[0]
        sprite = self.my_images[1]

        # Healthbar should be rectangles so it can change size without extra 
        self.my_images.append(drawable_object.Drawable_Image(0, -sprite.height, sprite.width, int(sprite.height/8), "gray", drawable_type = 1))
        self.my_images.append(drawable_object.Drawable_Image(0, -sprite.height, sprite.width - 4, int(sprite.height/8) - 4, "green", drawable_type = 1))
        self.my_images.append(drawable_object.Drawable_Image(0, -sprite.height, sprite.width - 4, int(sprite.height/8) - 4, self.name, drawable_type = 2))
        
        self.max_health = 100
        self.health = 100

        self.inventory = Multi_Menu(Storage_Menu(3, 3), Equipment_Menu())

    def update_self(self, logic):
        # Do Movement Animation (Currenlty just moving entire image in increments)
        ticks_to_move: int = 8
        if (self.x_offset > 0):
            self.x_offset = max(self.x_offset - int (CONSTANTS.TILE_WIDTH / ticks_to_move), 0)
        elif (self.x_offset < 0):
            self.x_offset = min(self.x_offset + int (CONSTANTS.TILE_WIDTH / ticks_to_move), 0)
        if (self.y_offset > 0):
            self.y_offset = max(self.y_offset - int (CONSTANTS.TILE_HEIGHT / ticks_to_move), 0)
        elif (self.y_offset < 0):
            self.y_offset = min(self.y_offset + int (CONSTANTS.TILE_HEIGHT / ticks_to_move), 0)

        # Update healthbar (indices: 0=shadow, 1=sprite, 2=gray, 3=green, 4=name)
        if (len(self.my_images) >= 4):
            self.my_images[3].width = int(self.health/self.max_health * self.my_images[1].width - 4)

        # If there is an action to preform return the required data to do that
        # TODO - need to have a movement cooldown rather then use offset
        # TODO - also a seperate attack cooldown for any units that can move and attack at same time in future
        
        if (len(self.implement_commands_list) == 0):
            if (len (self.player_commands_list) > 0):
                command, context = self.player_commands_list[0]
                if (command == ACTIONS.MOVE):
                    self.player_commands_list.pop(0)
                    self.move_unit(logic.get_world(), context)
                elif (command == ACTIONS.ATTACK):
                    self.player_commands_list.pop(0)
                    world = logic.get_world()
                    target = world.get(context)
                    if (self.can_attack(target, world)):
                        self.implement_commands_list.append((ACTIONS.ATTACK, target.key))
            # TODO - decide on ticks waiting before moving to next action in queue
            # For inteupted actions it makes sense to wait a bit
            # Waiting at least one tick also simplifies this section since we don't have to keep looking for an action until we find a valid one 
            return None

        # Currenlty only possible aciton in queue is move, and only return an action after the offset it 0
        #command, context = self.implement_commands_list[0]
        if(self.x_offset == 0 and self.y_offset == 0):
            return self.implement_commands_list[0]
        #else:

    def queue_command(self, command: int, context: str):
        self.player_commands_list.append( (command, context) )
    
    def set_command(self, command: int, context: str):
        self.player_commands_list = [ (command, context) ]
        self.implement_commands_list.clear()

    def has_bow_equipped(self) -> bool:
        equipment = self.inventory.equipment
        for i, slot in enumerate(equipment.slots):
            if slot["name"] in ("hand_left", "hand_right"):
                item = equipment.items[i]
                if item is not None and item.weapon_type == "bow":
                    return True
        return False

    def tile_distance_to(self, target: drawable_object.Drawable_Object) -> int:
        return Unit.heuristic(self, target)

    def is_adjacent_to(self, target: drawable_object.Drawable_Object, world: dict) -> bool:
        adjacent_tiles = get_adjacent_tiles(world, self.tile_x, self.tile_y)
        target_tile_key = str(target.tile_x) + "x" + str(target.tile_y)
        for tile in adjacent_tiles:
            if str(tile.tile_x) + "x" + str(tile.tile_y) == target_tile_key:
                return True
        return False

    def can_attack(self, target, world: dict) -> bool:
        if target is None or not isinstance(target, Unit):
            return False
        if target.key == self.key or target.health <= 0:
            return False
        if target.team is not None and self.team is not None and target.team is self.team:
            return False
        if self.has_bow_equipped():
            return self.tile_distance_to(target) <= CONSTANTS.BOW_RANGE
        return self.is_adjacent_to(target, world)


    # Add steps requried to move unit to destination to implement_commands_list
    def move_unit(self, world: dict[str, drawable_object.Drawable_Object], destination: str):
        start_tile: None | drawable_object.Drawable_Object = world.get(str(self.tile_x)+"x"+str(self.tile_y))
        end_tile: None | drawable_object.Drawable_Object = world.get(destination)
        # TODO - implement not implemented things, first case should not happen, second can definitely happen
        if (start_tile == None or end_tile == None):
            return
            # TODO
            # raise NotImplementedError("Start or End destination does not exist, and I have not decided how to handle it")
        route = self.a_star(world, start_tile, end_tile)
        if (route == None):
            self.implement_commands_list.clear()
            return
            # TODO - try pathing to adjacent tiles
            # raise NotImplementedError("No route found, and I have not decided how to handle it")
        
        # A_Star currently returns "nodes" representing the tiles it traveled, so convert that into a path
        path_list: list[str] = []
        while(route.path != None):
            path_list.insert(0, ""+str(route.current_tile.tile_x)+"x"+str(route.current_tile.tile_y)+"")
            route = route.path
        # Clear implment comands and add route to it
        self.implement_commands_list.clear()
        # TODO - remove this way of copyng path_list since it can be done better
        tile: str
        for tile in path_list:
            self.implement_commands_list.append((ACTIONS.MOVE, tile))

    def movement_blocked(self, world: dict[str, drawable_object.Drawable_Object]):
        command: int
        context: str
        command, context = self.implement_commands_list.pop()
        # If there is no path, then no path is added to list so next thing in player_commands will then start
        self.move_unit(world, context)

    # Return a path to the x, y tile in world from this units location
    # TODO - still work in progress, currenly move unit directly calls A_Star to get around this
    def pathfind(self, world, x, y):
        print("pathfinding to: "+str(x)+" "+str(y)+", from: "+str(self.tile_x)+", "+str(self.tile_y))
        start_tile = world.get(str(self.tile_x)+"x"+str(self.tile_y))
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
            path_string = ("("+str(route.current_tile.tile_x)+", "+str(route.current_tile.tile_y)+"), "+path_string)
            path_list.insert(0, "("+str(route.current_tile.tile_x)+", "+str(route.current_tile.tile_y)+"), ")
            route = route.path
        print(path_string)
    
        return path_list

    # A* search allgorithm
    # Can handle finding a path based on distance alone
    # Currenly does not handle other factors
    # TODO - improve it to consider things, or just replace with Dijkstra's as the only thing you loose is h(n)
    # Though I do think the end goal is weighted A*, where some terrain can be worse
    # This would also be modifiable to handle teleportation, and even AI unit actions 
    def a_star(self, world: dict[str, drawable_object.Drawable_Object], start_tile: drawable_object.Drawable_Object, goal_tile: drawable_object.Drawable_Object):
        # create the frontier as a priority queue
        # using heapq this is normal list but use heapq operations on it
        frontier: list[Node] = []
        
        class Node:
            def __init__(self, current_tile: drawable_object.Drawable_Object, path: None | Node, path_cost: int):
                self.current_tile = current_tile
                self.path = path
                self.path_cost = path_cost
                self.connected_tiles = get_adjacent_tiles(world, current_tile.tile_x, current_tile.tile_y)
                self.connected_tiles: list[drawable_object.Drawable_Object] = filter((lambda tile: tile.occupied == None), self.connected_tiles)

            def expand(self):
                children: list[Node] = []
                for new_tile in self.connected_tiles:
                    children.append(Node(new_tile, self, Unit.heuristic(new_tile, goal_tile)))
                return children

            def equals(self, other: Node):
                return self.current_tile == other.current_tile

        # Heapq uses second value as a tiebreaker if first are equal
        # Standard solution is apparantly a incremnting value to handle this
        # I kinda want to just override < in node since it is abitrary here and node is only used here
        a = 0

        # create a starting node and add it to the frontier
        starting_node = Node(start_tile, None, Unit.heuristic(start_tile, goal_tile))
        starting_priority = starting_node.path_cost + Unit.heuristic(start_tile, goal_tile)
        heapq.heappush(frontier, (starting_priority, a, starting_node))
        a+=1
        # Keep track of visited nodes
        visited = {starting_node.current_tile:starting_node.path_cost}
        # Keep expanding nodes in the frontier until we reach the goal or run out of nodes
        while len(frontier) != 0:
            priority, increment, node_to_expand = heapq.heappop(frontier)
            if (node_to_expand.current_tile == goal_tile):
                # node to expand should contain path
                # this is currenly partial single linked list of nodes but can be redone
                return node_to_expand
            else:
                # expand the node and add its successors to the frontier
                new_nodes = node_to_expand.expand()

                for connected_node in new_nodes:
                    # if it is a new node or a shorter path to an existing node handle it
                    if connected_node.current_tile not in visited:
                        # mark it as visited
                        visited[connected_node.current_tile] = connected_node.path_cost
                        # add it to the frontier
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
        # No path to goal was found
        return None
    
    @staticmethod
    def heuristic(current, goal):
        return abs(current.tile_x - goal.tile_x) + abs(current.tile_y - goal.tile_y)
    
    def draw_self(self, zoom, screen_x, screen_y, canvas, mode, image_list):
        if (self.health <= 0):
            # Unit death animation
            self.clear_image(canvas)
        else:
            return super().draw_self(zoom, screen_x, screen_y, canvas, mode, image_list)

        
