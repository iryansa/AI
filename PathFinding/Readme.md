# Multi-Robot Pathfinding in a Dynamic Environment

## Problem Description

An algorithm is designed to find the optimal path for multiple robots in a dynamic, partially observable environment. Each robot navigates a grid-based map while avoiding collisions with obstacles, dynamic agents, and other robots. The environment includes the following elements:

### Grid Representation
- The map is an N x M grid, where each cell can be:
    - **Free**: The robot can move through this cell.
    - **Obstacle**: The robot cannot move through this cell.
    - **Dynamic Obstacle**: A moving agent that occupies a cell for a certain time interval.
    - **Goal**: The destination the robot must reach.
- Minimum grid size: 4x4

### Robot Movement
- Each robot moves in four directions: up, down, left, and right.
- Each move takes 1 unit of time.
- Robots cannot move into a cell occupied by an obstacle, a dynamic agent, or another robot at the same time.

### Dynamic Agents
- There are K dynamic agents moving on the grid.
- Each agent follows a predefined path and occupies a sequence of cells at specific time steps.
- The paths of the agents are known in advance.
- Minimum number of agents: 2

### Multiple Robots
- There are R robots, each starting at a unique position on the grid.
- Each robot has its own goal position.
- Robots do not know the paths of other robots and must plan their paths independently.
- If two robots collide (occupy the same cell at the same time), both robots will randomly change direction and retry their movement.
- Minimum number of robots: 2

### Objective
- The shortest path is found for each robot from its starting position to its goal, avoiding collisions with obstacles, dynamic agents, and other robots.
- The paths are optimal in terms of both time and distance.

### Constraints
- Each robot starts at time t = 0.
- Robots cannot wait in a cell (they must move at every time step).
- The algorithm handles large grids (N and M up to 1000), a large number of dynamic agents (K up to 100), and multiple robots (R up to 10).
- If the goal state is an obstacle, it will not have a valid path.

## Algorithm Requirements
A hybrid algorithm is designed to solve this problem efficiently. The algorithm:
1. Explores the grid and identifies potential paths while considering the dynamic agents' movements and the presence of other robots.
2. Prioritizes paths that are more likely to lead to the goal, using a heuristic function that accounts for both distance and time.
3. Handles the dynamic nature of the environment by updating the grid state at each time step.
4. Simulates the behavior of other robots by predicting their possible movements and avoiding collisions.
5. Implements a collision resolution mechanism where robots randomly change direction upon collision.

## Input
- A 2D grid representing the map (N x M).
- The starting positions of the R robots.
- The goal positions for each robot.
- A list of K dynamic agents, each with a predefined path (a sequence of cells and the time steps at which they occupy those cells).

## Output
- The optimal path for each robot as a sequence of cells from the start to the goal.
- The total time taken for each robot to reach its goal.
