# S. Ahmad Ryan
# 22i-0781
# CS-B
# Assignment # 1
# Artificial Intellegence

import re

robots_start = []
robots_goal = []
num_robots = 0
num_agents = 0
agents_locations = []
agents_times = []

robots_curr_pos = []
curr_time = 0

main_grid = []

def read_input():
    global main_grid
    # will have to change the names of files here for different inputs
    # grid_file = open("Data/data0.txt", "r")
    grid_file = open("Data/testD.txt", "r")
    # read the number of the first line to get the number of rows of the grid
    num_rows = int(grid_file.readline())
    # read the remaining lines to get the grid (loop till num_rows) (removing the new line character)
    # not using the strip function as it was removing spaces as well, i dont know why
    for i in range(num_rows):
        main_grid.append(grid_file.readline()[:-1])
    # close the file
    grid_file.close()

    # for i in range(num_rows):
    #     print(main_grid[i])


####################################################

    # robots_file = open("Data/Robots0.txt", "r")
    robots_file = open("Data/testR.txt", "r")
    global num_robots
    global robots_start
    global robots_goal
    global robots_curr_pos
    # number of lines represent number of robots
    lines = robots_file.readlines()
    num_robots = len(lines)
    # removing the endline char from lines
    lines = [line[:-1] for line in lines]

    # print(num_robots)
    # for i in range(num_robots):
    #     print(lines[i])

    # Extracting the start and goal positions of the robots
    # using regex from re module (regular expression)
    for line in lines:
        positions = re.findall(r'\d+', line)
        
        if positions:
            start_x, start_y = int(positions[1]), int(positions[2])
            goal_x, goal_y = int(positions[3]), int(positions[4])
            
            robots_start.append([start_x, start_y])
            robots_goal.append([goal_x, goal_y])

    # close the file
    robots_file.close()

    # robots curr pos will be same as the start pos initially
    robots_curr_pos = [pos.copy() for pos in robots_start]


################################################## 


    # agents_file = open("Data/Agent0.txt", "r")
    agents_file = open("Data/testA.txt", "r")
    global num_agents
    global agents_locations
    global agents_times

    # number of lines represent number of agents
    lines = agents_file.readlines()
    num_agents = len(lines)
    # removing the endline char from lines
    lines = [line[:-1] for line in lines]

    # print(num_agents)

    # for i in range(num_agents):
    #     print(lines[i])

    # Process each line
    for line in lines:
        # Extract coordinates using regex
        coord_matches = re.findall(r'\((\d+), (\d+)\)', line)
        time_matches = re.findall(r'\d+', line.split("at times")[-1])  # Extract numbers after "at times"

        if coord_matches and time_matches:
            # Convert coordinate matches into a list of (x, y) pairs
            agent_path = [[int(x), int(y)] for x, y in coord_matches]
            agent_times = [int(t) for t in time_matches]

            # Append to lists
            agents_locations.append(agent_path)
            agents_times.append(agent_times)

    # Store the number of agents
    num_agents = len(agents_locations)

    # close the file
    agents_file.close()



#############################################################33

def heuristic(robot_num, movement):
    global robots_curr_pos
    global robots_goal
    global robots_start
    global curr_time

    # movement = 1 represents up, 2 represents down, 3 represents left, 4 represents right
    # check at that position in a local variable

    position = robots_curr_pos[robot_num].copy()
    time = curr_time + 1
    if movement == 1:
        position[0] -= 1
    elif movement == 2:
        position[0] += 1
    elif movement == 3:
        position[1] -= 1
    elif movement == 4:
        position[1] += 1
    elif movement == 0:
        position = robots_start[robot_num]
        time -= 1



    # calculate the manhattan distance + time taken to reach that position
    return abs(position[0] - robots_goal[robot_num][0]) + abs(position[1] - robots_goal[robot_num][1]) + time




def movement_permit(movement_list):
    # check if the movement is valid or not based on whether more than one robot is moving to the same position
    # or not
    # movement list will be a list of movements of all robots. 1 represents up, 2 represents down, 3 represents left, 4 represents right from current positions

    global robots_curr_pos
    global num_robots
    result_list = [False] * num_robots
    current_positions = robots_curr_pos.copy()
    for i in range(num_robots):
        if movement_list[i] == 1:
            current_positions[i][0] -= 1
        elif movement_list[i] == 2:
            current_positions[i][0] += 1
        elif movement_list[i] == 3:
            current_positions[i][1] -= 1
        elif movement_list[i] == 4:
            current_positions[i][1] += 1

    # like if robot 1 is at 0,0 and robot 2 is at 1,1 and robot 1 movement is down which will take it to 1,0 and robot 2 movement is left which will take it to 1,0 as well. thus we will store false for both robots else true
    for i in range(num_robots):
        if current_positions.count(current_positions[i]) > 1:
            result_list[i] = False
        else:
            result_list[i] = True

    return result_list



def simulation():
    
# all global variables
    global robots_curr_pos
    global curr_time
    global num_robots
    global num_agents
    global agents_locations
    global agents_times
    global main_grid

    # robots path will store the path of all robots to reach their goal positions
    robots_path = [[] for _ in range(num_robots)]
    robots_path_time = []

    # loop till all robots reach their goal positions
    while True:
        # best_moves will store the best move for each robot
        best_moves = [0] * num_robots   
        while True:
            flag = True
            # notpermitted will store the movements of robots which are not permitted. if a robot is not permiited to move in more than one directions then it will also store that
            notpermittedlist = [[] for _ in range(num_robots)]

    
            for i in range(num_robots):

                possible_moves = []
                # check if the robot has reached its goal position
                if robots_curr_pos[i] == robots_goal[i]:
                    continue
                # if robot is in the 0,0 position, it can only move down or right and so on
                if robots_curr_pos[i][0] == 0:
                    if 2 not in notpermittedlist[i]:
                        possible_moves.append(2)
                elif robots_curr_pos[i][0] == len(main_grid) - 1:
                    if 1 not in notpermittedlist[i]:
                        possible_moves.append(1)
                else:
                    if 1 not in notpermittedlist[i]:
                        possible_moves.append(1)
                    if 2 not in notpermittedlist[i]:
                        possible_moves.append(2)
                if robots_curr_pos[i][1] == 0:
                    if 4 not in notpermittedlist[i]:
                        possible_moves.append(4)
                elif robots_curr_pos[i][1] == len(main_grid[0]) - 1:
                    if 3 not in notpermittedlist[i]:
                        possible_moves.append(3)
                else:
                    if 3 not in notpermittedlist[i]:
                        possible_moves.append(3)
                    if 4 not in notpermittedlist[i]:
                        possible_moves.append(4)


                # remove those moves from possible moves which can cause collision with an agent at curr_time+1 or with an obstacle from main grid represented by X.
                for move in possible_moves:
                    if move == 1:
                        if main_grid[robots_curr_pos[i][0] - 1][robots_curr_pos[i][1]] == 'X':
                            possible_moves.remove(move)
                        for j in range(num_agents):
                            if agents_times[j][curr_time + 1] == robots_curr_pos[i][0] - 1 and agents_locations[j][curr_time + 1] == robots_curr_pos[i][1]:
                                possible_moves.remove(move)
                    elif move == 2:
                        if main_grid[robots_curr_pos[i][0] + 1][robots_curr_pos[i][1]] == 'X':
                            possible_moves.remove(move)
                        for j in range(num_agents):
                            if agents_times[j][curr_time + 1] == robots_curr_pos[i][0] + 1 and agents_locations[j][curr_time + 1] == robots_curr_pos[i][1]:
                                possible_moves.remove(move)
                    elif move == 3:
                        if main_grid[robots_curr_pos[i][0]][robots_curr_pos[i][1] - 1] == 'X':
                            possible_moves.remove(move)
                        for j in range(num_agents):
                            if agents_times[j][curr_time + 1] == robots_curr_pos[i][0] and agents_locations[j][curr_time + 1] == robots_curr_pos[i][1] - 1:
                                possible_moves.remove(move)
                    elif move == 4:
                        if main_grid[robots_curr_pos[i][0]][robots_curr_pos[i][1] + 1] == 'X':
                            possible_moves.remove(move)
                        for j in range(num_agents):
                            if agents_times[j][curr_time + 1] == robots_curr_pos[i][0] and agents_locations[j][curr_time + 1] == robots_curr_pos[i][1] + 1:
                                possible_moves.remove(move)
                # calculate the heuristic for all possible moves and select the best one and store in the best_moves list at robots index

                best_moves[i] = min(possible_moves, key=lambda move: heuristic(i, move))
                
            # check if the best moves are valid or not
            notpermitted = movement_permit(best_moves)

            # now that we know which moves are not permitted, we will store them in notpermittedlist. like if first robot is not permitted to move in 1 and 2 directions then we will store 1 and 2 in the list at index 0 ( meaning this list is 2D)
            for i in range(num_robots):
                if notpermitted[i] == False:
                    notpermittedlist[i].append(best_moves[i])
                    flag = False

            if flag == False:
                break
            # we will move all the robots to their best moves without checking for not permitted moves also add the new positions to the robot path list and increment the time
            for i in range(num_robots):
                if best_moves[i] == 1:
                    robots_curr_pos[i][0] -= 1
                elif best_moves[i] == 2:
                    robots_curr_pos[i][0] += 1
                elif best_moves[i] == 3:
                    robots_curr_pos[i][1] -= 1
                elif best_moves[i] == 4:
                    robots_curr_pos[i][1] += 1
            curr_time += 1
            robots_path.append(robots_curr_pos.copy())

        # check if all robots have reached their goal positions
        flag = True
        for i in range(num_robots):
            if robots_curr_pos[i] != robots_goal[i]:
                flag = False
                break
        if flag == True:
            break


    # print the path of all robots along with the time taken to reach the goal positions for each robot
    for i in range(num_robots):
        print("Robot", i, "Path:", robots_path[i])
        print("Time taken:", len(robots_path[i]))
        print()

    print("Total time taken:", curr_time)



read_input()
simulation()