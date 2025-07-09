import os
import time
import yaml
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# Define the scope for YouTube API (read/write access)
SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = "client_secrets.json"  # Path to your client_secrets.json
PODCAST_DIR = "assets/podcast/"  # Directory containing podcast episode folders

def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def set_video_thumbnail(youtube, video_id, thumbnail_path):
    """Update the thumbnail for a given video ID."""
    try:
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file {thumbnail_path} does not exist.")
            return False

        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_path
        )
        response = request.execute()
        print(f"Thumbnail updated successfully for video ID {video_id}: {response}")
        return True
    except HttpError as e:
        print(f"An error occurred for video ID {video_id}: {e}")
        return False

def get_video_thumbnail_pairs():
    """Iterate through podcast folders to collect video IDs and thumbnail paths."""
    video_thumbnail_pairs = []

    if not os.path.exists(PODCAST_DIR):
        print(f"Podcast directory {PODCAST_DIR} does not exist.")
        return video_thumbnail_pairs

    # Iterate through all subfolders in assets/podcast/
    for episode_folder in os.listdir(PODCAST_DIR):
        episode_path = os.path.join(PODCAST_DIR, episode_folder)
        if not os.path.isdir(episode_path):
            continue

        # Check for thumbnail.png
        thumbnail_path = os.path.join(episode_path, "thumbnail.png")
        if not os.path.exists(thumbnail_path):
            print(f"No thumbnail found in {episode_path}")
            continue

        # Check for links.yml
        links_path = os.path.join(episode_path, "links.yml")
        if not os.path.exists(links_path):
            print(f"No links.yml found in {episode_path}")
            continue

        # Parse links.yml to get YouTube video ID
        try:
            with open(links_path, "r") as f:
                links_data = yaml.safe_load(f)
                video_id = links_data.get("youtube")
                if not video_id:
                    print(f"No YouTube video ID found in {links_path}")
                    continue

                # Add to pairs list
                video_thumbnail_pairs.append({
                    "video_id": video_id,
                    "thumbnail_path": thumbnail_path
                })
        except yaml.YAMLError as e:
            print(f"Error parsing {links_path}: {e}")
            continue

    return video_thumbnail_pairs

def main():
    # Get list of video IDs and thumbnail paths
    video_thumbnail_pairs = get_video_thumbnail_pairs()

    if not video_thumbnail_pairs:
        print("No valid video ID and thumbnail pairs found.")
        return

    # Authenticate with YouTube API
    youtube = get_authenticated_service()

    # Update thumbnails for each video
    for pair in video_thumbnail_pairs:
        video_id = pair["video_id"]
        thumbnail_path = pair["thumbnail_path"]
        success = set_video_thumbnail(youtube, video_id, thumbnail_path)
        if success:
            print(f"Waiting 10 seconds to avoid quota limits...")
            time.sleep(10)  # Delay to respect API quota limits

if __name__ == "__main__":
    main()

