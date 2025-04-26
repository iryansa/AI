import sys
from collections import deque, defaultdict


def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("Error reading file:", e)
        sys.exit(1)


def parse_requests(lines):
    requests = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 4:
            continue

        roll = parts[0]
        curr_full = " ".join(parts[1:-2])
        curr_section_dup = parts[-2]
        desired_raw = parts[-1]

        curr_course, curr_section = (curr_full.split('-', 1)
                                     if '-' in curr_full else (curr_full, curr_section_dup))

        desired_course, desired_section = (desired_raw.split('-', 1)
                                           if '-' in desired_raw else (curr_course, desired_raw))

        satisfied = (curr_section == desired_section and curr_course == desired_course)

        try:
            year = int(roll[:2])
        except ValueError:
            year = 99

        requests.append({
            'roll': roll,
            'year': year,
            'current_course': curr_course,
            'current_section': curr_section,
            'desired_course': desired_course,
            'desired_section': desired_section,
            'satisfied': satisfied
        })
    return requests


def prioritize_requests(requests):
    return sorted(requests, key=lambda r: r['year'])


def build_current_mapping(requests, used):
    mapping = defaultdict(list)
    for idx, req in enumerate(requests):
        if idx not in used:
            mapping[(req['current_course'], req['current_section'])].append(idx)
    return mapping


def build_graph(requests, used, curr_map=None):
    graph = defaultdict(list)
    if curr_map is None:
        curr_map = build_current_mapping(requests, used)
    for idx, req in enumerate(requests):
        if idx in used or req['satisfied']:
            continue
        desired_key = (req['desired_course'], req['desired_section'])
        graph[idx] = [j for j in curr_map.get(desired_key, []) if j != idx]
    return graph


def find_direct_swaps(graph, requests, used):
    direct_swaps = []
    visited = set()
    for i in graph:
        if i in used or i in visited:
            continue
        for j in graph[i]:
            if j not in used and j not in visited and i in graph.get(j, []):
                direct_swaps.append([i, j])
                used.update([i, j])
                visited.update([i, j])
                break
    return direct_swaps


def bfs_find_cycle(graph, start, used):
    queue = deque([([start], start)])
    seen = set([start])
    while queue:
        path, current = queue.popleft()
        for neighbor in graph.get(current, []):
            if neighbor == start and len(path) >= 2:
                return path
            if neighbor not in path and neighbor not in used and neighbor not in seen:
                seen.add(neighbor)
                queue.append((path + [neighbor], neighbor))
    return None


def find_cycle_swaps(graph, requests, used):
    cycles = []
    for node in sorted(graph, key=lambda i: requests[i]['year']):
        if node not in used:
            cycle = bfs_find_cycle(graph, node, used)
            if cycle:
                used.update(cycle)
                cycles.append(cycle)
    return cycles


def generate_swap_instructions(direct_swaps, cycle_swaps, requests):
    instructions = []
    for i, j in direct_swaps:
        instructions.append(
            f"Direct Swap: Student {requests[i]['roll']} (currently in {requests[i]['current_course']}-{requests[i]['current_section']}) "
            f"swaps with Student {requests[j]['roll']} (currently in {requests[j]['current_course']}-{requests[j]['current_section']})."
        )
    for cycle in cycle_swaps:
        details = [
            f"Student {requests[cycle[k]]['roll']} gets {requests[cycle[k-1]]['current_course']}-{requests[cycle[k-1]]['current_section']}"
            for k in range(len(cycle))
        ]
        instructions.append("Cycle Swap: " + "; then ".join(details) + ".")
    return instructions


def print_summary(requests, direct_swaps, cycle_swaps):
    total = len(requests)
    satisfied_already = sum(r['satisfied'] for r in requests)
    satisfied_by_direct = len(direct_swaps) * 2
    satisfied_by_cycle = sum(map(len, cycle_swaps))
    total_satisfied = satisfied_already + satisfied_by_direct + satisfied_by_cycle

    print("\nSummary")
    print("-" * 40)
    print(f"Total requests:                 {total}")
    print(f"Satisfied (no swap needed):     {satisfied_already}")
    print(f"Satisfied via direct swaps:     {satisfied_by_direct}")
    print(f"Satisfied via cycle swaps:      {satisfied_by_cycle}")
    print(f"Total satisfied:                {total_satisfied}")
    print(f"Unresolved requests:            {total - total_satisfied}")


def main():
    filename = "Swapping/data3_2.txt"
    lines = load_file(filename)
    if not lines:
        print("No data found in the file!")
        sys.exit(1)

    requests = prioritize_requests(parse_requests(lines))
    used_indices = set()

    curr_map = build_current_mapping(requests, used_indices)
    graph = build_graph(requests, used_indices, curr_map)
    direct_swaps = find_direct_swaps(graph, requests, used_indices)

    graph = build_graph(requests, used_indices, curr_map)
    cycle_swaps = find_cycle_swaps(graph, requests, used_indices)

    for inst in generate_swap_instructions(direct_swaps, cycle_swaps, requests):
        print(inst)

    print_summary(requests, direct_swaps, cycle_swaps)


if __name__ == "__main__":
    main()
