import os
import time
import yaml
import argparse
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import re
from html import escape

# Define constants
SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = "client_secrets.json"  # Path to your client_secrets.json
PODCAST_DIR = "assets/podcast/"  # Directory containing podcast episode folders
GLOBAL_LINKS_FILE = os.path.join(PODCAST_DIR, "podcast-links.yml")  # Global podcast links
YOUTUBE_MAX_TITLE_LENGTH = 100  # YouTube's maximum title length
YOUTUBE_MAX_DESCRIPTION_LENGTH = 5000  # YouTube's maximum description length
SPOTIFY_MAX_TITLE_LENGTH = 200  # Spotify's maximum title length
SPOTIFY_MAX_DESCRIPTION_LENGTH = 4000  # Spotify's maximum description length

def get_authenticated_service():
    """Authenticate and return a YouTube API service object."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def update_video_metadata(youtube, video_id, title, description):
    """Update the title and description for a given video ID."""
    try:
        # Fetch current video details to preserve other metadata
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        if not response["items"]:
            print(f"Video ID {video_id} not found or inaccessible.")
            return False

        # Update title and description in snippet
        snippet = response["items"][0]["snippet"]
        snippet["title"] = title
        snippet["description"] = description

        # Update video with new metadata
        update_request = youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        )
        update_response = update_request.execute()
        print(f"Metadata updated successfully for video ID {video_id}: Title: {title}")
        return True
    except HttpError as e:
        print(f"An error occurred for video ID {video_id}: {e}")
        return False

def read_file_content(file_path):
    """Read content from a file, return empty string if file doesn't exist."""
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def convert_to_html_description(description_parts):
    """Convert description parts to HTML format for Spotify."""
    html_parts = []
    in_list = False

    for part in description_parts:
        if isinstance(part, list):
            # Handle list sections (e.g., Episode Links, References)
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            if part:  # Only start a list if there are items
                html_parts.append("<ul>")
                in_list = True
                for item in part:
                    if item.strip():  # Skip empty items
                        html_parts.append(f"<li>{escape(item.lstrip('- ').strip())}</li>")
        elif part.startswith("*") and part.endswith("*"):
            # Bold header (e.g., *References*)
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            header = escape(part[1:-1])
            html_parts.append(f"<b>{header}</b>")
        elif part == "":
            # Section separator
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append("<br>")
        else:
            # Plain text or outline (may contain * for bold first line)
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            lines = part.splitlines()
            formatted_lines = []
            for i, line in enumerate(lines):
                if i == 0 and line.startswith("*") and line.endswith("*"):
                    # Bold first line of outline
                    formatted_lines.append(f"<b>{escape(line[1:-1])}</b>")
                else:
                    formatted_lines.append(escape(line))
            html_parts.append(f"<p>{'<br>'.join(formatted_lines)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts).strip()

def get_video_metadata_pairs(generate_spotify=False):
    """Iterate through podcast folders to collect video IDs, titles, and descriptions."""
    video_metadata_pairs = []

    max_title_length = SPOTIFY_MAX_TITLE_LENGTH if generate_spotify else YOUTUBE_MAX_TITLE_LENGTH
    max_description_length = SPOTIFY_MAX_DESCRIPTION_LENGTH if generate_spotify else YOUTUBE_MAX_DESCRIPTION_LENGTH

    if not os.path.exists(PODCAST_DIR):
        print(f"Podcast directory {PODCAST_DIR} does not exist.")
        return video_metadata_pairs

    # Read global podcast-links.yml
    global_links = read_file_content(GLOBAL_LINKS_FILE)
    # Format global links as list of individual items
    global_links_formatted = []
    if global_links:
        global_links_formatted = [f"- {line}" for line in global_links.splitlines() if line.strip()]

    # Iterate through all subfolders in assets/podcast/
    for episode_folder in os.listdir(PODCAST_DIR):
        episode_path = os.path.join(PODCAST_DIR, episode_folder)
        if not os.path.isdir(episode_path):
            continue

        # Check for required files: links.yml, outline.txt, description.txt
        links_path = os.path.join(episode_path, "links.yml")
        outline_path = os.path.join(episode_path, "outline.txt")
        description_path = os.path.join(episode_path, "description.txt")

        missing_files = []
        if not os.path.exists(links_path):
            missing_files.append("links.yml")
        if not os.path.exists(outline_path):
            missing_files.append("outline.txt")
        if not os.path.exists(description_path):
            missing_files.append("description.txt")

        if missing_files:
            print(f"Error: Missing required files in {episode_path}: {', '.join(missing_files)}")
            continue

        # Parse links.yml to get YouTube video ID, title, and other links
        try:
            with open(links_path, "r") as f:
                links_data = yaml.safe_load(f)
                video_id = links_data.get("youtube")
                title = links_data.get("title")
                spotify_link = links_data.get("spotify")
                apple_link = links_data.get("apple")
                if not video_id and not generate_spotify:
                    print(f"No YouTube video ID found in {links_path}")
                    continue
                if not title:
                    print(f"No title found in {links_path}")
                    continue

                # Extract leading number from folder name (e.g., "03" from "03_james_kuffner")
                match = re.match(r"^(\d+)_", episode_folder)
                if not match:
                    print(f"Warning: Could not extract episode number from folder {episode_folder}")
                    continue
                episode_number = match.group(1).lstrip("0") or "0"  # Remove leading zeros, handle "00" case

                # Extend title with " | Andreas Orthey #N"
                extended_title = f"{title} | Andreas Orthey #{episode_number}"

                # Validate title length
                if len(extended_title) > max_title_length:
                    raise ValueError(f"Extended title in {links_path} is too long ({len(extended_title)} characters, max {max_title_length}): {extended_title}")

                # Construct description
                description_parts = []

                # 1. Read description.txt
                description_content = read_file_content(description_path)
                if description_content:
                    description_parts.append(description_content)
                    description_parts.append("")

                # 2. Read outline.txt, bold first line (no list formatting)
                outline_content = read_file_content(outline_path)
                if outline_content:
                    outline_lines = outline_content.splitlines()
                    if outline_lines:
                        outline_lines[0] = f"*{outline_lines[0]}*"
                        outline_content = "\n".join(outline_lines)
                    description_parts.append(outline_content)
                    description_parts.append("")

                # 3. Read references.txt with bold header and list formatting
                references_content = read_file_content(os.path.join(episode_path, "references.txt"))
                references_formatted = []
                if references_content:
                    references_formatted = [f"- {line}" for line in references_content.splitlines() if line.strip()]
                    description_parts.append("*References*")
                    description_parts.append(references_formatted)
                    description_parts.append("")

                # 4. Construct Episode Links section
                episode_links_parts = []
                # Add Spotify and Apple links from links.yml
                if spotify_link:
                    episode_links_parts.append(f"- Spotify: {spotify_link}")
                if apple_link:
                    episode_links_parts.append(f"- Apple: {apple_link}")
                # Read episode-links.yml and format as list
                episode_links_content = read_file_content(os.path.join(episode_path, "episode-links.yml"))
                if episode_links_content:
                    episode_links_parts.extend(f"- {line}" for line in episode_links_content.splitlines() if line.strip())
                # Combine episode links if any exist
                if episode_links_parts:
                    description_parts.append("*Episode Links*")
                    description_parts.append(episode_links_parts)
                    description_parts.append("")

                # 5. Add global podcast-links.yml with bold header and list formatting
                if global_links_formatted:
                    description_parts.append("*Podcast Links*")
                    description_parts.append(global_links_formatted)
                    description_parts.append("")

                # 6. Read errata.txt with bold header and list formatting
                errata_content = read_file_content(os.path.join(episode_path, "errata.txt"))
                errata_formatted = []
                if errata_content:
                    errata_formatted = [f"- {line}" for line in errata_content.splitlines() if line.strip()]
                    description_parts.append("*Errata*")
                    description_parts.append(errata_formatted)
                    description_parts.append("")

                # Combine description parts for YouTube
                description = "\n".join(str(part) if not isinstance(part, list) else "\n".join(part) for part in description_parts).strip()

                # Convert to HTML for Spotify
                if generate_spotify:
                    description = convert_to_html_description(description_parts)

                # Validate description length
                if len(description) > max_description_length:
                    print(f"Warning: Description for video ID {video_id} in {episode_path} is too long ({len(description)} characters, max {max_description_length})")
                    continue

                # Add to pairs list
                pair = {
                    "title": extended_title,
                    "description": description
                }
                if not generate_spotify:
                    pair["video_id"] = video_id
                video_metadata_pairs.append(pair)
        except yaml.YAMLError as e:
            print(f"Error parsing {links_path}: {e}")
            continue

    return video_metadata_pairs

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update YouTube video titles and descriptions or generate Spotify metadata")
    parser.add_argument("--update-youtube", action="store_true", help="Update titles and descriptions on YouTube")
    parser.add_argument("--generate-spotify", action="store_true", help="Generate titles and HTML descriptions for Spotify")
    args = parser.parse_args()

    # Get list of video IDs, titles, and descriptions
    if args.generate_spotify:
        video_metadata_pairs = get_video_metadata_pairs(generate_spotify=True)
        platform = "Spotify"
    else:
        video_metadata_pairs = get_video_metadata_pairs(generate_spotify=False)
        platform = "YouTube"

    if not video_metadata_pairs:
        print(f"No valid {platform} metadata pairs found.")
        return

    # Display video IDs, titles, and descriptions
    print(f"{platform} Metadata:")
    for pair in video_metadata_pairs:
        print(f"{'-' * 80}")
        if "video_id" in pair:
            print(f"Video ID: {pair['video_id']}")
        print(f"Title:\n{pair['title']}")
        print(f"Description:\n{pair['description']}\n")

    # Update metadata if --update-youtube is provided
    if args.update_youtube:
        if args.generate_spotify:
            print("Warning: --update-youtube will use YouTube-specific metadata, ignoring --generate-spotify for updates.")
            video_metadata_pairs = get_video_metadata_pairs(generate_spotify=False)
        # Authenticate with YouTube API
        youtube = get_authenticated_service()

        # Update titles and descriptions for each video
        for pair in video_metadata_pairs:
            video_id = pair["video_id"]
            title = pair["title"]
            description = pair["description"]
            success = update_video_metadata(youtube, video_id, title, description)
            if success:
                print(f"Waiting 10 seconds to avoid quota limits...")
                time.sleep(10)  # Delay to respect API quota limits

if __name__ == "__main__":
    main()
