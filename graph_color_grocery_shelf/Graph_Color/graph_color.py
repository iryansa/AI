import random
from collections import defaultdict
import heapq

def load_graph(filename):
    """Load graph from file."""
    graph = defaultdict(list)
    heuristics = {}
    max_node = 0

    with open(filename, 'r') as file:
        # Skip header line
        header = file.readline()
        
        for line in file:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            try:
                src = int(parts[0])
                dest = int(parts[1])
                heuristic = float(parts[2])
                graph[src].append(dest)
                graph[dest].append(src)
                heuristics[(src, dest)] = heuristic
                heuristics[(dest, src)] = heuristic
                max_node = max(max_node, src, dest)
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")
    
    return graph, heuristics, max_node

def precompute_two_hop_neighbors(graph):
    """Precompute two-hop neighbors for all nodes."""
    two_hop_neighbors = {}
    for node in graph:
        neighbors = set(graph[node])
        two_hop = set()
        for neighbor in neighbors:
            two_hop.update(graph[neighbor])
        two_hop -= neighbors  # Remove direct neighbors
        two_hop.discard(node)  # Remove self
        two_hop_neighbors[node] = two_hop
    return two_hop_neighbors

def initial_coloring(graph, two_hop_neighbors, preassigned_colors):
    """Generate initial valid coloring."""
    coloring = {}
    # Sort nodes by degree descending
    nodes = sorted(graph.keys(), key=lambda x: (-len(graph[x]), x))
    
    for node in nodes:
        if node in preassigned_colors:
            coloring[node] = preassigned_colors[node]
            continue
        
        # Collect used colors from neighbors and two-hop neighbors
        used_colors = set()
        for neighbor in graph[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        
        # Assign the smallest available color
        color = 0
        while color in used_colors:
            color += 1
        coloring[node] = color
    
    return coloring

def heuristic_function(graph, coloring, two_hop_neighbors, heuristics):
    """Evaluate the quality of a coloring."""
    conflicts = 0
    color_count = defaultdict(int)
    
    # Count conflicts and color usage
    for node in graph:
        color = coloring[node]
        color_count[color] += 1
        
        # Check adjacent nodes
        for neighbor in graph[node]:
            if coloring[node] == coloring[neighbor]:
                conflicts += heuristics.get((node, neighbor), 1)
        
        # Check two-hop nodes
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring and coloring[node] == coloring[neighbor]:
                conflicts += 2  # Higher penalty for two-hop conflicts
    
    # Calculate balance score
    if color_count:
        max_color = max(color_count.values())
        min_color = min(color_count.values())
        balance_score = max_color - min_color
    else:
        balance_score = 0
    
    # Total heuristic: conflicts + balance + number of colors
    return conflicts + balance_score + len(color_count)

def get_successors(graph, coloring, two_hop_neighbors, preassigned_colors):
    """Generate successor states by recoloring high-degree nodes."""
    successors = []
    # Identify high-degree nodes
    high_degree_nodes = sorted(graph.keys(), key=lambda x: (-len(graph[x]), x))[:5]
    
    for node in high_degree_nodes:
        if node in preassigned_colors:
            continue
        
        original_color = coloring[node]
        used_colors = set()
        
        # Collect used colors from neighbors and two-hop neighbors
        for neighbor in graph[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        
        # Generate possible new colors
        possible_colors = []
        for color in range(max(coloring.values()) + 2):
            if color not in used_colors and color != original_color:
                possible_colors.append(color)
        
        # Create new colorings
        for color in possible_colors:
            new_coloring = coloring.copy()
            new_coloring[node] = color
            successors.append(new_coloring)
    
    return successors

def local_beam_search(graph, heuristics, preassigned_colors, k=5, max_iterations=100):
    """Perform local beam search for graph coloring."""
    two_hop_neighbors = precompute_two_hop_neighbors(graph)
    
    # Generate initial states
    initial_state = initial_coloring(graph, two_hop_neighbors, preassigned_colors)
    states = [initial_state] * k
    
    best_state = min(states, key=lambda s: heuristic_function(graph, s, two_hop_neighbors, heuristics))
    best_score = heuristic_function(graph, best_state, two_hop_neighbors, heuristics)
    
    for _ in range(max_iterations):
        new_states = []
        for state in states:
            new_states.extend(get_successors(graph, state, two_hop_neighbors, preassigned_colors))
        
        if not new_states:
            break
        
        # Evaluate new states
        new_states_with_scores = []
        for new_state in new_states:
            score = heuristic_function(graph, new_state, two_hop_neighbors, heuristics)
            new_states_with_scores.append((new_state, score))
        
        # Select top k states
        new_states_with_scores.sort(key=lambda x: x[1])
        states = [state for state, score in new_states_with_scores[:k]]
        
        # Update best state
        current_best_score = new_states_with_scores[0][1] if new_states_with_scores else best_score
        if current_best_score < best_score:
            best_state, best_score = new_states_with_scores[0]
    
    return best_state, len(set(best_state.values()))

# Load dataset
graph, heuristics, max_node = load_graph("hypercube_dataset.txt")
preassigned_colors = {0: 0, 1: 1}  # Example preassigned colors

# Run Local Beam Search
final_coloring, num_colors = local_beam_search(graph, heuristics, preassigned_colors)

# Print results
print(f"Solution found with {num_colors} colors")
print("Final coloring:")
for node in sorted(final_coloring):
    print(f"Node {node} has color {final_coloring[node]}")