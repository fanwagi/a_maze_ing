from maze import Maze, example_config


def main():
    m = Maze(example_config)
    m.print_floor_plan()
    m.print_solution_path()


if __name__ == '__main__':
    main()
