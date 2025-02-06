# PCDC Dance Assignment Tool

A Python tool for optimizing dance assignments and show order for dance performances, designed specifically for PCDC (Penn Chinese Dance Company) or similar dance organizations.

## Overview

This tool helps solve two key problems in dance show organization:
1. Matching dancers to dances based on:
   - Dancer preferences (most wanted and okay with)
   - Choreographer ratings (1-5 scale)
   - Dancer experience levels
   - Desired number of dances per dancer
2. Optimizing the show order to minimize quick changes for dancers

## Prerequisites

- Python 3.8 or higher
- Required Python packages:
  ```bash
  pip install pandas networkx
  ```

## Setup Process

### 1. Prepare the Input Data
You'll need two separate CSV files:

#### Dancer Preferences CSV (`dancer_preferences.csv`)
Contains information about each dancer's preferences:
- Name: Dancer's full name
- Experience: none/beginner/intermediate/advanced
- Dances: Number of dances they want to participate in (1-2/2-3/3-4/4-5/5+)
- Most: Comma-separated list of dances they most want to join
- Okay: Comma-separated list of dances they're willing to join
- No: Comma-separated list of dances they do not want to join

#### Choreographer Preferences CSV (`choreographer_preferences.csv`)
Contains information about each dance and choreographer preferences:
- Dance: Name of the dance
- NumDancers: Maximum number of dancers needed (can be a range like "10-14" or options like "3,5")
- Rating_5: Comma-separated list of most-wanted dancers
- Rating_4: Comma-separated list of highly-wanted dancers
- Rating_3: Comma-separated list of wanted dancers
- Rating_2: Comma-separated list of acceptable dancers
- Rating_1: Comma-separated list of least-preferred dancers

Note: For ratings:
- It's okay to leave some rating categories empty
- Spaces around commas in the lists are optional
- Dancers who are rated 1 by more than 80% of choreographers will be excluded from assignments
- All dancers in rating lists must exist in the dancer preferences CSV

### 2. File Placement
Place both CSV files in the same directory as the script:
- `dancer_preferences.csv`
- `choreographer_preferences.csv`

## Running the Tool

Run the script: `python3 pcdcNEW.py`

## Output

The tool generates:

1. Console output showing:
   - Assignments summary for each dance
   - Optimized show order

2. Two CSV files:
   - `dance_assignments.csv`: Complete list of assignments with ratings
   - `show_order.csv`: Optimized performance order

## How It Works

1. **Data Loading**: 
   - Reads dancer preferences and choreographer ratings from separate CSV files
   - Parses desired dance ranges and experience levels
   - Validates that all rated dancers exist in the dancer list
   - Handles flexible dancer count requirements (ranges and options)

2. **Matching Algorithm**:
   - Identifies and excludes dancers rated poorly by >80% of choreographers
   - Respects dancers' "do not want" preferences (never assigns to these dances)
   - First pass: Assigns dancers to their "most wanted" dances
   - Second pass: Fills remaining spots with "okay with" preferences
   - Optimization pass: Improves assignments based on ratings

3. **Show Order Optimization**:
   - Creates a graph where:
     - Nodes represent dances
     - Edges represent shared dancers between dances
   - Uses a minimum spanning tree to minimize quick changes

## Setup Process - pcdcOLD

### 1. Prepare the Input Data
1. Use the [provided Google Sheets template](https://docs.google.com/spreadsheets/d/1ujp3BMIgsjc-Bwi_FJCohTYMzLsLyULVUY9hr0JExAk/edit?usp=sharing) to collect:
   - List of dances and maximum dancers per dance
   - List of dancers and maximum dances per dancer
   - Choreographer rankings (CR) for each dance
   - Dancer rankings (DR) for each dancer

2. Export the data:
   - Open the Google Sheet
   - Go to `File -> Download -> Comma Separated Values (.csv)`
   - Save the file as `pcdc - data.csv` in the same directory as the script

### 2. CSV File Format
Your CSV should include the following columns:
- `Dancers`: List of all dancer names
- `Max Dances/Dancer`: Maximum number of dances each dancer can participate in
- `Dances`: List of all dance names
- `Max Dancers/Dance`: Maximum number of dancers allowed in each dance
- `CR - {dance_name}`: Choreographer rankings for each dance
- `DR - {dancer_name}`: Dance preferences for each dancer


## Running the Tool - pcdcOLD

1. Place your CSV file in the same directory as `pcdc.py`
2. Run the script:
   ```bash
   python3 pcdc.py
   ```

## Output - pcdcOLD

The tool generates:
1. Console output showing:
   - Dance assignments (which dancers are in each dance)
   - Optimized show order to minimize quick changes
2. A CSV file (`pcdc_assignments.csv`) containing all assignments

## How It Works - pcdcOLD

1. **Data Loading**: Reads dancer and dance information from the CSV file
2. **Matching Algorithm**: Uses a modified version of the stable marriage algorithm to assign dancers to dances based on preferences
3. **Show Order Optimization**: Creates a graph where:
   - Nodes represent dances
   - Edges represent shared dancers between dances
   - Uses a minimum spanning tree to minimize quick changes

## Troubleshooting - pcdcOLD

Common issues:
1. **Column Name Errors**: Ensure your CSV column names exactly match the expected format:
   - Choreographer rankings: `CR - {dance_name}`
   - Dancer rankings: `DR - {dancer_name}`
2. **Missing Data**: All dancers and dances should have:
   - Maximum numbers specified
   - Complete ranking lists
   - No duplicate entries

## Limitations - pcdcOLD

- The tool assumes all preferences are provided
- Rankings must be complete (no partial rankings)
- Dance names and dancer names must be consistent throughout the spreadsheet

## License

MIT