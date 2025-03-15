import random
import pandas as pd

# Define shelves and products
shelves = {
    "S1": {"type": "checkout", "capacity": 8, "position": "high"},
    "S2": {"type": "lower", "capacity": 25, "position": "low"},
    "S4": {"type": "eye-level", "capacity": 15, "position": "mid"},
    "S5": {"type": "general", "capacity": 20, "position": "mid"},
    "R1": {"type": "refrigerator", "capacity": 20},
    "H1": {"type": "hazardous", "capacity": 10}
}

products = {
    "P1": {"name": "Milk", "weight": 5, "category": "dairy", "demand": "high", "storage": "regular"},
    "P2": {"name": "Rice Bag", "weight": 10, "category": "grains", "demand": "medium", "storage": "regular"},
    "P3": {"name": "Frozen Nuggets", "weight": 5, "category": "frozen", "demand": "high", "storage": "refrigerated"},
    "P4": {"name": "Cereal", "weight": 3, "category": "breakfast", "demand": "high", "storage": "regular"},
    "P5": {"name": "Pasta", "weight": 2, "category": "grains", "demand": "medium", "storage": "regular"},
    "P6": {"name": "Pasta Sauce", "weight": 3, "category": "sauces", "demand": "medium", "storage": "regular"},
    "P7": {"name": "Detergent", "weight": 4, "category": "cleaning", "demand": "low", "storage": "hazardous"},
    "P8": {"name": "Glass Cleaner", "weight": 5, "category": "cleaning", "demand": "low", "storage": "hazardous"}
}

# Revised initialization: rule-based assignment based on product attributes
def initialize_population_rule_based(pop_size=50):
    population = []
    for _ in range(pop_size):
        # Start with empty assignments for each shelf
        chromosome = {s: [] for s in shelves.keys()}
        for p, attr in products.items():
            # Refrigerated items go to R1
            if attr["storage"] == "refrigerated":
                chromosome["R1"].append(p)
            # Hazardous items go to H1
            elif attr["storage"] == "hazardous":
                chromosome["H1"].append(p)
            # High-demand products: Prefer eye-level (S4); if S4 is full, they can go elsewhere
            elif attr["demand"] == "high":
                total_weight_S4 = sum(products[prod]["weight"] for prod in chromosome["S4"])
                if total_weight_S4 + attr["weight"] <= shelves["S4"]["capacity"]:
                    chromosome["S4"].append(p)
                else:
                    chromosome["S1"].append(p)
            # Heavy items (weight > 5) prefer S2
            elif attr["weight"] > 5:
                chromosome["S2"].append(p)
            # Otherwise, assign to a general shelf (S5)
            else:
                chromosome["S5"].append(p)
        chromosome = repair(chromosome)
        population.append(chromosome)
    return population

# Fitness function: lower score means better fitness (0 is ideal)
def fitness(chromosome):
    penalty = 0
    for shelf, prod_ids in chromosome.items():
        shelf_capacity = shelves[shelf]["capacity"]
        total_weight = sum(products[p]["weight"] for p in prod_ids)
        if total_weight > shelf_capacity:
            penalty += (total_weight - shelf_capacity) * 10
        for p in prod_ids:
            prod = products[p]
            if prod["storage"] == "refrigerated" and shelf != "R1":
                penalty += 50
            if prod["storage"] == "hazardous" and shelf != "H1":
                penalty += 50
            if prod["demand"] == "high":
                if shelves[shelf].get("position") not in ["high", "mid"]:
                    penalty += 20
            if prod["weight"] > 5 and shelves[shelf].get("position") == "high":
                penalty += 10
        # Example: Ensure complementary items (P5 and P6) are grouped together
        if "P5" in prod_ids and "P6" not in prod_ids:
            penalty += 15
        if "P6" in prod_ids and "P5" not in prod_ids:
            penalty += 15
    return penalty

# Repair function: ensure each product appears exactly once
def repair(chromosome):
    all_products = set(products.keys())
    assigned = []
    for shelf in chromosome:
        unique = []
        for p in chromosome[shelf]:
            if p not in assigned:
                unique.append(p)
                assigned.append(p)
        chromosome[shelf] = unique
    missing = list(all_products - set(assigned))
    # Assign missing products to the shelf with the most available capacity (by weight)
    for p in missing:
        best_shelf = None
        best_remaining = -1
        for shelf in shelves:
            current_weight = sum(products[prod]["weight"] for prod in chromosome[shelf])
            remaining = shelves[shelf]["capacity"] - current_weight
            if remaining >= products[p]["weight"] and remaining > best_remaining:
                best_remaining = remaining
                best_shelf = shelf
        if best_shelf is None:
            best_shelf = random.choice(list(chromosome.keys()))
        chromosome[best_shelf].append(p)
    return chromosome

# Tournament selection
def selection(population, fitnesses, tournament_size=3):
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(list(zip(population, fitnesses)), tournament_size)
        tournament.sort(key=lambda x: x[1])
        selected.append(tournament[0][0])
    return selected

# Crossover: swap shelf assignments between two parents and repair duplicates/omissions
def crossover(parent1, parent2):
    child1, child2 = {}, {}
    for shelf in shelves.keys():
        if random.random() < 0.5:
            child1[shelf] = parent1[shelf][:]
            child2[shelf] = parent2[shelf][:]
        else:
            child1[shelf] = parent2[shelf][:]
            child2[shelf] = parent1[shelf][:]
    child1 = repair(child1)
    child2 = repair(child2)
    return child1, child2

# Mutation: randomly move a product from one shelf to another
def mutation(chromosome, mutation_rate=0.1):
    if random.random() < mutation_rate:
        shelf = random.choice(list(chromosome.keys()))
        if chromosome[shelf]:
            product = random.choice(chromosome[shelf])
            chromosome[shelf].remove(product)
            new_shelf = random.choice(list(chromosome.keys()))
            chromosome[new_shelf].append(product)
            chromosome = repair(chromosome)
    return chromosome

# GA main loop using the rule-based initialization; tracks and returns the generation number
def genetic_algorithm(max_generations=100):
    population = initialize_population_rule_based()
    best_solution = None
    best_fitness = float('inf')
    best_generation = 0
    for generation in range(max_generations):
        fitnesses = [fitness(chromo) for chromo in population]
        for chromo, fit in zip(population, fitnesses):
            if fit < best_fitness:
                best_fitness = fit
                best_solution = chromo
                best_generation = generation  # store generation at which best was found
        if best_fitness == 0:
            break
        selected = selection(population, fitnesses)
        next_generation = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[(i+1) % len(selected)]
            child1, child2 = crossover(parent1, parent2)
            child1 = mutation(child1)
            child2 = mutation(child2)
            next_generation.extend([child1, child2])
        population = next_generation
    return best_solution, best_fitness, best_generation

# Export the best solution to Excel
def export_to_excel(chromosome, filename="optimized_shelf_allocation.xlsx"):
    data = []
    for shelf, prods in chromosome.items():
        shelf_info = shelves[shelf]
        product_details = "; ".join([f"{p} ({products[p]['name']})" for p in prods])
        total_weight = sum(products[p]["weight"] for p in prods)
        data.append({
            "Shelf": shelf,
            "Type": shelf_info["type"],
            "Capacity": shelf_info["capacity"],
            "Assigned Products": product_details,
            "Total Weight": total_weight
        })
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# Run the GA and output results
best_chromosome, best_fit, best_gen = genetic_algorithm()
export_to_excel(best_chromosome)
print("Best Fitness:", best_fit)
print("Optimized Shelf Allocation:", best_chromosome)
print("Best found in Generation:", best_gen)
