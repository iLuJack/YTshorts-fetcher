import json
import re
import os
from typing import Dict, List, Any

# File paths
shorts_data_path = "./data-processed/kpop_shorts_data.json"
output_path = "./data-processed/kpop_shorts_data_processed.json"

def extract_hashtags_from_title(title: str) -> List[str]:
    """
    Extract hashtags from a title string using regex
    """
    hashtags = re.findall(r'#\w+', title)
    return hashtags

def process_hashtags(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process each short in the JSON data:
    1. Extract hashtags from the title
    2. Add them to the existing hashtags list (avoid duplicates)
    """
    processed_data = json_data.copy()
    
    # Stats counters
    total_groups = 0
    total_shorts = 0
    total_hashtags_before = 0
    total_hashtags_after = 0
    total_hashtags_added = 0
    
    for group_name, group_info in processed_data.items():
        if "shorts" not in group_info:
            continue
            
        total_groups += 1
        
        for short in group_info["shorts"]:
            total_shorts += 1
            
            # Initialize hashtags list if it doesn't exist
            if "hashtags" not in short:
                short["hashtags"] = []
                
            # Count existing hashtags
            total_hashtags_before += len(short["hashtags"])
            
            # Extract hashtags from title
            title_hashtags = extract_hashtags_from_title(short["title"])
            
            # Add non-duplicate hashtags to the list
            for hashtag in title_hashtags:
                if hashtag not in short["hashtags"]:
                    short["hashtags"].append(hashtag)
                    total_hashtags_added += 1
                    
            # Count hashtags after processing
            total_hashtags_after += len(short["hashtags"])
    
    # Print statistics
    print(f"Processed {total_shorts} shorts across {total_groups} groups")
    print(f"Total hashtags before: {total_hashtags_before}")
    print(f"Total hashtags after: {total_hashtags_after}")
    print(f"Added {total_hashtags_added} new hashtags from titles")
    
    return processed_data

def main():
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load the JSON data
    print(f"Loading data from {shorts_data_path}...")
    try:
        with open(shorts_data_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {shorts_data_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {shorts_data_path}")
        return
        
    print(f"Successfully loaded data with {len(json_data)} groups")
    
    # Process the hashtags
    print("Processing hashtags...")
    processed_data = process_hashtags(json_data)
    
    # Save the processed data
    print(f"Saving processed data to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()