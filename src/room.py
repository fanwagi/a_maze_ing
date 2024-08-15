from typing import List, Tuple, Dict


class Room:
    def __init__(self, loc: Tuple[int, int, int], size: Tuple[int, int, int], id: int):
        self.loc = loc
        self.size = size
        self.id = id
        self.neighbors: List[Room] = []
        self.neighbors_directions: List[int] = []
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