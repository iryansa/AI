# S Ahmad Ryan
# 22i-0781
# AI assignment 1

import re
import heapq
from collections import defaultdict

# Global variables
starts = []
goals = []
num_robots = 0
num_agents = 0
dynamic_agents = []
agents_times = []

robots_curr_pos = []
curr_time = 0
time_dict = {}

grid = []

def read_input(grid_file, robots_file, agents_file):
    global grid, starts, goals, num_robots, num_agents, dynamic_agents, agents_times

    # Read grid
    with open(grid_file, "r") as file:
        # num_rows = int(file.readline())
        # grid = [file.readline()[:-1] for _ in range(num_rows)]
        num_rows = int(file.readline())
        # grid = [[char for char in file.readline()[:-1]] for _ in range(num_rows)]
        for _ in range(num_rows):
            grid_row = []
            line = file.readline()
            for char in line[:-1]:
                if char == 'X':
                    grid_row.append('X')
                elif char == ' ':
                    grid_row.append('.')
            grid.append(grid_row) 

    # Read robots
    with open(robots_file, "r") as file:
        lines = file.readlines()
        num_robots = len(lines)
        for line in lines:
            positions = re.findall(r'\d+', line)
            if positions:
                start_x, start_y = int(positions[1]), int(positions[2])
                goal_x, goal_y = int(positions[3]), int(positions[4])
                starts.append((start_x, start_y))
                goals.append((goal_x, goal_y))

    # Read agents
    with open(agents_file, "r") as file:
        lines = file.readlines()
        num_agents = len(lines)
        for line in lines:
            coord_matches = re.findall(r'\((\d+), (\d+)\)', line)
            time_matches = re.findall(r'\d+', line.split("at times")[-1])
            if coord_matches and time_matches:
                dynamic_agents.append([[int(x), int(y)] for x, y in coord_matches])
                agents_times.append([int(t) for t in time_matches])


    # Store the locations of dynamic agents at their times in the time_dict dictionary
    for i in range(len(dynamic_agents)):  # Use len(dynamic_agents) instead of num_agents
        for time, loc in zip(agents_times[i], dynamic_agents[i]):
            if time not in time_dict:
                time_dict[time] = []
            time_dict[time].append(loc)


def heuristic(a, b):
    """Calculate the Manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_cell_safe(x, y, t, dynamic_agents):
    """Check if the cell (x, y) is safe at time t (not occupied by any dynamic agent)."""
    if t in time_dict and [x, y] in time_dict[t]:
        return False
    return True

def a_star(grid, start, goal, dynamic_agents, max_time=1000):
    """A* algorithm with dynamic agents."""
    # Define possible movements (up, down, left, right)
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    # Initialize the open and closed sets
    open_set = []
    heapq.heappush(open_set, (0, (start[0], start[1], 0)))  # (f_score, (x, y, t))
    came_from = {}
    g_score = {(start[0], start[1], 0): 0}
    f_score = {(start[0], start[1], 0): heuristic(start, goal)}
    
    while open_set:
        # Get the node with the lowest f_score
        current_f, current_state = heapq.heappop(open_set)
        x, y, t = current_state
        # print(current_state)
        # If we've reached the goal, reconstruct the path
        if (x, y) == goal:
            path = []
            while (x, y, t) in came_from:
                path.append((x, y, t))
                x, y, t = came_from[(x, y, t)]
            path.append((start[0], start[1], 0))
            return path[::-1]  # Return reversed path
        
        # If we've exceeded the maximum time, terminate
        if t >= max_time:
            continue
        
        # Explore neighbors
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            nt = t + 1  # Time increases by 1 for each move
            
            # Check if the neighbor is within the grid boundaries
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                # Check if the neighbor is not an obstacle and is safe at time nt
                if grid[nx][ny] == 'X' or not is_cell_safe(nx, ny, nt, dynamic_agents):
                    continue
                
                # Calculate tentative g_score
                tentative_g_score = g_score[(x, y, t)] + 1
                
                if (nx, ny, nt) not in g_score or tentative_g_score < g_score[(nx, ny, nt)]:
                    # This path to the neighbor is better than any previous one
                    came_from[(nx, ny, nt)] = (x, y, t)
                    g_score[(nx, ny, nt)] = tentative_g_score
                    f_score[(nx, ny, nt)] = tentative_g_score + heuristic((nx, ny), goal)
                    heapq.heappush(open_set, (f_score[(nx, ny, nt)], (nx, ny, nt)))
    
    # If the open set is empty and the goal was never reached, return failure
    return [(-1, -1, 0)]  # Return a path with invalid coordinates and time

def resolve_conflicts(robot_paths):
    """Resolve conflicts between robot paths."""
    max_time = max(len(path) for path in robot_paths)
    for t in range(max_time):
        # Track occupied cells at time t
        occupied = defaultdict(list)
        for robot_id, path in enumerate(robot_paths):
            if t < len(path):
                x, y, _ = path[t]  # Unpack (x, y, t) and ignore t
                occupied[(x, y)].append(robot_id)
        
        # Collect conflicts
        conflicts = []
        for cell, robots in occupied.items():
            if len(robots) > 1:
                conflicts.append((cell, robots))
        
        # Resolve conflicts
        for cell, robots in conflicts:
            # Allow the first robot to move, and reroute the others
            for robot_id in robots[1:]:
                # Find an alternative move for the conflicting robot
                x_prev, y_prev, _ = robot_paths[robot_id][t - 1]  # Unpack (x, y, t) and ignore t
                neighbors = [(x_prev + dx, y_prev + dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]]
                for nx, ny in neighbors:
                    if (nx, ny) not in occupied:
                        robot_paths[robot_id][t] = (nx, ny, t)  # Update with time component
                        occupied[(nx, ny)].append(robot_id)
                        break
                else:
                    # No alternative move found, stay in place
                    robot_paths[robot_id][t] = (x_prev, y_prev, t)  # Update with time component
    return robot_paths

def plan_robot_movements(grid, starts, goals, dynamic_agents):
    """Plan movements for multiple robots."""
    robot_paths = []
    for start, goal in zip(starts, goals):
        path = a_star(grid, start, goal, dynamic_agents)
        robot_paths.append(path)
    
    # Resolve conflicts between robot paths
    robot_paths = resolve_conflicts(robot_paths)
    
    return robot_paths


num = int(input("Enter test number: "))
data_name = f"Data/data{num}.txt"
robots_name = f"Data/Robots{num}.txt"
agents_name = f"Data/Agent{num}.txt"

read_input(data_name, robots_name, agents_name)

# Plan movements for all robots
robot_paths = plan_robot_movements(grid, starts, goals, dynamic_agents)

# Print the paths
for robot_id, path in enumerate(robot_paths):
    print(f"Robot {robot_id} path:")
    for x, y, t in path:
        # print(f"({x}, {y}) at time {t}", end=" -> ")
        print(f"({x}, {y}) ", end="->")
    print("Total time = ", t)
    print()
    print()

