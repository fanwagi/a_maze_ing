# 3D Maze Generator

## Overview
This Python program generates a random 3D maze based on customizable configurations. The generated maze consists of interconnected rooms of varying sizes, each of which is in a cube-like shape. The start and goal rooms are predefined, and the program ensures that all rooms are connected via doors. A solution path from the start room to the goal room is automatically generated using a random depth-first search algorithm.

## Features
- **Random Room Generation**: Rooms of varying sizes are randomly placed in the maze, each having a unique ID.
- **Spanning Tree Connectivity**: Rooms are connected in a tree-like structure, ensuring all rooms are reachable from the start.
- **Solution Path**: A path from the start room to the goal room is calculated and can be displayed.
- **Customizable Configuration**: The maze can be customized by changing the size, start location, goal location, room sizes, and more.
- **Floor Plan and Grid Representation**: The program can output a visual representation of the maze in both a grid and floor plan format.
- **Doors and Walls**: Doors are randomly generated between rooms, ensuring connectivity.

## Usage
To use this program, you need to define a configuration dictionary specifying the maze dimensions, start and goal room locations, room sizes, etc. An example configuration is provided below:

```python
example_config = {
    "maze_size": (2, 9, 9),  # (height, rows, columns)
    "start_loc": (0, 3, 3),  # start room will be (loc0: loc0+size0, loc1: loc1+size1, loc2: loc2+size2)
    "start_room_size": (1, 3, 3),
    "goal_loc": (0, 0, 0),   # goal room will be (loc0: loc0+size0, loc1: loc1+size1, loc2: loc2+size2)
    "goal_room_size": (1, 1, 1),
    "max_room_size": (2, 2, 2),   # the maximum size of any room on each dimension
}
```

### Key Classes
- **Maze**: Handles the generation of the maze, rooms, doors, and solution path. This class includes methods to:
  - Generate random rooms and connect them using a spanning tree.
  - Print a grid or a floor plan of the maze.
  - Print the solution path from start to goal.

- **Room**: Represents a single room in the maze. A room has a location, size, and can have doors that connect it to neighboring rooms.

### Maze Output
The `Maze` class provides several methods to visualize the maze:
- `print_grid()`: Displays the maze in a grid format, showing which rooms occupy which parts of the maze.
- `print_floor_plan()`: Displays a floor plan view of the maze, optionally showing the solution path.
- `print_solution_path()`: Prints the sequence of rooms that form the solution path from the start room to the goal.

### Example Usage
```python
from maze import Maze, example_config

# Create a maze with the example configuration
maze = Maze(example_config)

# Print the maze in grid form
maze.print_grid()

# Print the solution path
maze.print_solution_path()

# Print the maze's floor plan
maze.print_floor_plan()
```

### Customization
You can modify the maze configuration to suit your needs:
- **maze_size**: Adjust the height, number of rows, and number of columns in the maze.
- **start_loc** and **start_room_size**: Define where the start room is located and its size.
- **goal_loc** and **goal_room_size**: Set the location and size of the goal room.
- **max_room_size**: Limit the size of any generated room to avoid creating rooms that are too large.

## How to run the code
1. Clone this repository.
2. Go to the src folder:
```commandline
cd src
```
3. Run the example main file:
```commandline
python main.py
```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
