import os
import yaml
import argparse
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import isodate
import re

# Define constants
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CLIENT_SECRETS_FILE = os.path.join("../../../", "client_secrets.json")  # Path to client_secrets.json
PODCAST_DIR = os.path.join(os.path.dirname(__file__), '..')  # Directory containing podcast episode folders

def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        return build("youtube", "v3", credentials=credentials)
    except FileNotFoundError:
        print(f"Error: Client secrets file not found at {CLIENT_SECRETS_FILE}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during authentication: {e}")
        sys.exit(1)

def get_youtube_duration(youtube, video_id):
    """Fetch the duration of a YouTube video using its video ID."""
    try:
        request = youtube.videos().list(
            part="contentDetails",
            id=video_id
        )
        response = request.execute()

        if not response["items"]:
            print(f"Video ID {video_id} not found or inaccessible.")
            return None

        # Extract duration in ISO 8601 format (e.g., PT1H23M45S)
        duration_iso = response["items"][0]["contentDetails"]["duration"]
        # Parse ISO 8601 duration to seconds
        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
        # Convert to HH:MM:SS format
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return duration_formatted
    except HttpError as e:
        print(f"Error fetching duration for video ID {video_id}: {e}")
        return None

def extract_youtube_id(url):
    """Extract YouTube video ID from a URL."""
    patterns = [
        r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/clip\/([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url  # Return as-is if no match (assuming it's already a video ID)

def check_for_missing_durations():
    """Scan folders for metadata.yml files missing duration but with a YouTube link."""
    parser = argparse.ArgumentParser(description="Update duration in metadata.yml files using YouTube API")
    parser.add_argument("--filename", type=str, help="Specify a single episode folder to process (e.g., '07_name')")
    parser.add_argument("--all", action="store_true", help="Process all episode folders (default unless --filename is specified)")
    args = parser.parse_args()

    if args.filename and args.all:
        print("Error: Cannot use --filename and --all together.")
        sys.exit(1)

    # Determine which folders to process
    episode_folders = []
    if args.filename:
        episode_path = os.path.join(PODCAST_DIR, args.filename)
        if not os.path.isdir(episode_path):
            print(f"Error: Specified folder {episode_path} does not exist or is not a directory.")
            sys.exit(1)
        episode_folders.append(args.filename)
    else:
        if not os.path.exists(PODCAST_DIR):
            print(f"Podcast directory {PODCAST_DIR} does not exist.")
            sys.exit(1)
        episode_folders = [f for f in os.listdir(PODCAST_DIR) if os.path.isdir(os.path.join(PODCAST_DIR, f))]

    if not episode_folders:
        print("No episode folders found to process.")
        sys.exit(1)

    # Check for metadata.yml files needing duration updates
    folders_needing_update = []
    for episode_folder in episode_folders:
        metadata_path = os.path.join(PODCAST_DIR, episode_folder, "metadata.yml")
        if not os.path.exists(metadata_path):
            print(f"Skipping {episode_folder}: metadata.yml not found.")
            continue

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                content = f.read()
                metadata = yaml.safe_load(content)
                if not isinstance(metadata, dict):
                    print(f"Error: {metadata_path} does not contain a valid YAML mapping.")
                    continue

                # Check if duration is missing and youtube link exists
                if not metadata.get("duration") and metadata.get("youtube"):
                    youtube_url = metadata.get("youtube")
                    video_id = extract_youtube_id(youtube_url)
                    if video_id:
                        folders_needing_update.append((episode_folder, metadata_path, youtube_url))
                    else:
                        print(f"Skipping {episode_folder}: Could not extract valid YouTube video ID.")
        except yaml.YAMLError as e:
            print(f"Error parsing {metadata_path}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {metadata_path}: {e}")
            continue

    if not folders_needing_update:
        print("No metadata.yml files found that need duration updates.")
        sys.exit(0)

    # Authenticate with YouTube API only if updates are needed
    youtube = get_authenticated_service()

    # Process folders needing updates
    updated_files = 0
    for episode_folder, metadata_path, youtube_url in folders_needing_update:
        try:
            # Fetch duration from YouTube API
            video_id = extract_youtube_id(youtube_url)
            duration = get_youtube_duration(youtube, video_id)
            if not duration:
                print(f"Skipping {episode_folder}: Failed to fetch duration for video ID {video_id}.")
                continue

            # Read original content to preserve formatting
            with open(metadata_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Append duration with an empty line
            lines = content.rstrip().splitlines()
            lines.append(f"duration: {duration}")
            lines.append("")
            updated_content = "\n".join(lines)

            # Write back to the file
            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"Updated {metadata_path}: Added duration {duration}.")
            updated_files += 1

        except Exception as e:
            print(f"Error processing {metadata_path}: {e}")
            continue

    print(f"\nProcessing complete. Updated {updated_files} metadata.yml file(s).")

if __name__ == "__main__":
    check_for_missing_durations()
