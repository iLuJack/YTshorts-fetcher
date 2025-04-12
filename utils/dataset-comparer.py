import json
import pandas as pd
from typing import Set, Dict, List, Any

shorts_data_path = "../data-processed/kpop_shorts_data.json"
group_data_path = "../data-original/kpop-group.csv"
idol_data_path = "../data-original/kpop-idol.csv"

def compare_group_sets(json_data_keys: Set[str], csv_groups: Set[str]) -> Dict[str, List[str]]:
    """
    Compare two sets of group names and return groups unique to each set
    """
    only_in_json = list(json_data_keys - csv_groups)
    only_in_csv = list(csv_groups - json_data_keys)
    in_both = list(json_data_keys & csv_groups)
    
    return {
        "only_in_json_data": sorted(only_in_json),
        "only_in_csv_data": sorted(only_in_csv),
        "in_both_datasets": sorted(in_both)
    }

def main():
    # Load the datasets
    group_data = pd.read_csv(group_data_path)
    idol_data = pd.read_csv(idol_data_path)
    
    try:
        with open(shorts_data_path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the JSON file at {shorts_data_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: The file at {shorts_data_path} is not valid JSON")
        return
    
    # Extract group names
    json_groups = set(json_data.keys())
    csv_groups = set(group_data["group (english)"])
    
    # Compare the sets
    comparison = compare_group_sets(json_groups, csv_groups)
    
    # Print the results
    print(f"Total groups in JSON data: {len(json_groups)}")
    print(f"Total groups in CSV data: {len(csv_groups)}")
    print("\n" + "="*50)
    
    print("\nGroups only in JSON data (not in CSV):")
    if comparison["only_in_json_data"]:
        for i, group in enumerate(comparison["only_in_json_data"], 1):
            print(f"{i}. {group}")
    else:
        print("None")
    
    print("\nGroups only in CSV data (not in JSON):")
    if comparison["only_in_csv_data"]:
        for i, group in enumerate(comparison["only_in_csv_data"], 1):
            print(f"{i}. {group}")
    else:
        print("None")
    
    print(f"\nNumber of groups in both datasets: {len(comparison['in_both_datasets'])}")
    
    # Optional: If you want to see the list of groups in both datasets
    print("\nGroups in both datasets:")
    for i, group in enumerate(comparison["in_both_datasets"], 1):
        print(f"{i}. {group}")
    
    # Calculate coverage
    coverage_percentage = (len(comparison["in_both_datasets"]) / len(csv_groups)) * 100
    print(f"\nCoverage: {coverage_percentage:.2f}% of CSV groups are in the JSON data")

if __name__ == "__main__":
    main()