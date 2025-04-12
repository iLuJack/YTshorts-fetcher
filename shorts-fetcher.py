# https://stackoverflow.com/questions/71192605/how-do-i-get-youtube-shorts-from-youtube-api-data-v3
import os
import requests
import json
from datetime import datetime, timezone
import time
from typing import List, Dict, Any, Optional
import dotenv
import csv
import re
# from list import youtubers

dotenv.load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
print(API_KEY)

def read_kpop_csv(filename="kpop-group-updated.csv"):
    """
    Reads data from a CSV file and returns a Python dictionary.

    Args:
        filename (str, optional): The name of the CSV file. Defaults to "kpop-group-updated.csv".

    Returns:
        dict: A dictionary where the keys are English group names and the values
              are dictionaries containing Korean names, YouTube channel URLs, and channel IDs.
    """
    data_dict = {}
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:  # Specify encoding
            reader = csv.reader(csvfile)
            header = next(reader)  # Read the header row
            for row in reader:
                if row:  # Ensure the row is not empty
                    english_name = row[0]
                    korean_name = row[1]
                    youtube_channel = row[2] if len(row) > 2 else None
                    channel_id = row[3] if len(row) > 3 else None
                    data_dict[english_name] = {
                        "korean": korean_name,
                        "youtube": youtube_channel,
                        "channel_id": channel_id
                    }
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data_dict

def extract_hashtags(description: str) -> List[str]:
    """Extract hashtags from video description"""
    hashtags = re.findall(r'#\w+', description)
    return hashtags

def get_shorts_playlist_id(channel_id: str) -> Optional[str]:
    """
    Create a shorts playlist ID from a channel ID by replacing 'UC' with 'UUSH'
    """
    if not channel_id or not channel_id.startswith("UC"):
        return None
    
    return "UUSH" + channel_id[2:]

def get_shorts_from_playlist(shorts_playlist_id: str, min_date: datetime = datetime(2020, 1, 1, tzinfo=timezone.utc)) -> List[Dict[str, Any]]:
    """
    Get all shorts videos from a shorts playlist and filter by date
    Since shorts are listed from newest to oldest, we can stop when we hit videos older than min_date
    """
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"
    shorts_videos = []
    page_token = None
    found_old_video = False
    
    # Use pagination to get all videos
    while True:
        params = {
            "key": API_KEY,
            "playlistId": shorts_playlist_id,
            "part": "snippet,contentDetails",
            "maxResults": 50  # Max allowed by API
        }
        
        if page_token:
            params["pageToken"] = page_token
        
        try:
            response = requests.get(url, params=params)
            playlist_data = response.json()
            
            if "error" in playlist_data:
                error_message = playlist_data["error"].get("message", "Unknown error")
                print(f"Error fetching playlist {shorts_playlist_id}: {error_message}")
                break
            
            if "items" in playlist_data:
                for item in playlist_data["items"]:
                    video_id = item["contentDetails"]["videoId"]
                    published_at = datetime.fromisoformat(item["snippet"]["publishedAt"].replace('Z', '+00:00'))
                    
                    # If we've reached a video before our min_date, we can stop checking more pages
                    if published_at < min_date:
                        found_old_video = True
                        continue
                        
                    # Get full video details
                    video_details = get_video_details(video_id)
                    
                    if video_details:
                        shorts_videos.append({
                            "video_id": video_id,
                            "title": item["snippet"]["title"],
                            "channel": item["snippet"]["channelTitle"],
                            "upload_time": published_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "views": video_details.get("views", 0),
                            "likes": video_details.get("likes", 0),
                            "comments": video_details.get("comments", 0),
                            "hashtags": video_details.get("hashtags", []),
                            "url": f"https://www.youtube.com/shorts/{video_id}"
                        })
                    
                    # Adding a short delay to avoid hitting API rate limits
                    time.sleep(0.5)
                
                # If we found an old video in this batch, no need to check next pages
                if found_old_video:
                    print(f"  Found videos older than {min_date.strftime('%Y-%m-%d')}, stopping pagination")
                    break
            
            # Check if there are more pages
            if "nextPageToken" in playlist_data and not found_old_video:
                page_token = playlist_data["nextPageToken"]
                print(f"  Fetching next page of results with token: {page_token}")
            else:
                break
            
        except Exception as e:
            print(f"Error processing shorts playlist {shorts_playlist_id}: {e}")
            break
            
    return shorts_videos

def get_video_details(video_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific video
    """
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": API_KEY,
        "id": video_id,
        "part": "statistics,contentDetails,snippet"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            return {}
        
        video_info = data["items"][0]
        description = video_info["snippet"].get("description", "")
        
        return {
            "views": int(video_info["statistics"].get("viewCount", 0)),
            "likes": int(video_info["statistics"].get("likeCount", 0)),
            "comments": int(video_info["statistics"].get("commentCount", 0)),
            "duration": video_info["contentDetails"]["duration"],
            "hashtags": extract_hashtags(description)
        }
    except Exception as e:
        print(f"Error getting video details for {video_id}: {e}")
        return {}

def try_alternative_shorts_methods(channel_id: str, min_date: datetime = datetime(2020, 1, 1, tzinfo=timezone.utc)) -> List[Dict[str, Any]]:
    """
    Try alternative methods to get shorts if the shorts playlist doesn't work
    """
    # Method 1: Get uploads and filter for shorts
    url = f"https://www.googleapis.com/youtube/v3/channels"
    params = {
        "key": API_KEY,
        "id": channel_id,
        "part": "contentDetails"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "items" not in data or len(data["items"]) == 0:
        return []
    
    uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Use pagination to get all videos
    shorts_videos = []
    page_token = None
    
    while True:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "key": API_KEY,
            "playlistId": uploads_playlist_id,
            "part": "snippet,contentDetails",
            "maxResults": 50  # Maximum allowed by YouTube API
        }
        
        if page_token:
            params["pageToken"] = page_token
        
        try:
            response = requests.get(url, params=params)
            playlist_data = response.json()
            
            if "items" in playlist_data:
                for item in playlist_data["items"]:
                    video_id = item["contentDetails"]["videoId"]
                    published_at = datetime.fromisoformat(item["snippet"]["publishedAt"].replace('Z', '+00:00'))
                    
                    # Skip videos before 2020/01/01
                    if published_at < min_date:
                        continue
                        
                    # Get full video details
                    video_details = get_video_details(video_id)
                    
                    # Only include shorts
                    if video_details:
                        shorts_videos.append({
                            "video_id": video_id,
                            "title": item["snippet"]["title"],
                            "channel": item["snippet"]["channelTitle"],
                            "upload_time": published_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "views": video_details.get("views", 0),
                            "likes": video_details.get("likes", 0),
                            "comments": video_details.get("comments", 0),
                            "hashtags": video_details.get("hashtags", []),
                            "url": f"https://www.youtube.com/shorts/{video_id}"
                        })
                    
                    # Adding a short delay to avoid hitting API rate limits
                    time.sleep(0.5)
            
            # Check if there are more pages
            if "nextPageToken" in playlist_data:
                page_token = playlist_data["nextPageToken"]
                print(f"  Fetching next page of uploads with token: {page_token}")
            else:
                break
                
        except Exception as e:
            print(f"Error processing uploads: {e}")
            break
    
    return shorts_videos

def fetch_single_group_shorts(group_name: str, group_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch shorts data for a single K-pop group and return it as a dictionary
    """
    results = {}
    min_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    
    channel_id = group_info.get("channel_id")
    if not channel_id:
        print(f"No YouTube channel ID for {group_name}, skipping")
        return results
        
    print(f"Fetching shorts for {group_name}")
    
    # First try using the shorts playlist
    shorts_playlist_id = get_shorts_playlist_id(channel_id)
    shorts = []
    
    if shorts_playlist_id:
        print(f"  Trying shorts playlist: {shorts_playlist_id} for {group_name}")
        shorts = get_shorts_from_playlist(shorts_playlist_id, min_date)
    
    # If no shorts found, try alternative methods
    if not shorts:
        print(f"  No shorts found in shorts playlist, trying alternative methods for {group_name}")
        # Uncomment the line below to try alternative methods
        # shorts = try_alternative_shorts_methods(channel_id, min_date)
    
    if shorts:
        results[group_name] = {
            "korean_name": group_info["korean"],
            "channel_id": channel_id,
            "channel_url": group_info["youtube"],
            "shorts_count": len(shorts),
            "shorts": shorts
        }
        print(f"  Found {len(shorts)} shorts for {group_name}")
    else:
        print(f"  No shorts found for {group_name}")
        
    return results

def save_results(data: Dict[str, Any], filename: str = "kpop_shorts_data.json"):
    """
    Save results to a JSON file.
    If the file already exists, load the existing data and combine it with the new data.
    """
    existing_data = {}
    
    # Try to load existing data from the file
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        print(f"Loaded existing data from {filename} with {len(existing_data)} groups")
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"No existing data found in {filename} or file is not valid JSON. Creating new file.")
    
    # Merge the existing data with the new data
    # New data will overwrite existing data for the same groups
    combined_data = {**existing_data, **data}
    
    # Write the combined data back to the file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved combined data to {filename}")

if __name__ == "__main__":
    # Load the K-pop group data from CSV
    kpop_data = read_kpop_csv("kpop-group-updated.csv")
    print(f"Found {len(kpop_data)} K-pop groups in CSV")
    
    # Process each group one by one, saving after each group
    for group_name, group_info in kpop_data.items():
        print(f"Processing group: {group_name}")
        
        # Fetch shorts for this specific group
        single_group_data = fetch_single_group_shorts(group_name, group_info)
        
        # Save the data immediately after processing each group
        if single_group_data:
            print(f"Saving shorts data for {group_name}")
            save_results(single_group_data, "kpop_shorts_data.json")
        else:
            print(f"No data to save for {group_name}")
        
        print(f"Completed processing {group_name}\n")

