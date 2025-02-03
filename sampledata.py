import random
import pandas as pd

def generate_random_preferences(dance_list, min_most=1, max_most=4, min_okay=2, max_okay=6, min_no=0, max_no=3):
    """
    Generate random preferences from a list of dances.
    
    Parameters:
    - dance_list: List of all possible dances
    - min_most/max_most: Range for number of "most wanted" dances
    - min_okay/max_okay: Range for number of "okay with" dances
    - min_no/max_no: Range for number of "do not want" dances
    
    Returns:
    - Dictionary with most, okay, and no lists
    """
    # Create a copy of the dance list to work with
    available_dances = dance_list.copy()
    
    # Randomly select number of dances for each category
    num_most = random.randint(min_most, min(max_most, len(available_dances)))
    
    # Select "most" dances
    most_dances = random.sample(available_dances, num_most)
    # Remove selected dances from available pool
    for dance in most_dances:
        available_dances.remove(dance)
    
    # Select "no" dances from remaining
    num_no = random.randint(min_no, min(max_no, len(available_dances)))
    no_dances = random.sample(available_dances, num_no)
    # Remove selected dances from available pool
    for dance in no_dances:
        available_dances.remove(dance)
    
    # Select "okay" dances from remaining
    num_okay = random.randint(min_okay, min(max_okay, len(available_dances)))
    okay_dances = random.sample(available_dances, num_okay)
    
    return {
        'most': ','.join(most_dances),
        'okay': ','.join(okay_dances),
        'no': ','.join(no_dances)
    }

def generate_random_ratings(all_dancers, num_dancers_needed):
    """
    Generate random ratings for dancers.
    
    Parameters:
    - all_dancers: List of all possible dancers
    - num_dancers_needed: Number of dancers needed for this dance
    
    Returns:
    - Dictionary with ratings 1-5, each containing a list of dancers
    """
    # Create a copy of the dancer list to work with
    available_dancers = all_dancers.copy()
    
    # Distribute dancers across ratings, with higher ratings getting more dancers
    ratings = {5: [], 4: [], 3: [], 2: [], 1: []}
    
    # Distribution weights (higher ratings get more dancers)
    distribution = {
        5: int(num_dancers_needed * 0.5),  # 50% of needed dancers
        4: int(num_dancers_needed * 0.7),  # 70% of needed dancers
        3: int(num_dancers_needed * 1.0),  # 100% of needed dancers
        2: int(num_dancers_needed * 0.7),  # 70% of needed dancers
        1: int(num_dancers_needed * 0.3),  # 30% of needed dancers
    }
    
    # Assign random dancers to each rating
    for rating in range(5, 0, -1):
        num_to_select = min(distribution[rating], len(available_dancers))
        selected_dancers = random.sample(available_dancers, num_to_select)
        ratings[rating] = selected_dancers
        
        # Remove selected dancers from available pool
        for dancer in selected_dancers:
            available_dancers.remove(dancer)
    
    return {
        'Rating_5': ','.join(ratings[5]),
        'Rating_4': ','.join(ratings[4]),
        'Rating_3': ','.join(ratings[3]),
        'Rating_2': ','.join(ratings[2]),
        'Rating_1': ','.join(ratings[1])
    }

def main():
    # Chinese dance list with number of dancers needed
    dances_with_sizes = {
        "淡妆浓抹总相宜": 8,
        "茉莉花": 10,
        "青山远黛": 6,
        "傣家女儿傣家雨": 12,
        "蛾儿雪柳": 8,
        "溯跃": 6,
        "云水伊人": 10,
        "喜马拉雅": 8,
        "东北秧歌小看戏": 12,
        "天鹅": 6,
        "一生一世": 8,
        "只此青绿": 10,
        "玉鸟": 8
    }
    
    dances = list(dances_with_sizes.keys())
    dancers = [f"name{i}" for i in range(1, 23)]
    experience_levels = ['none', 'beginner', 'intermediate', 'advanced']
    dance_ranges = ['1-2', '2-3', '3-4', '4-5', '5+']
    
    # Generate dancer preferences
    dancer_data = []
    for dancer in dancers:
        prefs = generate_random_preferences(dances.copy())
        dancer_data.append({
            'Name': dancer,
            'Experience': random.choice(experience_levels),
            'Dances': random.choice(dance_ranges),
            'Most': prefs['most'],
            'Okay': prefs['okay'],
            'No': prefs['no']
        })
    
    # Generate choreographer preferences
    choreo_data = []
    for dance, num_dancers in dances_with_sizes.items():
        ratings = generate_random_ratings(dancers.copy(), num_dancers)
        choreo_data.append({
            'Dance': dance,
            'NumDancers': num_dancers,
            'Rating_5': ratings['Rating_5'],
            'Rating_4': ratings['Rating_4'],
            'Rating_3': ratings['Rating_3'],
            'Rating_2': ratings['Rating_2'],
            'Rating_1': ratings['Rating_1']
        })
    
    # Create DataFrames and save to CSV
    dancer_df = pd.DataFrame(dancer_data)
    choreo_df = pd.DataFrame(choreo_data)
    
    dancer_df.to_csv('dancer_preferences.csv', index=False)
    choreo_df.to_csv('choreographer_preferences.csv', index=False)
    
    print("Generated files saved:")
    print("1. dancer_preferences.csv")
    print("2. choreographer_preferences.csv")
    
    print("\nExample of dancer preferences:")
    print(dancer_df.head().to_string())
    print("\nExample of choreographer preferences:")
    print(choreo_df.head().to_string())

if __name__ == "__main__":
    main()