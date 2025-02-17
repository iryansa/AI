import re

# Global variables
robots_start = []
robots_goal = []
num_robots = 0
num_agents = 0
agents_locations = []
agents_times = []

robots_curr_pos = []
curr_time = 0

main_grid = []

def read_input(grid_file, robots_file, agents_file):
    global main_grid, robots_start, robots_goal, num_robots, num_agents, agents_locations, agents_times

    # Read grid
    with open(grid_file, "r") as file:
        num_rows = int(file.readline())
        main_grid = [file.readline()[:-1] for _ in range(num_rows)]

    # Read robots
    with open(robots_file, "r") as file:
        lines = file.readlines()
        num_robots = len(lines)
        for line in lines:
            positions = re.findall(r'\d+', line)
            if positions:
                start_x, start_y = int(positions[1]), int(positions[2])
                goal_x, goal_y = int(positions[3]), int(positions[4])
                robots_start.append([start_x, start_y])
                robots_goal.append([goal_x, goal_y])

    # Read agents
    with open(agents_file, "r") as file:
        lines = file.readlines()
        num_agents = len(lines)
        for line in lines:
            coord_matches = re.findall(r'\((\d+), (\d+)\)', line)
            time_matches = re.findall(r'\d+', line.split("at times")[-1])
            if coord_matches and time_matches:
                agents_locations.append([[int(x), int(y)] for x, y in coord_matches])
                agents_times.append([int(t) for t in time_matches])

def heuristic(robot_num, move):
    global robots_curr_pos, robots_goal, curr_time

    # Calculate new position
    new_pos = robots_curr_pos[robot_num].copy()
    if move == 1:
        new_pos[0] -= 1
    elif move == 2:
        new_pos[0] += 1
    elif move == 3:
        new_pos[1] -= 1
    elif move == 4:
        new_pos[1] += 1

    # Calculate Manhattan distance + time
    return abs(new_pos[0] - robots_goal[robot_num][0]) + abs(new_pos[1] - robots_goal[robot_num][1]) + curr_time + 1

def movement_permit(movement_list):
    global robots_curr_pos, num_robots

    # Calculate new positions
    new_positions = [robots_curr_pos[i].copy() for i in range(num_robots)]
    for i in range(num_robots):
        move = movement_list[i]
        if move == 1:
            new_positions[i][0] -= 1
        elif move == 2:
            new_positions[i][0] += 1
        elif move == 3:
            new_positions[i][1] -= 1
        elif move == 4:
            new_positions[i][1] += 1

    # Check for collisions
    return [new_positions.count(new_positions[i]) == 1 for i in range(num_robots)]

def simulation():
    global robots_curr_pos, curr_time, num_robots, num_agents, agents_locations, agents_times, main_grid

    robots_path = [[] for _ in range(num_robots)]
    robots_curr_pos = [pos.copy() for pos in robots_start]

    while True:
        best_moves = [0] * num_robots
        notpermittedlist = [[] for _ in range(num_robots)]

        for i in range(num_robots):
            if robots_curr_pos[i] == robots_goal[i]:
                continue

            possible_moves = []
            if robots_curr_pos[i][0] > 0 and main_grid[robots_curr_pos[i][0] - 1][robots_curr_pos[i][1]] != 'X':
                possible_moves.append(1)
            if robots_curr_pos[i][0] < len(main_grid) - 1 and main_grid[robots_curr_pos[i][0] + 1][robots_curr_pos[i][1]] != 'X':
                possible_moves.append(2)
            if robots_curr_pos[i][1] > 0 and main_grid[robots_curr_pos[i][0]][robots_curr_pos[i][1] - 1] != 'X':
                possible_moves.append(3)
            if robots_curr_pos[i][1] < len(main_grid[0]) - 1 and main_grid[robots_curr_pos[i][0]][robots_curr_pos[i][1] + 1] != 'X':
                possible_moves.append(4)

            # Filter out moves that collide with agents
            for move in possible_moves.copy():
                new_pos = robots_curr_pos[i].copy()
                if move == 1:
                    new_pos[0] -= 1
                elif move == 2:
                    new_pos[0] += 1
                elif move == 3:
                    new_pos[1] -= 1
                elif move == 4:
                    new_pos[1] += 1

                for j in range(num_agents):
                    if agents_times[j][curr_time + 1] == new_pos[0] and agents_locations[j][curr_time + 1] == new_pos[1]:
                        possible_moves.remove(move)
                        break

            if possible_moves:
                best_moves[i] = min(possible_moves, key=lambda move: heuristic(i, move))

        # Validate movements
        notpermitted = movement_permit(best_moves)
        for i in range(num_robots):
            if notpermitted[i]:
                notpermittedlist[i].append(best_moves[i])

        # Move robots
        for i in range(num_robots):
            if notpermitted[i]:
                continue
            move = best_moves[i]
            if move == 1:
                robots_curr_pos[i][0] -= 1
            elif move == 2:
                robots_curr_pos[i][0] += 1
            elif move == 3:
                robots_curr_pos[i][1] -= 1
            elif move == 4:
                robots_curr_pos[i][1] += 1
            robots_path[i].append(robots_curr_pos[i].copy())

        curr_time += 1

        # Check if all robots have reached their goals
        if all(robots_curr_pos[i] == robots_goal[i] for i in range(num_robots)):
            break

    # Print results
    for i in range(num_robots):
        print(f"Robot {i} Path: {robots_path[i]}")
        print(f"Time taken: {len(robots_path[i])}")
    print(f"Total time taken: {curr_time}")

# Example usage
read_input("Data/testD.txt", "Data/testR.txt", "Data/testA.txt")
print("Grid:")
for row in main_grid:
    print(row)

print()

simulation()