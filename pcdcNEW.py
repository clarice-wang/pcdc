import pandas as pd
from collections import defaultdict, deque
import networkx as nx

# File paths
DANCER_CSV = "./dancer_preferences.csv"
CHOREO_CSV = "./choreographer_preferences.csv"

def load_data():
    """Load and parse the CSV files"""
    dancers_df = pd.read_csv(DANCER_CSV)
    choreo_df = pd.read_csv(CHOREO_CSV)
    
    # Parse dancer information
    dancers = {}
    for _, row in dancers_df.iterrows():
        dancers[row['Name']] = {
            'experience': row['Experience'],
            'dances': parse_dance_range(row['Dances']),
            'most': str(row['Most']).split(','),
            'okay': str(row['Okay']).split(','),
            'no': str(row['No']).split(','),
            'current_dances': []
        }
    
    # Parse choreographer information
    dances = {}
    for _, row in choreo_df.iterrows():
        dances[row['Dance']] = {
            'max_dancers': int(row['NumDancers']),
            'ratings': {
                5: str(row['Rating_5']).split(','),
                4: str(row['Rating_4']).split(','),
                3: str(row['Rating_3']).split(','),
                2: str(row['Rating_2']).split(','),
                1: str(row['Rating_1']).split(',')
            },
            'current_dancers': []
        }
    
    return dancers, dances

def parse_dance_range(range_str):
    """Convert dance range string to min-max tuple"""
    ranges = {
        '1-2': (1, 2),
        '2-3': (2, 3),
        '3-4': (3, 4),
        '4-5': (4, 5),
        '5+': (5, 8)  # Setting arbitrary max of 8
    }
    return ranges.get(range_str, (1, 2))  # Default to 1-2 if invalid

def get_dancer_rating(dancer, dance, dances):
    """Get choreographer's rating for a dancer"""
    for rating in range(5, 0, -1):
        if dancer in dances[dance]['ratings'][rating]:
            return rating
    return 0  # Not rated

def can_add_dancer(dancer, dance, dancers, dances):
    """Check if a dancer can be added to a dance"""
    # Check if dance is in do-not-want list
    if dance in dancers[dancer]['no']:
        return False
        
    # Check if dance is full
    if len(dances[dance]['current_dancers']) >= dances[dance]['max_dancers']:
        return False
    
    # Check if dancer has reached their maximum
    current_count = len(dancers[dancer]['current_dances'])
    max_dances = dancers[dancer]['dances'][1]
    return current_count < max_dances

def assign_dancers(dancers, dances):
    """Main matching algorithm"""
    # First pass: Assign dancers to their most wanted dances
    for dancer in dancers:
        for dance in dancers[dancer]['most']:
            if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                if get_dancer_rating(dancer, dance, dances) > 0:  # Only assign if rated
                    dances[dance]['current_dancers'].append(dancer)
                    dancers[dancer]['current_dances'].append(dance)

    # Second pass: Fill remaining spots with "okay with" preferences
    for dancer in dancers:
        if len(dancers[dancer]['current_dances']) < dancers[dancer]['dances'][0]:
            for dance in dancers[dancer]['okay']:
                if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                    if get_dancer_rating(dancer, dance, dances) > 0:
                        dances[dance]['current_dancers'].append(dancer)
                        dancers[dancer]['current_dances'].append(dance)

    # Optional: Optimization pass to improve assignments
    optimize_assignments(dancers, dances)

def optimize_assignments(dancers, dances):
    """Attempt to improve assignments by swapping dancers"""
    improvements_made = True
    while improvements_made:
        improvements_made = False
        for dance in dances:
            if len(dances[dance]['current_dancers']) < dances[dance]['max_dancers']:
                # Look for highly rated dancers not in the dance
                for rating in range(5, 2, -1):  # Only consider ratings 5-3
                    for dancer in dances[dance]['ratings'][rating]:
                        if dancer not in dances[dance]['current_dancers']:
                            if can_add_dancer(dancer, dance, dancers, dances):
                                dances[dance]['current_dancers'].append(dancer)
                                dancers[dancer]['current_dances'].append(dance)
                                improvements_made = True

def create_show_order(dances):
    """Create optimal show order to minimize quick changes"""
    graph = nx.Graph()
    graph.add_nodes_from(dances.keys())
    
    # Add edges weighted by shared dancers
    for dance1 in dances:
        for dance2 in dances:
            if dance1 < dance2:
                shared = len(set(dances[dance1]['current_dancers']) & 
                           set(dances[dance2]['current_dancers']))
                if shared > 0:
                    graph.add_edge(dance1, dance2, weight=shared)
    
    # Create show order using minimum spanning tree
    mst = nx.minimum_spanning_tree(graph)
    return list(nx.dfs_preorder_nodes(mst))

def save_results(dancers, dances, show_order):
    """Save results to CSV files"""
    # Save assignments
    assignments = []
    for dance in dances:
        for dancer in dances[dance]['current_dancers']:
            assignments.append({
                'Dance': dance,
                'Dancer': dancer,
                'Rating': get_dancer_rating(dancer, dance, dances)
            })
    
    assignments_df = pd.DataFrame(assignments)
    assignments_df.to_csv('dance_assignments.csv', index=False)
    
    # Save show order
    show_order_df = pd.DataFrame({'Order': range(1, len(show_order) + 1),
                                 'Dance': show_order})
    show_order_df.to_csv('show_order.csv', index=False)

def main():
    # Load data
    dancers, dances = load_data()
    
    # Make assignments
    assign_dancers(dancers, dances)
    
    # Generate show order
    show_order = create_show_order(dances)
    
    # Save results
    save_results(dancers, dances, show_order)
    
    # Print summary
    print("\nAssignments Summary:")
    for dance in dances:
        print(f"\n{dance}:")
        print(f"Dancers: {', '.join(dances[dance]['current_dancers'])}")
        print(f"Total: {len(dances[dance]['current_dancers'])}/{dances[dance]['max_dancers']}")
    
    print("\nShow Order:")
    print(" -> ".join(show_order))
    
    print("\nResults saved to 'dance_assignments.csv' and 'show_order.csv'")

if __name__ == "__main__":
    main()