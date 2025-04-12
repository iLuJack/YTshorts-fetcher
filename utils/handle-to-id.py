import os
import csv
import requests
import time
import dotenv
from typing import List, Dict, Tuple

dotenv.load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_id_from_handle(handle: str) -> str:
    """
    Get channel ID from a YouTube handle (starting with @)
    """
    if not handle or not handle.strip():
        return None
        
    # Remove @ if it exists to make the query more reliable
    query = handle[1:] if handle.startswith('@') else handle
    
    url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "q": query,
        "type": "channel",
        "part": "id,snippet"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            print(f"No results found for handle: {handle}")
            return None
        
        return data["items"][0]["id"]["channelId"]
    except Exception as e:
        print(f"Error getting channel ID for {handle}: {e}")
        return None

def process_youtube_handle(handle: str) -> Tuple[str, str]:
    """Process YouTube handle and return channel ID"""
    if not handle or not handle.strip():
        return handle, ""
    
    # Handle special cases like YouTube shorts links
    if "shorts/" in handle:
        return handle, ""  # Can't easily extract from shorts URLs without web scraping
        
    # Extract handle if it's a URL
    if "youtube.com" in handle:
        if "/@" in handle:
            handle = "@" + handle.split("/@")[1].split("/")[0]
        elif "/c/" in handle:
            handle = "@" + handle.split("/c/")[1].split("/")[0]
            
    # If it's already a handle starting with @, get channel ID
    if handle.startswith("@"):
        channel_id = get_channel_id_from_handle(handle)
        if channel_id:
            return handle, channel_id
            
    return handle, ""

def update_csv_with_channel_ids(input_file: str, output_file: str):
    """Update CSV with YouTube channel IDs"""
    rows = []
    updated_count = 0
    
    # Read the CSV
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        
        # Add a new column for channel ID if it doesn't exist
        if len(header) < 4:
            header.append("Channel ID")
        
        rows.append(header)
        
        for row in reader:
            if len(row) > 2 and row[2]:  # If there's a YouTube channel handle/URL
                handle = row[2]
                print(f"Processing: {row[0]} with handle {handle}")
                
                handle, channel_id = process_youtube_handle(handle)
                
                # Make sure the row has enough columns
                while len(row) < 4:
                    row.append("")
                    
                if channel_id:
                    row[3] = channel_id
                    updated_count += 1
                    print(f"Found channel ID for {row[0]}: {channel_id}")
                else:
                    print(f"Could not find channel ID for {row[0]}")
            
            rows.append(row)
            # Add a small delay to prevent hitting API limits
            time.sleep(0.5)
    
    # Write the updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    
    print(f"Updated {updated_count} channel IDs. Results saved to {output_file}")

if __name__ == "__main__":
    update_csv_with_channel_ids("kpop-group.csv", "kpop-group-updated.csv")