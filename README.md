# PCDC Dance Assignment Tool

A Python tool for optimizing dance assignments and show order for dance performances, designed specifically for PCDC (Penn Chinese Dance Company) or similar dance organizations.

## Overview

This tool helps solve two key problems in dance show organization:
1. Matching dancers to dances based on both choreographer and dancer preferences
2. Optimizing the show order to minimize quick changes for dancers

## Prerequisites

- Python 3.8 or higher
- Required Python packages:
  ```bash
  pip install pandas networkx
  ```

## Setup Process

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


## Running the Tool

1. Place your CSV file in the same directory as `pcdc.py`
2. Run the script:
   ```bash
   python3 pcdc.py
   ```

## Output

The tool generates:
1. Console output showing:
   - Dance assignments (which dancers are in each dance)
   - Optimized show order to minimize quick changes
2. A CSV file (`pcdc_assignments.csv`) containing all assignments

## How It Works

1. **Data Loading**: Reads dancer and dance information from the CSV file
2. **Matching Algorithm**: Uses a modified version of the stable marriage algorithm to assign dancers to dances based on preferences
3. **Show Order Optimization**: Creates a graph where:
   - Nodes represent dances
   - Edges represent shared dancers between dances
   - Uses a minimum spanning tree to minimize quick changes

## Troubleshooting

Common issues:
1. **Column Name Errors**: Ensure your CSV column names exactly match the expected format:
   - Choreographer rankings: `CR - {dance_name}`
   - Dancer rankings: `DR - {dancer_name}`
2. **Missing Data**: All dancers and dances should have:
   - Maximum numbers specified
   - Complete ranking lists
   - No duplicate entries

## Limitations

- The tool assumes all preferences are provided
- Rankings must be complete (no partial rankings)
- Dance names and dancer names must be consistent throughout the spreadsheet

## License

MIT