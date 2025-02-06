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
    
    # Parse dancer information first
    dancers = {}
    for _, row in dancers_df.iterrows():
        dancers[str(row['Name'])] = {
            'experience': row['Experience'],
            'dances': parse_dance_range(row['Dances']),
            'most': parse_preference_list(row['Most']),
            'okay': parse_preference_list(row['Okay']),
            'no': parse_preference_list(row['No']),
            'current_dances': []
        }
    
    # Get valid dancer set
    valid_dancers = set(dancers.keys())
    
    # Parse choreographer information, filtering out invalid dancers
    dances = {}
    for _, row in choreo_df.iterrows():
        ratings_dict = {}
        for rating in range(1, 6):
            # Filter out any dancers that aren't in our dancer list
            rated_dancers = parse_preference_list(row[f'Rating_{rating}'])
            ratings_dict[rating] = [d for d in rated_dancers if d in valid_dancers]
            
            # Print warning about invalid dancers
            invalid_dancers = [d for d in rated_dancers if d not in valid_dancers]
            if invalid_dancers:
                print(f"Warning: Dance '{row['Dance']}' rated unknown dancer(s) {invalid_dancers} as {rating}")
        
        dances[str(row['Dance'])] = {
            'max_dancers': parse_num_dancers(str(row['NumDancers'])),
            'ratings': ratings_dict,
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

def parse_num_dancers(num_str):
    """Convert number of dancers string to min-max tuple"""
    try:
        if '-' in num_str:
            # Handle range format (e.g., "10-14")
            min_val, max_val = map(int, num_str.split('-'))
            return (min_val, max_val)
        elif ',' in num_str:
            # Handle options format (e.g., "3,5")
            options = [int(x.strip()) for x in num_str.split(',')]
            return (min(options), max(options))
        else:
            # Handle single number
            val = int(num_str)
            return (val, val)
    except (ValueError, TypeError):
        return (1, 1)  # Default fallback

def parse_preference_list(value):
    """Parse a preference list, handling empty/NaN values"""
    if pd.isna(value) or value == '':
        return []
    return [str(x.strip()) for x in str(value).split(',') if x.strip()]

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
    current_dancers = len(dances[dance]['current_dancers'])
    max_dancers_range = dances[dance]['max_dancers']
    if current_dancers >= max_dancers_range[1]:  # Use upper bound of range
        return False
    
    # Check if dancer has reached their maximum
    current_count = len(dancers[dancer]['current_dances'])
    max_dances = dancers[dancer]['dances'][1]
    if current_count >= max_dances:
        return False

    # Prevent dancers from being in both '只此青绿' and '玉鸟'
    if dance in ['只此青绿', '玉鸟']:
        other_dance = '玉鸟' if dance == '只此青绿' else '只此青绿'
        if other_dance in dancers[dancer]['current_dances']:
            return False

    return True

def identify_excluded_dancers(dances):
    """Identify dancers that are rated 1 by more than 60% of choreographers"""
    total_dances = len(dances)
    threshold = 0.6 * total_dances
    
    # Count how many dances gave each dancer a rating of 1
    rating_1_counts = defaultdict(int)
    for dance in dances:
        for dancer in dances[dance]['ratings'][1]:
            rating_1_counts[dancer] += 1
    
    # Find dancers above threshold
    excluded_dancers = [
        dancer for dancer, count in rating_1_counts.items() 
        if count >= threshold
    ]
    
    if excluded_dancers:
        print("\nWARNING: The following dancers were rated poorly by >60% of choreographers")
        print("and will be excluded from assignments:")
        for dancer in excluded_dancers:
            print(f"- {dancer} (rated 1 by {rating_1_counts[dancer]} choreographers)")
        print()
    
    return set(excluded_dancers)

def assign_dancers(dancers, dances):
    """Main matching algorithm"""
    # First identify dancers to exclude
    excluded_dancers = identify_excluded_dancers(dances)
    
    # First pass: Assign dancers to ONE of their most wanted dances
    for dancer in dancers:
        if dancer in excluded_dancers:
            continue
        for dance in dancers[dancer]['most']:
            if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                if get_dancer_rating(dancer, dance, dances) > 0:  # Only assign if rated
                    dances[dance]['current_dancers'].append(dancer)
                    dancers[dancer]['current_dances'].append(dance)
                    break  # Only assign ONE dance initially
    
    # Second pass: Ensure everyone has at least one dance (using "okay" preferences)
    for dancer in dancers:
        if dancer in excluded_dancers:
            continue
        if len(dancers[dancer]['current_dances']) == 0:
            # Try their "okay" dances first
            for dance in dancers[dancer]['okay']:
                if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                    if get_dancer_rating(dancer, dance, dances) > 0:
                        dances[dance]['current_dancers'].append(dancer)
                        dancers[dancer]['current_dances'].append(dance)
                        break
            
            # If still not assigned, try any available dance
            if len(dancers[dancer]['current_dances']) == 0:
                for dance in dances:
                    if (dance not in dancers[dancer]['no'] and 
                        can_add_dancer(dancer, dance, dancers, dances) and 
                        get_dancer_rating(dancer, dance, dances) > 0):
                        dances[dance]['current_dancers'].append(dancer)
                        dancers[dancer]['current_dances'].append(dance)
                        break

    # Third pass: Now assign additional dances up to limits
    for dancer in dancers:
        if dancer in excluded_dancers:
            continue
        # First try their "most" preferences
        for dance in dancers[dancer]['most']:
            if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                if get_dancer_rating(dancer, dance, dances) > 0:
                    dances[dance]['current_dancers'].append(dancer)
                    dancers[dancer]['current_dances'].append(dance)

        # Then try their "okay" preferences
        for dance in dancers[dancer]['okay']:
            if dance in dances and can_add_dancer(dancer, dance, dancers, dances):
                if get_dancer_rating(dancer, dance, dances) > 0:
                    dances[dance]['current_dancers'].append(dancer)
                    dancers[dancer]['current_dances'].append(dance)

    # Print warning for any still-unassigned dancers
    unassigned = [d for d in dancers if d not in excluded_dancers and len(dancers[d]['current_dances']) == 0]
    if unassigned:
        print("\nWARNING: Could not assign the following dancers to any dances:")
        for dancer in unassigned:
            print(f"- {dancer}")
        print()

    # Optional: Optimization pass to improve assignments
    optimize_assignments(dancers, dances, excluded_dancers)

def optimize_assignments(dancers, dances, excluded_dancers):
    """Attempt to improve assignments by swapping dancers"""
    improvements_made = True
    while improvements_made:
        improvements_made = False
        for dance in dances:
            if len(dances[dance]['current_dancers']) < dances[dance]['max_dancers'][1]:
                # Look for highly rated dancers not in the dance
                for rating in range(5, 2, -1):  # Only consider ratings 5-3
                    for dancer in dances[dance]['ratings'][rating]:
                        if dancer not in excluded_dancers and dancer not in dances[dance]['current_dancers']:
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
    # Save dance assignments
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
    
    # Save dancer assignments
    dancer_assignments = []
    for dancer in dancers:
        dancer_assignments.append({
            'Dancer': dancer,
            'Assigned_Dances': ','.join(dancers[dancer]['current_dances']),
            'Number_of_Dances': len(dancers[dancer]['current_dances'])
        })
    
    dancer_df = pd.DataFrame(dancer_assignments)
    dancer_df.to_csv('dancer_assignments.csv', index=False)
    
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
        print(f"Total: {len(dances[dance]['current_dancers'])}/{dances[dance]['max_dancers'][1]}")
    
    print("\nDancer Assignments:")
    for dancer in sorted(dancers.keys()):
        if dancers[dancer]['current_dances']:
            print(f"{dancer}: {', '.join(dancers[dancer]['current_dances'])} ({len(dancers[dancer]['current_dances'])} dances)")
    
    print("\nShow Order:")
    print(" -> ".join(show_order))
    
    print("\nResults saved to:")
    print("- 'dance_assignments.csv' (dance-centric view)")
    print("- 'dancer_assignments.csv' (dancer-centric view)")
    print("- 'show_order.csv'")

if __name__ == "__main__":
    main()