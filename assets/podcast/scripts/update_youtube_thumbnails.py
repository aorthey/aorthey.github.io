import os
import time
import yaml
import argparse
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Define the scope for YouTube API (read/write access)
SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = os.path.join("../../../", "client_secrets.json")  # Path to client_secrets.json in project root
PODCAST_DIR = os.path.join(os.path.dirname(__file__), '..')  # Directory containing podcast episode folders

def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def check_video_exists(youtube, video_id):
    """Check if a YouTube video exists."""
    try:
        request = youtube.videos().list(
            part="id",
            id=video_id
        )
        response = request.execute()
        return len(response.get("items", [])) > 0
    except HttpError as e:
        print(f"Error checking video ID {video_id}: {e}")
        return False

def set_video_thumbnail(youtube, video_id, thumbnail_path):
    """Update the thumbnail for a given video ID."""
    try:
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file {thumbnail_path} does not exist.")
            return False

        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        )
        response = request.execute()
        print(f"Thumbnail updated successfully for video ID {video_id}: {response}")
        return True
    except HttpError as e:
        print(f"An error occurred for video ID {video_id}: {e}")
        return False

def is_thumbnail_valid(thumbnail_path):
    """Check if thumbnail file exists and is a valid image."""
    if not os.path.exists(thumbnail_path):
        return False
    # Basic validation for PNG file
    if not thumbnail_path.lower().endswith('.png'):
        print(f"Thumbnail {thumbnail_path} is not a PNG file")
        return False
    # Could add more validation (e.g., image dimensions) if needed
    return True

def get_video_thumbnail_pairs(specific_folder=None):
    """Iterate through podcast folders to collect video IDs and thumbnail paths."""
    video_thumbnail_pairs = []

    if not os.path.exists(PODCAST_DIR):
        print(f"Podcast directory {PODCAST_DIR} does not exist.")
        return video_thumbnail_pairs

    # If specific folder is provided, only process that folder
    folders_to_process = [specific_folder] if specific_folder else os.listdir(PODCAST_DIR)

    for episode_folder in folders_to_process:
        episode_path = os.path.join(PODCAST_DIR, episode_folder)
        if not os.path.isdir(episode_path):
            print(f"{episode_path} is not a directory")
            continue

        # Check for thumbnail.png
        thumbnail_path = os.path.join(episode_path, "thumbnail.png")
        if not is_thumbnail_valid(thumbnail_path):
            print(f"Invalid or missing thumbnail in {episode_path}")
            continue

        # Check for metadata.yml
        metadata_path = os.path.join(episode_path, "metadata.yml")
        if not os.path.exists(metadata_path):
            print(f"No metadata.yml found in {episode_path}")
            continue

        # Parse metadata.yml to get YouTube video ID
        try:
            with open(metadata_path, "r") as f:
                metadata = yaml.safe_load(f)
                video_id = metadata.get("youtube")
                if not video_id:
                    print(f"No YouTube video ID found in {metadata_path}")
                    continue

                video_thumbnail_pairs.append({
                    "video_id": video_id,
                    "thumbnail_path": thumbnail_path,
                    "episode_folder": episode_folder
                })
        except yaml.YAMLError as e:
            print(f"Error parsing {metadata_path}: {e}")
            continue

    return video_thumbnail_pairs

def main():
    parser = argparse.ArgumentParser(description="Check or update YouTube video thumbnails")
    parser.add_argument("--update-youtube", action="store_true", help="Actually update thumbnails on YouTube")
    parser.add_argument("--filename", help="Process only the specified folder")
    args = parser.parse_args()

    # Get list of video IDs and thumbnail paths
    video_thumbnail_pairs = get_video_thumbnail_pairs(args.filename)

    if not video_thumbnail_pairs:
        print("No valid video ID and thumbnail pairs found.")
        return

    # Authenticate with YouTube API
    youtube = get_authenticated_service()

    # Process each video
    for pair in video_thumbnail_pairs:
        video_id = pair["video_id"]
        thumbnail_path = pair["thumbnail_path"]
        episode_folder = pair["episode_folder"]

        # Check if video exists
        if not check_video_exists(youtube, video_id):
            print(f"Video {video_id} does not exist for folder {episode_folder}")
            continue

        print(f"Valid video and thumbnail found for {episode_folder}: {video_id}")

        # Update thumbnail if --update-youtube is specified
        if args.update_youtube:
            success = set_video_thumbnail(youtube, video_id, thumbnail_path)
            if success:
                print(f"Waiting 10 seconds to avoid quota limits...")
                time.sleep(10)  # Delay to respect API quota limits

if __name__ == "__main__":
    main()
