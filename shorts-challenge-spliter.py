import json
import pandas as pd
from typing import Set, Dict, List, Any, Tuple
from collections import defaultdict

shorts_data_path = "./data-processed/kpop_shorts_data_hashtag_processed.json"
idol_data_path = "./data-original/kpop-idol.csv"
challenge_output_path = "./data-processed/v2-kpop-challenge-shorts.json"
non_challenge_output_path = "./data-processed/v2-kpop-non-challenge-shorts.json"

def is_challenge_short(hashtags: List[str]) -> bool:
    for hashtag in hashtags:
        if "challenge" in hashtag.lower():
            return True
    return False

def main():
    # Load the datasets
    with open(shorts_data_path, 'r') as f:
        json_data = json.load(f)
    
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
            if is_challenge_short(short["hashtags"]):
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
    
    print(f"Total challenge shorts (有 hashtag 包含 challenge): {total_challenge}")
    print(f"Total non-challenge shorts (沒有 hashtag 包含 challenge): {total_non_challenge}")

if __name__ == "__main__":
    main()