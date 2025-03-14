import random
import heapq
from collections import defaultdict

def load_graph(filename):
    graph = defaultdict(list)
    heuristics = {}

    with open(filename, 'r') as file:
        first_line = file.readline().strip()
        if first_line.lower().startswith("source"):  # Skip header line
            pass
        
        for line in file:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            try:
                src, dest, heuristic = int(parts[0]), int(parts[1]), float(parts[2])
                graph[src].append(dest)
                graph[dest].append(src)
                heuristics[(src, dest)] = heuristic
                heuristics[(dest, src)] = heuristic
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")
    
    return graph, heuristics

def precompute_two_hop_neighbors(graph):
    """Precomputes two-hop neighbors for all nodes to speed up constraint checking."""
    two_hop_neighbors = {}
    for node in graph:
        neighbors = set(graph[node])
        two_hop = set()
        for neighbor in neighbors:
            two_hop.update(graph[neighbor])
        two_hop -= neighbors
        two_hop.discard(node)
        two_hop_neighbors[node] = two_hop
    return two_hop_neighbors

def initial_coloring(graph, two_hop_neighbors, preassigned_colors):
    coloring = {}
    available_colors = {}  # Track the lowest available color for each node
    
    for node in sorted(graph, key=lambda x: -len(graph[x])):
        if node in preassigned_colors:
            coloring[node] = preassigned_colors[node]
        else:
            used_colors = {coloring.get(neighbor) for neighbor in graph[node] if neighbor in coloring}
            used_colors |= {coloring.get(neighbor) for neighbor in two_hop_neighbors[node] if neighbor in coloring}
            
            min_color = 0
            while min_color in used_colors:
                min_color += 1
            
            coloring[node] = min_color
            available_colors[node] = min_color
    return coloring

def heuristic_function(graph, coloring, two_hop_neighbors, heuristics):
    conflicts = 0
    color_count = defaultdict(int)
    for node, color in coloring.items():
        color_count[color] += 1
        for neighbor in graph[node]:
            if coloring[node] == coloring[neighbor]:
                conflicts += heuristics.get((node, neighbor), 1)
        
        for neighbor in two_hop_neighbors[node]:
            if coloring[node] == coloring.get(neighbor, -1):
                conflicts += 2  # Higher penalty for two-hop conflicts
    
    balance_score = max(color_count.values()) - min(color_count.values())
    return conflicts + balance_score + len(color_count)  # Lower is better

def get_successors(graph, coloring, two_hop_neighbors, preassigned_colors):
    successors = []
    most_conflicted = sorted(graph, key=lambda x: -sum(coloring[x] == coloring[n] for n in graph[x]))[:3]
    
    for node in most_conflicted:
        if node in preassigned_colors:
            continue
        original_color = coloring[node]
        used_colors = {coloring.get(neighbor) for neighbor in graph[node] if neighbor in coloring}
        used_colors |= {coloring.get(neighbor) for neighbor in two_hop_neighbors[node] if neighbor in coloring}
        
        min_color = 0
        while min_color in used_colors:
            min_color += 1
        
        if min_color != original_color:
            new_coloring = coloring.copy()
            new_coloring[node] = min_color
            successors.append(new_coloring)
    return successors

def local_beam_search(graph, heuristics, preassigned_colors, k=3, max_iterations=500):
    two_hop_neighbors = precompute_two_hop_neighbors(graph)
    states = [initial_coloring(graph, two_hop_neighbors, preassigned_colors) for _ in range(k)]
    best_state = min(states, key=lambda s: heuristic_function(graph, s, two_hop_neighbors, heuristics))
    best_score = heuristic_function(graph, best_state, two_hop_neighbors, heuristics)
    
    for _ in range(max_iterations):
        new_states = []
        for state in states:
            new_states.extend(get_successors(graph, state, two_hop_neighbors, preassigned_colors))
        
        if not new_states:
            break
        
        states = sorted(new_states, key=lambda s: heuristic_function(graph, s, two_hop_neighbors, heuristics))[:k]
        new_best = states[0]
        new_best_score = heuristic_function(graph, new_best, two_hop_neighbors, heuristics)
        
        if new_best_score >= best_score:
            break  # Early exit if no improvement
        best_state, best_score = new_best, new_best_score
    
    return best_state

# Load dataset
graph, heuristics = load_graph("hypercube_dataset.txt")
preassigned_colors = {0: 0, 1: 1}  # Example preassigned colors

# Run Local Beam Search
final_coloring = local_beam_search(graph, heuristics, preassigned_colors)
print("Final coloring:")
for node in sorted(final_coloring):
    print(f"Node {node} has color {final_coloring[node]}")