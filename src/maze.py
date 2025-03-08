from typing import List, Dict, Tuple, Set
import random

from room import Room

example_config = {
    "maze_size": (2, 9, 9),  # (height, rows, columns)
    "start_loc": (0, 3, 3),  # start room will be (loc0: loc0+size0, loc1: loc1+size1, loc2: loc2+size2)
    "start_room_size": (1, 3, 3),
    "goal_loc": (0, 0, 0),   # goal room will be (loc0: loc0+size0, loc1: loc1+size1, loc2: loc2+size2)
    "goal_room_size": (1, 1, 1),
    "max_room_size": (2, 2, 2),   # the maximum size of any room on each dimension
}

random.seed(1)


class Maze:
    """
    The Maze class contains all information about a randomly generated 3D maze. The maze is randomly generated at
    initialisation. A config is required for the initialisation, an example config with explanation can be found
    above.

    The class utilises the following internal parameters to hold information about the maze:
        self.maze: a 3D integer array that stores the most native maze layout. The maze is consisted of rooms with
        different sizes, each room has a unique id, and occupies a cube shape space in the maze. Self.maze contains
        the room ids of the room each cell belongs to. The start room is always room 0, and the goal room is -1.

        self.rooms: a dictionary to quickly reference a room by its ID.

        self.paths: a dictionary to describe the connectivity of the rooms. Some neighbouring rooms are connected
        by a door, and the doors are randomly generated such that all the rooms are connected in a spanning tree
        fashion, with the start room as the root. Self.paths describes such a tree, its keys are room ids, and the
        values are the room's corresponding parent room id in the spanning tree.

        self.doors: a dictionary to quickly reference the doors by its location (x, y, z).

        self.solution_path: a list of room ids that leads from start room to the goal room.

    The class provides some utility functions to print the information about the maze:
        print_grid(): it simply prints the maze in its native form, i.e. printing self.maze layer by layer.

        print_solution_path(): it prints the room ids in the self.solution_path to show the correct path to goal.

        print_floor_plan(): it prints the maze layout, including walls, doors, ceiling/floors etc. Optionally it
        can also print the solution path in the layout, indicated by arrows at doors.

    The input config should have the following keys:
        maze_size: a tuple of three values to represent the total size of the maze in the (height, rows, columns) format.
        start_loc: start room's highest top left corner cell, represented as its index in a tuple.
        start_room_size: the size of the start room, represented as a tuple of 3 values on the 3 dimensions.
        goal_loc: goal room's starting location, a tuple of 3 values.
        goal_room_size: goal room's size, a tuple of 3 values.
        max_room_size: maximum size of each dimension for any room in the maze. A tuple of 3 values.

    """
    def __init__(self, config: Dict):
        self.config = config
        self.mh, self.mr, self.mc = self.config["maze_size"]
        self.rooms: Dict[int, Room] = {}
        self.paths: Dict[int, int] = {}
        self.doors: Dict[Tuple[int, int, int], Set[int]] = {}
        self.solution_path: List[int] = []
        # initialise the maze grid
        self._init_maze()
        # randomly fill the maze with rooms
        self._generate_rooms()
        # find all the neighbouring rooms, represented as a network (but not connecting them yet)
        self._generate_maze_network()
        # generate a spanning tree to connect all the rooms, with the start room as the root.
        self._generate_spanning_tree()

    def _init_maze(self):
        # Maze grid. Each cell will be filled with an integer corresponding to its room id.
        self.maze: List[List[List[int]]] = [[[None] * self.mc for _ in range(self.mr)] for _ in range(self.mh)]
        # The starting room has id 0
        self._set_room(self.config["start_loc"], self.config["start_room_size"], 0)
        # The goal room has id -1
        self._set_room(self.config["goal_loc"], self.config["goal_room_size"], -1)

    def _set_room(self, loc: Tuple[int, int, int], size: Tuple[int, int, int], id: int):
        """
        Create a room with specified location and size, and set all the cell values in the grid with id.
        Args:
            loc: A tuple of the start location of the room.
            size: A tuple of the size of the room
            id: The id of the room
        """
        for hi in range(loc[0], loc[0] + size[0]):
            for ri in range(loc[1], loc[1] + size[1]):
                for ci in range(loc[2], loc[2] + size[2]):
                    self.maze[hi][ri][ci] = id
        self.rooms[id] = Room(loc, size, id)

    def print_grid(self):
        """
        Utility function for printing the grid values (room ids) layer by layer.
        """
        for hi in range(self.mh):
            for ri in range(self.mr):
                for ci in range(self.mc):
                    print(self.maze[hi][ri][ci], end="\t")
                print()
            print("===============================================")

    def _generate_rooms(self):
        """
        First step of generating a maze: fill the grid with rooms with random sizes.
        Each room is limited by the maximum size in the config. The smallest room can be 1x1x1.
        A chain of 1x1x1 rooms can be seen as a hallway, therefore it is not necessary to have a hallway type of room.
        """
        room_id = 1
        # iterate over all cells in the maze, floor by floor, and try to fill them with rooms
        for hi in range(self.mh):
            for ri in range(self.mr):
                for ci in range(self.mc):
                    # skip the cell if it is already occupied by a room
                    if self.maze[hi][ri][ci] is not None:
                        continue
                    # explore downwards to see the maximum height we can fit a room in.
                    max_room_h = 1
                    while max_room_h < self.config["max_room_size"][0] and hi + max_room_h < self.mh and self.maze[hi + max_room_h][ri][ci] is None:
                        max_room_h += 1
                    # determine the room height randomly within the limit
                    room_h = random.randint(1, max_room_h)
                    # now we have determined the height of the room, we can explore horizontally to determine the max row and columns we can fit a room in.
                    max_room_r = 1
                    while max_room_r < self.config["max_room_size"][1] and ri + max_room_r < self.mr:
                        can_fill = True
                        for hj in range(room_h):
                            if self.maze[hi + hj][ri + max_room_r][ci] is not None:
                                can_fill = False
                                break
                        if not can_fill:
                            break
                        max_room_r += 1
                    room_r = random.randint(1, max_room_r)
                    if room_h == room_r == 1:
                        max_room_c = 1
                        while max_room_c < self.config["max_room_size"][2] and ci + max_room_c < self.mc and self.maze[hi][ri][ci + max_room_c] is None:
                            max_room_c += 1
                        room_c = random.randint(1, max_room_c)
                    elif room_h == 1 or room_r == 1:
                        room_c = 1
                        if hi == self.mh - 1 or ri == self.mr - 1:
                            while room_c < self.config["max_room_size"][2] and ci + room_c < self.mc:
                                can_fill = True
                                for hj in range(room_h):
                                    for rj in range(room_r):
                                        if self.maze[hi + hj][ri + rj][ci + room_c] is not None:
                                            can_fill = False
                                            break
                                    if not can_fill:
                                        break
                                if not can_fill:
                                    break
                                room_c += 1
                    else:
                        max_room_c = 1
                        while max_room_c < self.config["max_room_size"][2] and ci + max_room_c < self.mc:
                            can_fill = True
                            for hj in range(room_h):
                                for rj in range(room_r):
                                    if self.maze[hi + hj][ri + rj][ci + max_room_c] is not None:
                                        can_fill = False
                                        break
                                if not can_fill:
                                    break
                            if not can_fill:
                                break
                            max_room_c += 1
                        room_c = random.randint(1, max_room_c)
                    # fill the grid with the room
                    self._set_room((hi, ri, ci), (room_h, room_r, room_c), room_id)
                    room_id += 1

    def _generate_maze_network(self):
        """
        Second step of generating a maze: find the neighbours of all the rooms.
        A room is a neighbour if it shares a wall with the current room.
        This effectively generate a network where each node is a room, and each edge representing the two rooms on
        both sides are neighbours.
        Later, we can generate a spanning tree in the network to generate paths in the maze.
        """
        for room in self.rooms.values():
            # directions: 0=h-1, 1=h+1, 2=r-1, 3=r+1, 4=c-1, 5=c+1
            direction = 0
            if room.loc[0] > 0:
                for ri in range(room.loc[1], room.loc[1] + room.size[1]):
                    for ci in range(room.loc[2], room.loc[2] + room.size[2]):
                        neighbor = self.rooms[self.maze[room.loc[0] - 1][ri][ci]]
                        room.add_neighbor(neighbor, direction)
            direction = 1
            if room.loc[0] + room.size[0] < self.mh:
                for ri in range(room.loc[1], room.loc[1] + room.size[1]):
                    for ci in range(room.loc[2], room.loc[2] + room.size[2]):
                        neighbor = self.rooms[self.maze[room.loc[0] + room.size[0]][ri][ci]]
                        room.add_neighbor(neighbor, direction)
            direction = 2
            if room.loc[1] > 0:
                for hi in range(room.loc[0], room.loc[0] + room.size[0]):
                    for ci in range(room.loc[2], room.loc[2] + room.size[2]):
                        neighbor = self.rooms[self.maze[hi][room.loc[1] - 1][ci]]
                        room.add_neighbor(neighbor, direction)
            direction = 3
            if room.loc[1] + room.size[1] < self.mr:
                for hi in range(room.loc[0], room.loc[0] + room.size[0]):
                    for ci in range(room.loc[2], room.loc[2] + room.size[2]):
                        neighbor = self.rooms[self.maze[hi][room.loc[1] + room.size[1]][ci]]
                        room.add_neighbor(neighbor, direction)
            direction = 4
            if room.loc[2] > 0:
                for hi in range(room.loc[0], room.loc[0] + room.size[0]):
                    for ri in range(room.loc[1], room.loc[1] + room.size[1]):
                        neighbor = self.rooms[self.maze[hi][ri][room.loc[2] - 1]]
                        room.add_neighbor(neighbor, direction)
            direction = 5
            if room.loc[2] + room.size[2] < self.mc:
                for hi in range(room.loc[0], room.loc[0] + room.size[0]):
                    for ri in range(room.loc[1], room.loc[1] + room.size[1]):
                        neighbor = self.rooms[self.maze[hi][ri][room.loc[2] + room.size[2]]]
                        room.add_neighbor(neighbor, direction)

    def _generate_spanning_tree(self):
        """
        Last step of generating a maze: create paths from start room to goal room.
        It starts with a random walk DFS to find a path from start room to goal room.
        A door is created between neighbouring rooms on each step.
        After a path is created, it randomly expands the tree to gradually connect all the rooms, which will
        generate random dead ends in the maze.
        The maze generated in this way will be a tree structure, i.e. there is no loop in the maze.
        """
        # Random Depth-First Search to generate a path to the goal
        # this is also the solution path to the goal.
        stack: List[Room] = [self.rooms[0]]
        visited = set(stack)
        while stack:
            room = stack[-1]
            if room.id == -1:
                stack.pop()
                break
            neighbors = [n for n in room.neighbors if n not in visited]
            if neighbors:
                neighbor = random.choice(neighbors)
                stack.append(neighbor)
                visited.add(neighbor)
                self.paths[neighbor.id] = room.id
                # add door
                self._add_door(room, neighbor)
            else:
                stack.pop()
        # randomly expand the tree
        while stack:
            i = random.randint(0, len(stack) - 1)
            room = stack[i]
            neighbors = [n for n in room.neighbors if n not in visited]
            if neighbors:
                neighbor = random.choice(neighbors)
                stack.append(neighbor)
                visited.add(neighbor)
                self.paths[neighbor.id] = room.id
                # add door
                self._add_door(room, neighbor)
            else:
                stack.pop(i)
        # walk backwards from the goal room to record the correct path.
        self.solution_path = [-1]
        while self.solution_path[0] != 0:
            self.solution_path.insert(0, self.paths[self.solution_path[0]])

    def _add_door(self, room1: Room, room2: Room):
        """
        Utility function for adding a door between two neighbouring rooms.
        If there are multiple cells that could fit a door, use a random one, except that the door is always
        at the lowest height.
        Args:
            room1: first room.
            room2: second room.
        """
        direction = room1.neighbors_directions[room1.neighbors.index(room2)]
        if direction % 2 == 0:
            room1, room2 = room2, room1
        door_direction = direction // 2
        if door_direction == 0:
            dr0 = max(room1.loc[1], room2.loc[1])
            dr1 = min(room1.loc[1] + room1.size[1], room2.loc[1] + room2.size[1])
            door_r = random.randint(dr0, dr1 - 1)
            dc0 = max(room1.loc[2], room2.loc[2])
            dc1 = min(room1.loc[2] + room1.size[2], room2.loc[2] + room2.size[2])
            door_c = random.randint(dc0, dc1 - 1)
            door_h = room1.loc[0] + room1.size[0] - 1
        elif door_direction == 1:
            door_h = min(room1.loc[0] + room1.size[0], room2.loc[0] + room2.size[0]) - 1
            dc0 = max(room1.loc[2], room2.loc[2])
            dc1 = min(room1.loc[2] + room1.size[2], room2.loc[2] + room2.size[2])
            door_c = random.randint(dc0, dc1 - 1)
            door_r = room1.loc[1] + room1.size[1] - 1
        else:
            door_h = min(room1.loc[0] + room1.size[0], room2.loc[0] + room2.size[0]) - 1
            dr0 = max(room1.loc[1], room2.loc[1])
            dr1 = min(room1.loc[1] + room1.size[1], room2.loc[1] + room2.size[1])
            door_r = random.randint(dr0, dr1 - 1)
            door_c = room1.loc[2] + room1.size[2] - 1
        if (door_h, door_r, door_c) not in self.doors:
            self.doors[(door_h, door_r, door_c)] = set()
        self.doors[(door_h, door_r, door_c)].add(door_direction)
        room1.add_door(room2, (door_h, door_r, door_c), door_direction * 2 + 1)
        if door_direction == 0:
            door_h += 1
        elif door_direction == 1:
            door_r += 1
        else:
            door_c += 1
        room2.add_door(room1, (door_h, door_r, door_c), door_direction * 2)

    def print_solution_path(self):
        """
        Print the solution path as a chain of rooms (ids) along the path.
        """
        print(f"{len(self.solution_path) - 1} steps:")
        for room in self.solution_path[:-1]:
            print(room, end=" -> ")
        print(self.solution_path[-1])

    def print_floor_plan(self, print_solution_path=True):
        """
        Utility function for printing the floor plan, including all the floors and walls.
        If there is a door, it is left as empty. Each cell is represented by two characters, and each wall
        is represented by a charactor.
        If print_solution_path is True, it also prints the solution path on the floor plan as the directions
        to the next room on the path.
        Args:
            print_solution_path: whether to print the solution path on the floor plan.
        """
        floor_plan: List[List[str]] = [[] for _ in range(self.mh)]
        for hi in range(self.mh):
            # top boarder row
            row_str = '┌'
            for ci in range(self.mc - 1):
                if self.maze[hi][0][ci] == self.maze[hi][0][ci + 1]:
                    row_str += '───'
                else:
                    row_str += '──┬'
            row_str += '──┐'
            floor_plan[hi].append(row_str)
            for ri in range(self.mr):
                # room floor row
                row_str = '│'
                for ci in range(self.mc):
                    if (hi < self.mh - 1 and self.maze[hi][ri][ci] == self.maze[hi + 1][ri][ci]) or ((hi, ri, ci) in self.doors and 0 in self.doors[(hi, ri, ci)]):
                        row_str += '  '
                    else:
                        row_str += '██'
                    if (ci < self.mc - 1 and self.maze[hi][ri][ci] == self.maze[hi][ri][ci + 1]) or ((hi, ri, ci) in self.doors and 2 in self.doors[(hi, ri, ci)]):
                        row_str += ' '
                    else:
                        row_str += '│'
                floor_plan[hi].append(row_str)
                if ri < self.mr - 1:
                    # room boarder row
                    row_str = '│' if self.maze[hi][ri][0] == self.maze[hi][ri + 1][0] else '├'
                    for ci in range(self.mc):
                        if self.maze[hi][ri][ci] == self.maze[hi][ri + 1][ci] or ((hi, ri, ci) in self.doors and 1 in self.doors[(hi, ri, ci)]):
                            row_str += '  '
                        else:
                            row_str += '──'
                        if ci == self.mc - 1:
                            row_str += '│' if self.maze[hi][ri][ci] == self.maze[hi][ri + 1][ci] else '┤'
                        elif self.maze[hi][ri][ci] == self.maze[hi][ri + 1][ci + 1]:
                            row_str += ' '
                        elif self.maze[hi][ri][ci] == self.maze[hi][ri + 1][ci]:
                            row_str += '│' if self.maze[hi][ri][ci + 1] == self.maze[hi][ri + 1][ci + 1] else '├'
                        elif self.maze[hi][ri][ci] == self.maze[hi][ri][ci + 1]:
                            row_str += '─' if self.maze[hi][ri + 1][ci] == self.maze[hi][ri + 1][ci + 1] else '┬'
                        elif self.maze[hi][ri + 1][ci] == self.maze[hi][ri + 1][ci + 1]:
                            row_str += '┴'
                        elif self.maze[hi][ri][ci + 1] == self.maze[hi][ri + 1][ci + 1]:
                            row_str += '┤'
                        else:
                            row_str += '┼'
                    floor_plan[hi].append(row_str)
            # bottom boarder row
            row_str = '└'
            for ci in range(self.mc - 1):
                if self.maze[hi][self.mr - 1][ci] == self.maze[hi][self.mr - 1][ci + 1]:
                    row_str += '───'
                else:
                    row_str += '──┴'
            row_str += '──┘'
            floor_plan[hi].append(row_str)
        if print_solution_path:
            direction_chars = '↥↧↑↓←→'
            prev_room = self.rooms[self.solution_path[0]]
            for room_id in self.solution_path[1:]:
                room = self.rooms[room_id]
                (hi, ri, ci), direction = prev_room.doors[room]
                fpi, fpj, fpk = hi, ri * 2 + 1, ci * 3 + 1
                fpk += direction % 2
                floor_plan[fpi][fpj] = floor_plan[fpi][fpj][:fpk] + direction_chars[direction] + floor_plan[fpi][fpj][fpk + 1:]
                prev_room = room
        print('\n\n'.join(['\n'.join(floor_plan[hi]) for hi in range(self.mh)]))
