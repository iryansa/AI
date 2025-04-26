import networkx as nx

def read_graph(filepath):
    """
    Construct an undirected graph from the provided file.
    Each line is assumed to define an edge using at least two elements:
      - The first node (source)
      - The second node (destination)
    Any additional elements are ignored.
    """
    graph = nx.Graph()
    with open(filepath, 'r') as file:
        for line in file:
            tokens = line.strip().split()
            if len(tokens) < 2:
                continue
            source, destination = tokens[0], tokens[1]
            graph.add_edge(source, destination)
    return graph

def extract_cliques(graph):
    """
    Retrieve all maximal cliques in the graph.
    A maximal clique is a fully connected subset of nodes that cannot be extended.
    """
    return list(nx.find_cliques(graph))

def extract_cycles(graph):
    """
    Generate the cycle basis for the graph.
    A cycle basis is a minimal set of simple cycles from which other cycles can be formed.
    """
    return nx.cycle_basis(graph)

def detect_stars(graph):
    """
    Find star-like patterns in the graph.
    A node with two or more neighbors forms a star if its neighbors are not connected to each other.
    Each star is reported as a list: [center, leaf1, leaf2, ...].
    """
    star_patterns = []
    for node in graph.nodes():
        neighbors = list(graph.neighbors(node))
        if len(neighbors) < 2:
            continue
        if all(not graph.has_edge(neighbors[i], neighbors[j]) 
               for i in range(len(neighbors)) 
               for j in range(i + 1, len(neighbors))):
            star_patterns.append([node] + neighbors)
    return star_patterns

def detect_chains(graph):
    """
    Identify simple paths (chains) in the graph.
    A chain is defined as a linear subgraph with:
      - Exactly two nodes of degree 1 (endpoints),
      - All other nodes having degree 2.
    """
    chain_list = []
    for component in nx.connected_components(graph):
        subgraph = graph.subgraph(component)
        if len(subgraph.nodes) < 2:
            continue
        degree_counts = [subgraph.degree(node) for node in subgraph.nodes]
        if degree_counts.count(1) == 2 and degree_counts.count(2) == len(subgraph.nodes) - 2:
            endpoints = [node for node in subgraph.nodes if subgraph.degree(node) == 1]
            if len(endpoints) == 2:
                path = nx.shortest_path(subgraph, source=endpoints[0], target=endpoints[1])
                chain_list.append(path)
    return chain_list

def main():
    input_file = "Identification/Data2.txt"  
    graph = read_graph(input_file)

    cliques = extract_cliques(graph)
    cycles = extract_cycles(graph)
    stars = detect_stars(graph)
    chains = detect_chains(graph)

    with open("output.txt", "w") as output:
        output.write(f"Cliques (maximal): {len(cliques)}\n")
        output.write(f"\nCycles (basis): {len(cycles)}\n")
        output.write(f"\nStars (center + leaves): {len(stars)}\n")
        output.write(f"\nChains (simple paths): {len(chains)}\n")
        output.write("------------------------------------------------------------------------------\n")

        output.write("Cliques:\n")
        for group in cliques:
            output.write(f" - {group}\n")
        output.write("------------------------------------------------------------------------------\n")

        output.write("Cycles:\n")
        for cyc in cycles:
            output.write(f" - {cyc}\n")
        output.write("------------------------------------------------------------------------------\n")

        output.write("Stars:\n")
        for s in stars:
            output.write(f" - {s}\n")
        output.write("------------------------------------------------------------------------------\n")

        output.write("Chains:\n")
        for ch in chains:
            output.write(f" - {ch}\n")

if __name__ == "__main__":
    main()
