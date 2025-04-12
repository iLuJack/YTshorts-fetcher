import json
import pandas as pd
from typing import Set, Dict, List, Any, Tuple
from collections import defaultdict

shorts_data_path = "./data-processed/kpop_shorts_data_hashtag_processed.json"
idol_data_path = "./data-original/kpop-idol.csv"
challenge_output_path = "./data-processed/kpop-challenge-shorts.json"
non_challenge_output_path = "./data-processed/kpop-non-challenge-shorts.json"

def create_name_to_group_mapping(idol_data: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    """Create mappings from names to groups and groups to their members"""
    name_to_group = {}
    group_to_members = defaultdict(set)
    
    # Process English names
    for _, row in idol_data.iterrows():
        name = row['name (english)'].lower()
        group = row['group (english)'].lower()
        
        name_to_group[name] = group
        group_to_members[group].add(name)
        
        # Also add Korean names
        k_name = row['name (korean)'].lower()
        k_group = row['group (korean)'].lower()
        
        name_to_group[k_name] = group
        group_to_members[group].add(k_name)
        
    # Also map group names to themselves
    for group in group_to_members:
        name_to_group[group] = group
        # Add Korean group name version too
        k_group = idol_data[idol_data['group (english)'].str.lower() == group]['group (korean)'].iloc[0].lower()
        name_to_group[k_group] = group
    print(group_to_members)
    return name_to_group, group_to_members

def is_challenge_short(hashtags: List[str], name_to_group: Dict[str, str], 
                       group_to_members: Dict[str, Set[str]], current_group: str) -> bool:
    """
    Check if a short is a challenge based on hashtags.
    A challenge short must contain:
    1. At least one reference to the current group or its members, AND
    2. At least one reference to a different group or its members
    """
    # Clean and lowercase hashtags
    clean_tags = [tag.lower().strip('#') for tag in hashtags]
    current_group = current_group.lower()
    
    # Track if we've found the current group and any other group
    found_own_group = False
    found_other_group = False
    
    # Find all mentioned groups in hashtags
    mentioned_groups = set()
    
    for tag in clean_tags:
        if tag in name_to_group:
            group = name_to_group[tag]
            mentioned_groups.add(group)
            
            if group == current_group:
                found_own_group = True
            else:
                found_other_group = True
    
    # Return true only if both conditions are met
    if(found_own_group and found_other_group):
        return True
    return False
def main():
    # Load the datasets
    idol_data = pd.read_csv(idol_data_path)
    with open(shorts_data_path, 'r') as f:
        json_data = json.load(f)
    
    # Create mappings
    name_to_group, group_to_members = create_name_to_group_mapping(idol_data)
    
    # Initialize output dictionaries
    challenge_shorts = {}
    non_challenge_shorts = {}
    
    # Process each group and its shorts
    for group, group_data in json_data.items():
        challenge_shorts[group] = {
            "korean_name": group_data["korean_name"],
            "channel_id": group_data["channel_id"],
            "channel_url": group_data["channel_url"],
            "shorts_count": 0,
            "shorts": []
        }
        
        non_challenge_shorts[group] = {
            "korean_name": group_data["korean_name"],
            "channel_id": group_data["channel_id"],
            "channel_url": group_data["channel_url"],
            "shorts_count": 0,
            "shorts": []
        }
        
        for short in group_data["shorts"]:
            if is_challenge_short(short["hashtags"], name_to_group, group_to_members, group):
                challenge_shorts[group]["shorts"].append(short)
                challenge_shorts[group]["shorts_count"] += 1
            else:
                non_challenge_shorts[group]["shorts"].append(short)
                non_challenge_shorts[group]["shorts_count"] += 1
    
    # Filter out groups with no shorts in respective categories
    challenge_shorts = {k: v for k, v in challenge_shorts.items() if v["shorts_count"] > 0}
    non_challenge_shorts = {k: v for k, v in non_challenge_shorts.items() if v["shorts_count"] > 0}
    
    # Write output files
    with open(challenge_output_path, 'w', encoding='utf-8') as f:
        json.dump(challenge_shorts, f, ensure_ascii=False, indent=2)
    
    with open(non_challenge_output_path, 'w', encoding='utf-8') as f:
        json.dump(non_challenge_shorts, f, ensure_ascii=False, indent=2)
    
    print(f"Challenge shorts saved to {challenge_output_path}")
    print(f"Non-challenge shorts saved to {non_challenge_output_path}")
    
    # Print some statistics
    total_challenge = sum(data["shorts_count"] for data in challenge_shorts.values())
    total_non_challenge = sum(data["shorts_count"] for data in non_challenge_shorts.values())
    
    print(f"Total challenge shorts: {total_challenge}")
    print(f"Total non-challenge shorts: {total_non_challenge}")

if __name__ == "__main__":
    main()