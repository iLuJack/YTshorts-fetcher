from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

def download_video(url, output_path):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Downloading: {yt.title}")
        ys = yt.streams.get_highest_resolution()
        downloaded_path = ys.download(output_path=output_path)
        print(f"Video downloaded to: {downloaded_path}")
        return downloaded_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    download_video(url, "videos")
    