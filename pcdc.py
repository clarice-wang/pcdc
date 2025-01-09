import pandas as pd
from collections import defaultdict, deque
import networkx as nx

# File Paths
csv_file = "./pcdc - data.csv"

# Step 1: Load CSV Data
data = pd.read_csv(csv_file)

# Parse Columns
dancers = data['Dancers'].dropna().unique().tolist()
max_dances_per_dancer = dict(zip(data['Dancers'].dropna(), data['Max Dances/Dancer'].dropna()))
dances = data['Dances'].dropna().unique().tolist()
max_dancers_per_dance = dict(zip(data['Dances'].dropna(), data['Max Dancers/Dance'].dropna()))

# Debug: Print column names and dance names
# print("Available columns:", data.columns.tolist())
# print("Dance names:", dances)
# print("Dancer names:", dancers)

# Parse Rankings (Choreographer and Dancer Rankings)
choreographer_rankings = {}
for dance in dances:
    column_name = f"CR - {dance}"
    if column_name in data.columns:
        choreographer_rankings[dance] = data[column_name].dropna().tolist()
    else:
        print(f"Warning: Column '{column_name}' not found in data")

dancer_rankings = {}
for dancer in dancers:
    column_name = f"DR - {dancer}"
    if column_name in data.columns:
        dancer_rankings[dancer] = data[column_name].dropna().tolist()
    else:
        print(f"Warning: Column '{column_name}' not found in data")

# Step 2: Matching Algorithm
# Helper function to initialize preferences
def create_preference_queue(rankings):
    return {key: deque(rankings[key]) for key in rankings}

# Initialize preferences and assignments
available_dancers = set(dancers)
dancer_preferences = create_preference_queue(dancer_rankings)
dance_preferences = create_preference_queue(choreographer_rankings)

# Assignments
dance_assignments = {dance: [] for dance in dances}
dancer_assignments = {dancer: [] for dancer in dancers}

# Matching
while available_dancers:
    dancer = available_dancers.pop()
    while len(dancer_assignments[dancer]) < max_dances_per_dancer[dancer] and dancer_preferences[dancer]:
        preferred_dance = dancer_preferences[dancer].popleft()
        if len(dance_assignments[preferred_dance]) < max_dancers_per_dance[preferred_dance]:
            # Assign dancer to the dance
            dance_assignments[preferred_dance].append(dancer)
            dancer_assignments[dancer].append(preferred_dance)
        else:
            # Check if current assignments can be improved
            least_preferred_dancer = min(
                dance_assignments[preferred_dance],
                key=lambda x: choreographer_rankings[preferred_dance].index(x)
            )
            if choreographer_rankings[preferred_dance].index(dancer) < choreographer_rankings[preferred_dance].index(least_preferred_dancer):
                # Replace the least preferred dancer
                dance_assignments[preferred_dance].remove(least_preferred_dancer)
                dancer_assignments[least_preferred_dancer].remove(preferred_dance)
                available_dancers.add(least_preferred_dancer)

                # Add the new dancer
                dance_assignments[preferred_dance].append(dancer)
                dancer_assignments[dancer].append(preferred_dance)

# Step 3: Show Order Optimization
# Create a graph with dances as nodes and edges weighted by shared dancers
graph = nx.Graph()
graph.add_nodes_from(dances)

for i, dance_a in enumerate(dances):
    for j, dance_b in enumerate(dances):
        if i != j:
            shared_dancers = set(dance_assignments[dance_a]) & set(dance_assignments[dance_b])
            if shared_dancers:
                graph.add_edge(dance_a, dance_b, weight=len(shared_dancers))

# Optimize order using minimum spanning tree and traversal
mst = nx.minimum_spanning_tree(graph)
show_order = list(nx.dfs_preorder_nodes(mst))

# Step 4: Output Results
# Final Assignments
print("Dance Assignments:")
for dance, assigned_dancers in dance_assignments.items():
    print(f"{dance}: {', '.join(assigned_dancers)}")

# Show Order
print("\nShow Order:")
print(" -> ".join(show_order))

# Save results to CSV
assignments_output = []
for dance, assigned_dancers in dance_assignments.items():
    for dancer in assigned_dancers:
        assignments_output.append({"Dance": dance, "Dancer": dancer})

assignments_df = pd.DataFrame(assignments_output)
assignments_df.to_csv("pcdc_assignments.csv", index=False)

print("\nResults saved to 'pcdc_assignments.csv'")
