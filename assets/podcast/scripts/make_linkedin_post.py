import os
import yaml
import argparse
import sys
import re

# Define constants
PODCAST_DIR = os.path.join(os.path.dirname(__file__), '..')  # Directory containing podcast episode folders
GLOBAL_LINKS_FILE = os.path.join(PODCAST_DIR, "podcast-links.yml")  # Global podcast links

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

def get_linkedin_posts(filename=None):
    """Iterate through podcast folders or a specific file to generate LinkedIn posts."""
    posts = []

    if not os.path.exists(PODCAST_DIR):
        print(f"Podcast directory {PODCAST_DIR} does not exist.")
        sys.exit(1)

    # Read global podcast-links.yml
    global_links = read_file_content(GLOBAL_LINKS_FILE)
    global_links_formatted = [f"- {line.strip()}" for line in global_links.splitlines() if line.strip()] if global_links else []

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
    for episode_folder in sorted(episode_folders):
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

                # Extract fields
                description = data.get("description")
                video_id = data.get("youtube")
                spotify_link = data.get("spotify")
                apple_link = data.get("apple")
                x_link = data.get("x")
                books_list = data.get("books") or []
                content_list = data.get("content") or []
                references_list = data.get("references") or []
                errata_list = data.get("errata") or []

                # Extract episode number from folder name
                match = re.match(r"^(\d+)_", episode_folder)
                if not match:
                    print(f"Warning: Could not extract episode number from folder {episode_folder}")
                    sys.exit(1)
                episode_number = match.group(1).lstrip("0") or "0"

                # Build description_parts
                description_parts = []

                if description:
                    description_parts.append(description)
                    description_parts.append("")

                # Combine main text
                main_text = "\n".join(
                    part if isinstance(part, str) else "\n".join(part) for part in description_parts
                ).strip()

                # Build links
                links = []
                if video_id:
                    links.append(f"YouTube: https://www.youtube.com/watch?v={video_id}")
                if spotify_link:
                    links.append(f"Spotify: {spotify_link}")
                if x_link:
                    links.append(f"X: {x_link}")
                if apple_link:
                    links.append(f"Apple: {apple_link}")
                links_text = "\n".join(links) if links else ""

                # Build references
                references_end = []
                for i, item in enumerate(references_list, 1):
                    if isinstance(item, str):
                        ref = item.strip()
                    elif isinstance(item, dict) and len(item) == 1:
                        key = list(item.keys())[0].strip()
                        value = list(item.values())[0].strip()
                        ref = f"{key}: {value}"
                    else:
                        ref = str(item).strip()
                    if ref:
                        references_end.append(f"[{i}] {ref}")
                references_text = "\n".join(references_end) if references_end else ""

                # Combine post
                post_sections = []
                if main_text:
                    post_sections.append(main_text)
                if links_text:
                    post_sections.append(links_text)
                if references_text:
                    post_sections.append(references_text)
                post = "\n\n".join(post_sections).strip()

                posts.append((episode_number, post))

        except yaml.YAMLError as e:
            print(f"Error parsing {metadata_path}: {e}")
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

    return posts

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate LinkedIn posts from podcast metadata")
    parser.add_argument("--filename", type=str, help="Specify a single episode folder to process (e.g., '07_name')")
    args = parser.parse_args()

    filename = args.filename

    # Get posts
    posts = get_linkedin_posts(filename=filename)

    if not posts:
        print("No valid metadata found.")
        sys.exit(1)

    # Display posts
    for episode_number, post in posts:
        print(f"LinkedIn Post for Episode {episode_number}:")
        print(post)
        print("-" * 80)

if __name__ == "__main__":
    main()

