import random
import heapq
from collections import defaultdict

def load_graph(filename):
    graph = defaultdict(list)
    heuristics = {}
    max_node = 0

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
                max_node = max(max_node, src, dest)
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")
    
    return graph, heuristics, max_node

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
    available_colors = defaultdict(set)
    
    for node in sorted(graph, key=lambda x: -len(graph[x])):
        if node in preassigned_colors:
            coloring[node] = preassigned_colors[node]
        else:
            used_colors = {coloring.get(neighbor) for neighbor in graph[node] if neighbor in coloring}
            used_colors |= {coloring.get(neighbor) for neighbor in two_hop_neighbors[node] if neighbor in coloring}
            
            for color in range(len(graph)):
                if color not in used_colors:
                    coloring[node] = color
                    break
    
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

def get_successors(graph, coloring, two_hop_neighbors, preassigned_colors, max_colors):
    successors = []
    most_conflicted = sorted(graph, key=lambda x: -sum(coloring[x] == coloring[n] for n in graph[x]))[:5]
    
    for node in most_conflicted:
        if node in preassigned_colors:
            continue
        original_color = coloring[node]
        used_colors = {coloring.get(neighbor) for neighbor in graph[node] if neighbor in coloring}
        used_colors |= {coloring.get(neighbor) for neighbor in two_hop_neighbors[node] if neighbor in coloring}
        
        for color in range(max_colors):
            if color not in used_colors and color < original_color:
                new_coloring = coloring.copy()
                new_coloring[node] = color
                successors.append(new_coloring)
                break
    return successors

def local_beam_search(graph, heuristics, preassigned_colors, max_node, k=3, max_iterations=500):
    two_hop_neighbors = precompute_two_hop_neighbors(graph)
    max_colors = 15  # Force a tighter color limit
    states = [initial_coloring(graph, two_hop_neighbors, preassigned_colors) for _ in range(k)]
    best_state = min(states, key=lambda s: heuristic_function(graph, s, two_hop_neighbors, heuristics))
    best_score = heuristic_function(graph, best_state, two_hop_neighbors, heuristics)
    
    for _ in range(max_iterations):
        new_states = []
        for state in states:
            new_states.extend(get_successors(graph, state, two_hop_neighbors, preassigned_colors, max_colors))
        
        if not new_states:
            break
        
        states = sorted(new_states, key=lambda s: heuristic_function(graph, s, two_hop_neighbors, heuristics))[:k]
        new_best = states[0]
        new_best_score = heuristic_function(graph, new_best, two_hop_neighbors, heuristics)
        
        if new_best_score >= best_score:
            break  # Early exit if no improvement
        best_state, best_score = new_best, new_best_score
    
    return best_state, max_colors

# Load dataset
graph, heuristics, max_node = load_graph("hypercube_dataset.txt")
preassigned_colors = {0: 0, 1: 7, 3: 11, 50: 4, 308: 5, 576: 6}  # Example preassigned colors

# Run Local Beam Search
final_coloring, max_colors = local_beam_search(graph, heuristics, preassigned_colors, max_node)
print(f"Solution found with {max_colors} colors")
print("Final coloring:")
for node in sorted(final_coloring):
    print(f"Node {node} has color {final_coloring[node]}")
