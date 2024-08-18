from typing import List, Tuple, Dict


class Room:
    """
    A room in the maze, represented by the start location (a tuple of 3 values), the size on the three dimensions
    (a tuple of 3 values), and its unique id.
    """
    def __init__(self, loc: Tuple[int, int, int], size: Tuple[int, int, int], id: int):
        self.loc = loc
        self.size = size
        self.id = id
        # a list of it's neighbours that share a wall with this room
        self.neighbors: List[Room] = []
        # the directions of all its neighbours, it can be up/down/left/right/forward/backward
        self.neighbors_directions: List[int] = []
        # a list of doors, represented as a dictionary of neighbour-room: (door location cell, direction)
        self.doors: Dict[Room, Tuple[Tuple[int, int, int], int]] = {}

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def add_neighbor(self, room: 'Room', direction: int):
        if room not in self.neighbors:
            self.neighbors.append(room)
            self.neighbors_directions.append(direction)

    def add_door(self, neighbor: 'Room', door_loc: Tuple[int, int, int], door_direction: int):
        self.doors[neighbor] = (door_loc, door_direction)