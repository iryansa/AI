# Graph Coloring and Grocery Store Shelf Optimization

## Overview

This repository contains solutions for two optimization problems:

1. **Graph Coloring using Local Beam Search**
2. **Grocery Store Shelf Optimization using Genetic Algorithm (GA)**

## Problem 1: Graph Coloring using Local Beam Search

### Problem Statement

Given an undirected graph **G(V, E)**, assign colors to each vertex while satisfying:

1. No two adjacent vertices share the same color.
2. Minimize the number of colors used (Chromatic Number Constraint).

### Additional Constraints

- **Degree-Based Coloring:** Higher-degree vertices are assigned colors first.
- **Pre-Assigned Colors:** Some vertices have predefined colors that must remain unchanged.
- **Balanced Color Usage:** The number of vertices per color should be approximately equal.
- **Distance Constraint:** Certain vertices must have different colors even if they are two hops apart.

### Approach

The **Local Beam Search** algorithm is used for solving this problem:

1. **State Representation:** Each state represents a color assignment for all vertices.
2. **Initial State:** A random valid coloring satisfying pre-assigned colors.
3. **Successor Generation:**
   - Recolor vertices while maintaining constraints.
   - Prioritize high-degree vertices to reduce conflicts.
4. **Heuristic Function:** Evaluates the best states based on constraints.

### Dataset

The solution is tested on the **hypercube\_dataset.txt**, which includes heuristics under additional constraints.

## Problem 2: Grocery Store Shelf Optimization using Genetic Algorithm

### Problem Statement

Optimize shelf space allocation in a grocery store to:

- Maximize space utilization.
- Ensure quick access to high-demand products.
- Enhance customer shopping experience.

### Constraints Considered

1. **Shelf Capacity & Weight Limit** – Each shelf has a maximum weight limit.
2. **High-Demand Product Accessibility** – Frequently bought items should be at eye level.
3. **Product Category Segmentation** – Similar products should be placed together.
4. **Perishable vs. Non-Perishable Separation** – Perishables require refrigeration.
5. **Hazardous and Allergen-Free Zones** – Dangerous items must be stored separately.
6. **Product Compatibility and Cross-Selling** – Complementary products should be placed nearby.
7. **Restocking Efficiency** – Heavy items should be on lower shelves.
8. **Refrigeration Efficiency** – Maximize refrigerator usage before opening a new one.
9. **Promotional and Discounted Items Visibility** – Place offers in highly visible areas.
10. **Theft Prevention** – Secure high-value items in visible or locked sections.

### Approach

The **Genetic Algorithm (GA)** is used to generate an optimal shelving plan:

1. **Population Initialization:** Random valid shelving arrangements.
2. **Fitness Function:** Evaluates solutions based on constraint satisfaction.
3. **Selection:** Top candidates are chosen for crossover.
4. **Crossover & Mutation:** Generates new solutions by combining existing ones.
5. **Termination Criteria:** Stops when an optimal/near-optimal shelving plan is achieved.

### Output

The optimized shelf allocation results are stored in an **Excel sheet** for better visualization.

## Repository Structure

```
📂 graph_color_grocery_shelf
├── 📂 Graph_Color
|   ├── hypercube_dataset.txt
│   ├── graph_color.py
│   ├── mini.txt
│
├── 📂 Grocey_shelf_optimization
│   ├── grocery_shelf.py
│   
├── optimized_shelvf_allocation.xlsx   
├── README.md
├── AI-ASSIGNMENT 2 (1).pdf
```

## How to Run

### Graph Coloring

1. Navigate to the `Graph_Color` folder.
2. Run:
   ```bash
   python graph_color.py
   ```

### Shelf Optimization

1. Navigate to the `Grocery_shelf_optimization` folder.
2. Run:
   ```bash
   python grocery_shelf.py
   ```
3. The optimized shelving plan will be saved in `optimized_shelf_allocation.xlsx`.

## Requirements

Install pandas using:

```bash
pip install pandas
```

## Author

Siddique Ahmad Ryan

## License

This project is licensed under the MIT License.

