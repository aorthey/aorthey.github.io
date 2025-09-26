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
CLIENT_SECRETS_FILE = os.path.join("../../../", "client_secrets.json")  # Path to client_secrets.json in project root
PODCAST_DIR = os.path.join(os.path.dirname(__file__), '..')  # Directory containing podcast episode folders
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
            sys.exit(1)

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
        sys.exit(1)

def read_file_content(file_path):
    """Read content from a file, return empty string if file doesn't exist."""
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

def convert_to_html_description(description_parts):
    """Convert description parts to HTML format for Spotify."""
    html_parts = []
    in_list = False

    for part in description_parts:
        if isinstance(part, list):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            if part:
                html_parts.append("<ul>")
                in_list = True
                for item in part:
                    if item.strip():
                        html_parts.append(f"<li>{escape(item.lstrip('- ').strip())}</li>")
        elif part.startswith("*") and part.endswith("*"):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            header = escape(part[1:-1])
            html_parts.append(f"<b>{header}</b>")
        elif part == "":
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append("<br>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            lines = part.splitlines()
            formatted_lines = []
            for line in lines:
                formatted_lines.append(escape(line))
            html_parts.append(f"<p>{'<br>'.join(formatted_lines)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts).strip()

def get_video_metadata_pairs(generate_spotify=False, filename=None):
    """Iterate through podcast folders or a specific file to collect video IDs, titles, and descriptions."""
    video_metadata_pairs = []

    max_title_length = SPOTIFY_MAX_TITLE_LENGTH if generate_spotify else YOUTUBE_MAX_TITLE_LENGTH
    max_description_length = SPOTIFY_MAX_DESCRIPTION_LENGTH if generate_spotify else YOUTUBE_MAX_DESCRIPTION_LENGTH

    if not os.path.exists(PODCAST_DIR):
        print(f"Podcast directory {PODCAST_DIR} does not exist.")
        sys.exit(1)

    # Read global podcast-links.yml
    global_links = read_file_content(GLOBAL_LINKS_FILE)
    global_links_formatted = []
    if global_links:
        global_links_formatted = [f"- {line}" for line in global_links.splitlines() if line.strip()]

    # Determine which folders to process
    episode_folders = []
    if filename:
        episode_path = os.path.join(PODCAST_DIR, filename)
        if not os.path.isdir(episode_path):
            print(f"Error: Specified folder {episode_path} does not exist or is not a directory.")
            sys.exit(1)
        episode_folders.append(filename)
    else:
        # Process all folders
        for folder in os.listdir(PODCAST_DIR):
            if os.path.isdir(os.path.join(PODCAST_DIR, folder)):
                episode_folders.append(folder)

    # Iterate through selected folders
    for episode_folder in episode_folders:
        episode_path = os.path.join(PODCAST_DIR, episode_folder)
        if not os.path.isdir(episode_path):
            continue

        # Check for metadata.yml
        metadata_path = os.path.join(episode_path, "metadata.yml")
        if not os.path.exists(metadata_path):
            print(f"Error: Missing metadata.yml in {metadata_path}")
            continue

        # Parse metadata.yml
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)
                if not isinstance(data, dict):
                    print(f"Error: {metadata_path} does not contain a valid YAML mapping")
                    sys.exit(1)

                # Extract required fields
                title = data.get("title")
                description = data.get("description")
                video_id = data.get("youtube")
                spotify_link = data.get("spotify")
                apple_link = data.get("apple")
                x_link = data.get("x")
                books_list = data.get("books") or []

                # Validate required fields
                if not title:
                    print(f"No title found in {metadata_path}")
                    sys.exit(1)
                if not description:
                    print(f"No description found in {metadata_path}")
                    sys.exit(1)

                # Extract episode number from folder name
                match = re.match(r"^(\d+)_", episode_folder)
                if not match:
                    print(f"Warning: Could not extract episode number from folder {episode_folder}")
                    sys.exit(1)
                episode_number = match.group(1).lstrip("0") or "0"

                # Extend title
                extended_title = f"{title} | Andreas Orthey #{episode_number}"

                # Validate title length
                if len(extended_title) > max_title_length:
                    print(f"Extended title in {metadata_path} is too long ({len(extended_title)} characters, max {max_title_length}): {extended_title}")
                    sys.exit(1)

                # Construct description
                description_parts = []

                # Description
                if description:
                    description_parts.append(description)
                    description_parts.append("")

                # Content (outline) with *Outline* header
                content_list = data.get("content") or []
                outline_content = []
                for item in content_list:
                    prefix = f""
                    if isinstance(item, str) and item.strip():
                        outline_content.append(f"{prefix}{item}")
                    elif isinstance(item, dict) and len(item) == 1:
                        key = list(item.keys())[0]
                        value = list(item.values())[0]
                        if isinstance(key, str) and isinstance(value, str):
                            formatted = f"{prefix}{key}: {value}"
                            outline_content.append(formatted)
                        else:
                            print(f"Warning: Invalid dict outline format in {metadata_path}: {item}. Converting to string.")
                            outline_content.append(f"{prefix}{str(item).strip()}")
                    else:
                        print(f"Warning: Invalid outline format in {metadata_path}: {item}. Converting to string.")
                        outline_content.append(f"{prefix}{str(item).strip()}")
                if outline_content:
                    description_parts.append("*Outline*")
                    description_parts.append(outline_content)
                    description_parts.append("")

                # References
                references_list = data.get("references") or []
                references_formatted = []
                counter = 1
                for item in references_list:
                    prefix = f"- [{counter}] "
                    counter += 1
                    if isinstance(item, str) and item.strip():
                        references_formatted.append(f"{prefix}{item}")
                    elif isinstance(item, dict) and len(item) == 1:
                        key = list(item.keys())[0]
                        value = list(item.values())[0]
                        if isinstance(key, str) and isinstance(value, str):
                            formatted = f"{prefix}{key}: {value}"
                            references_formatted.append(formatted)
                        else:
                            print(f"Warning: Invalid dict reference format in {metadata_path}: {item}. Converting to string.")
                            references_formatted.append(f"{prefix}{str(item).strip()}")
                    else:
                        print(f"Warning: Invalid reference format in {metadata_path}: {item}. Converting to string.")
                        references_formatted.append(f"{prefix}{str(item).strip()}")
                if references_formatted:
                    description_parts.append("*References*")
                    description_parts.append(references_formatted)
                    description_parts.append("")


                # Books
                books_formatted = []
                for item in books_list:
                    # Ensure item is treated as a string, preserving colons
                    if isinstance(item, dict):
                        # If parsed as a dict, reconstruct as string (e.g., "Vehicles: Experiments...")
                        if len(item) == 1:
                            key, value = list(item.items())[0]
                            book_entry = f"{key}: {value}".strip()
                            print(f"Warning: Book entry in {metadata_path} parsed as dict: {item}. Converted to string: {book_entry}")
                        else:
                            book_entry = str(item).strip()
                            print(f"Warning: Invalid dict book format in {metadata_path}: {item}. Converting to string: {book_entry}")
                    else:
                        book_entry = str(item).strip()
                    if book_entry:
                        books_formatted.append(f"- {book_entry}")
                if books_formatted:
                    description_parts.append("*Books Mentioned*")
                    description_parts.append(books_formatted)
                    description_parts.append("")

                # Episode Links
                episode_links_parts = []
                if spotify_link:
                    episode_links_parts.append(f"- Spotify: {spotify_link}")
                if apple_link:
                    episode_links_parts.append(f"- Apple: {apple_link}")
                if x_link:
                    episode_links_parts.append(f"- X: {x_link}")
                episode_links_list = data.get("episode-links") or []
                for item in episode_links_list:
                    if isinstance(item, str) and item.strip():
                        episode_links_parts.append(f"- {item}")
                    elif isinstance(item, dict) and len(item) == 1:
                        key = list(item.keys())[0]
                        value = list(item.values())[0]
                        if isinstance(key, str) and isinstance(value, str):
                            formatted = f"- {key}: {value}"
                            episode_links_parts.append(formatted)
                        else:
                            print(f"Warning: Invalid dict episode-links format in {metadata_path}: {item}. Converting to string.")
                            episode_links_parts.append(f"- {str(item).strip()}")
                    else:
                        print(f"Warning: Invalid episode-links format in {metadata_path}: {item}. Converting to string.")
                        episode_links_parts.append(f"- {str(item).strip()}")

                if episode_links_parts:
                    description_parts.append("*Episode Links*")
                    description_parts.append(episode_links_parts)
                    description_parts.append("")

                # Global links
                if global_links_formatted:
                    description_parts.append("*Podcast Links*")
                    description_parts.append(global_links_formatted)
                    description_parts.append("")

                # Errata
                errata_list = data.get("errata") or []
                errata_formatted = [f"- {line}" for line in errata_list if line.strip()]
                if errata_formatted:
                    description_parts.append("*Errata*")
                    description_parts.append(errata_formatted)
                    description_parts.append("")

                # Combine description parts
                description = "\n".join(str(part) if not isinstance(part, list) else "\n".join(part) for part in description_parts).strip()

                # Validate description length
                if len(description) > max_description_length:
                    print(f"Description for video ID {video_id} in {episode_path} is too long ({len(description)} characters, max {max_description_length})")
                    sys.exit(1)

                # Convert to HTML for Spotify
                if generate_spotify:
                    description = convert_to_html_description(description_parts)

                # Add to pairs list
                pair = {
                    "title": extended_title,
                    "description": description
                }
                if not generate_spotify:
                    pair["video_id"] = video_id
                video_metadata_pairs.append(pair)

        except yaml.YAMLError as e:
            print(f"Error parsing {metadata_path}: {e}")
            # Print lines around the error for context
            lines = content.splitlines()
            error_line = getattr(e, 'problem_mark', None)
            if error_line:
                line_num = error_line.line
                start = max(0, line_num - 2)
                end = min(len(lines), line_num + 3)
                print(f"Context around line {line_num + 1}:")
                for i in range(start, end):
                    prefix = ">>" if i == line_num else "  "
                    print(f"{prefix} {i + 1}: {lines[i]}")
            sys.exit(1)
        except ValueError as e:
            print(f"Validation error in {metadata_path}: {e}")
            sys.exit(1)

    return video_metadata_pairs

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update YouTube video titles and descriptions or generate Spotify metadata")
    parser.add_argument("--update-youtube", action="store_true", help="Update titles and descriptions on YouTube")
    parser.add_argument("--generate-spotify", action="store_true", help="Generate titles and HTML descriptions for Spotify")
    parser.add_argument("--filename", type=str, help="Specify a single episode folder to process (e.g., '07_name')")
    parser.add_argument("--all", action="store_true", help="Process all episode folders (default unless --filename is specified)")
    args = parser.parse_args()

    # Validate argument combination
    if args.filename and args.all:
        print("Error: Cannot use --filename and --all together.")
        sys.exit(1)

    # Set filename to None if --all is specified or no filename is provided
    filename = args.filename if args.filename else None

    # Get list of video IDs, titles, and descriptions
    if args.generate_spotify:
        video_metadata_pairs = get_video_metadata_pairs(generate_spotify=True, filename=filename)
        platform = "Spotify"
    else:
        video_metadata_pairs = get_video_metadata_pairs(generate_spotify=False, filename=filename)
        platform = "YouTube"

    if not video_metadata_pairs:
        print(f"No valid {platform} metadata pairs found.")
        sys.exit(1)

    # Display video IDs, titles, and descriptions
    print(f"{platform} Metadata:")
    for pair in video_metadata_pairs:
        print(f"{'-' * 80}")
        if "video_id" in pair:
            print(f"Video ID: {pair['video_id']}")
        print(f"Title:\n[{pair['title']}]")
        print(f"Description:\n{pair['description']}")

    # Update metadata if --update-youtube is provided
    if args.update_youtube:
        if args.generate_spotify:
            print("Warning: --update-youtube will use YouTube-specific metadata, ignoring --generate-spotify for updates.")
            video_metadata_pairs = get_video_metadata_pairs(generate_spotify=False, filename=filename)
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
