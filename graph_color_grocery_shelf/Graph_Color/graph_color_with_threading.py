import random
from collections import defaultdict
import heapq
import time
import threading

# Load graph function remains unchanged
def load_graph(filename):
    graph = defaultdict(list)
    heuristics = {}
    max_node = 0
    
    with open(filename, 'r') as file:
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
    two_hop_neighbors = {}
    
    def process_node(node):
        neighbors = set(graph[node])
        two_hop = set()
        for neighbor in neighbors:
            two_hop.update(graph[neighbor])
        two_hop -= neighbors
        two_hop.discard(node)
        two_hop_neighbors[node] = two_hop
    
    if len(graph) > 100:
        threads = []
        for node in graph:
            t = threading.Thread(target=process_node, args=(node,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    else:
        for node in graph:
            process_node(node)
    
    return two_hop_neighbors

def heuristic_function(graph, coloring, two_hop_neighbors, heuristics):
    conflicts = 0
    color_count = defaultdict(int)
    
    for node in graph:
        color = coloring[node]
        color_count[color] += 1
        
        for neighbor in graph[node]:
            if coloring[node] == coloring[neighbor]:
                conflicts += heuristics.get((node, neighbor), 1)
        
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring and coloring[node] == coloring[neighbor]:
                conflicts += 2  
    
    if color_count:
        max_color = max(color_count.values())
        min_color = min(color_count.values())
        balance_score = max_color - min_color
    else:
        balance_score = 0
    
    return conflicts + balance_score + len(color_count)

def initial_coloring(graph, two_hop_neighbors, preassigned_colors):
    coloring = preassigned_colors.copy()
    nodes = sorted(graph.keys(), key=lambda x: (-len(graph[x]), x))
    lock = threading.Lock()
    
    def color_node(node):
        if node in preassigned_colors:
            return
        used_colors = set()
        for neighbor in graph[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        color = 0
        while color in used_colors:
            color += 1
        with lock:
            coloring[node] = color
    
    if len(graph) > 100:
        threads = []
        for node in nodes:
            t = threading.Thread(target=color_node, args=(node,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    else:
        for node in nodes:
            color_node(node)
    
    return coloring

def get_successors(graph, coloring, two_hop_neighbors, preassigned_colors):
    successors = []
    high_degree_nodes = sorted(graph.keys(), key=lambda x: (-len(graph[x]), x))[:5]
    lock = threading.Lock()
    
    def process_node(node):
        if node in preassigned_colors:
            return
        original_color = coloring[node]
        used_colors = set()
        for neighbor in graph[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        for neighbor in two_hop_neighbors[node]:
            if neighbor in coloring:
                used_colors.add(coloring[neighbor])
        possible_colors = [c for c in range(max(coloring.values()) + 2) if c not in used_colors and c != original_color]
        for color in possible_colors:
            new_coloring = coloring.copy()
            new_coloring[node] = color
            with lock:
                successors.append(new_coloring)
    
    if len(graph) > 100:
        threads = []
        for node in high_degree_nodes:
            t = threading.Thread(target=process_node, args=(node,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    else:
        for node in high_degree_nodes:
            process_node(node)
    
    return successors

def local_beam_search(graph, heuristics, preassigned_colors, k=5, max_iterations=100):
    two_hop_neighbors = precompute_two_hop_neighbors(graph)
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
        
        new_states_with_scores = [(state, heuristic_function(graph, state, two_hop_neighbors, heuristics)) for state in new_states]
        new_states_with_scores.sort(key=lambda x: x[1])
        states = [state for state, score in new_states_with_scores[:k]]
        
        current_best_score = new_states_with_scores[0][1] if new_states_with_scores else best_score
        if current_best_score < best_score:
            best_state, best_score = new_states_with_scores[0]
    
    return best_state, len(set(best_state.values()))

# Load dataset
graph, heuristics, max_node = load_graph("hypercube_dataset.txt")
num_nodes = max_node + 1

# Set the maximum color based on the number of nodes
if num_nodes < 500:
    max_color = 5
elif num_nodes < 1500:
    max_color = 10
elif num_nodes < 3000:
    max_color = 20
else:
    max_color = 30  # Default max color for larger graphs
# preassigned_colors = {node: random.randint(0, 5) for node in random.sample(range(num_nodes), max(1, num_nodes // 10))}
# # Generate random preassigned colors
preassigned_colors = {node: random.randint(0, max_color - 1) for node in random.sample(range(num_nodes), min(5, num_nodes))}
print("Preassigned colors:", preassigned_colors)

print("Total Vertices:", num_nodes)
print("Total Edges:", sum(len(neighbors) for neighbors in graph.values()) // 2)

start_time = time.time()
final_coloring, num_colors = local_beam_search(graph, heuristics, preassigned_colors)

print(f"Solution found with {num_colors} colors")
print("Final coloring:")
print("Node\t:\tColor")
for node in sorted(final_coloring):
    print(node, "\t:\t", final_coloring[node])

end_time = time.time()
execution_time = end_time - start_time
print("Execution Time:", execution_time)
