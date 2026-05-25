import os
from PIL import Image
import math
import argparse
from src.generate_thumbnail import create_image_with_headshot
from src.generate_thumbnail_square import create_square_image

# Define the podcast directory and output for combined image
border_color = "#6da3c5"
podcast_dir = "assets/podcast"
podcast_host = "Andreas Orthey"
combined_output_path = "assets/podcast/combined_thumbnails.png"
combined_square_output_path = "assets/podcast/combined_thumbnails_squared.png"
thumbs_per_row = 3

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate podcast thumbnails.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--all', action='store_true', help='Generate thumbnails for all folders.')
group.add_argument('--filename', type=str, help='Generate thumbnail for the specified folder (e.g., 02_steven_lavalle).')
args = parser.parse_args()

# Determine which folders to process
folder_names = []
if args.all:
    folder_names = sorted([f for f in os.listdir(podcast_dir) if os.path.isdir(os.path.join(podcast_dir, f))])
elif args.filename:
    folder_path = os.path.join(podcast_dir, args.filename)
    if os.path.isdir(folder_path):
        folder_names = [args.filename]
    else:
        print(f"Folder '{args.filename}' not found in '{podcast_dir}'.")
        exit(1)

# List to store thumbnail paths
thumbnail_paths = []
thumbnail_square_paths = []

# Iterate through selected folders
for folder_name in folder_names:
    folder_path = os.path.join(podcast_dir, folder_name)
    # Check if it matches the naming pattern
    if folder_name[2] == '_':
        try:
            # Extract number and name from folder name (format: 01_surname_name)
            number, full_name = folder_name.split('_', 1)
            name_parts = full_name.replace('_', ' ').title()

            # print(full_name)
            print(name_parts)

            # exit(0)
            # Define input and output paths
            input_image_path = os.path.join(folder_path, "headshot.png")
            output_image_path = os.path.join(folder_path, "thumbnail.png")
            output_image_square_path = os.path.join(folder_path, "thumbnail_square.png")
            # Check if headshot.png exists
            if os.path.exists(input_image_path):
                # Generate thumbnail
                create_image_with_headshot(
                    input_image_path=input_image_path,
                    output_image_path=output_image_path,
                    name1=name_parts,
                    number=number,
                    name2=podcast_host,
                    border_color=border_color
                )
                print(f"Generated thumbnail for {folder_name}")
                create_square_image(
                    input_image_path=input_image_path,
                    output_image_path=output_image_square_path,
                    name1=name_parts,
                    number=number,
                    name2=podcast_host,
                    border_color=border_color
                )
                thumbnail_paths.append(output_image_path)
                thumbnail_square_paths.append(output_image_square_path)
            else:
                print(f"No headshot.png found in {folder_name}")
        except ValueError:
            print(f"Skipping folder {folder_name}: Invalid format")
            continue
    else:
        print(f"Skipping folder {folder_name}: Does not match naming pattern (e.g., 01_surname_name)")

# Add line_width parameter
line_width = 1  # Width of the white line between thumbnails

# Combine thumbnails into a single image (rectangular thumbnails)
if thumbnail_paths:
    # Open all thumbnail images
    images = [Image.open(path) for path in thumbnail_paths]
    # Assume all thumbnails are the same size
    thumb_width, thumb_height = images[0].size
    # Calculate grid dimensions (e.g., 3 thumbnails per row)
    num_rows = math.ceil(len(images) / thumbs_per_row)
    # Create a new blank image for the combined thumbnails, accounting for line_width
    combined_width = thumb_width * thumbs_per_row + line_width * (thumbs_per_row - 1)
    combined_height = thumb_height * num_rows + line_width * (num_rows - 1)
    combined_image = Image.new('RGB', (combined_width, combined_height), (255, 255, 255))
    # Paste thumbnails into the combined image with white lines
    for idx, img in enumerate(images):
        row = idx // thumbs_per_row
        col = idx % thumbs_per_row
        x = col * (thumb_width + line_width)
        y = row * (thumb_height + line_width)
        combined_image.paste(img, (x, y))
    # Save the combined image
    combined_image.save(combined_output_path)
    print(f"Combined thumbnails saved to {combined_output_path}")
else:
    print("No thumbnails were generated.")

# Combine square thumbnails into a single image
if thumbnail_square_paths:
    # Open all thumbnail images
    images = [Image.open(path) for path in thumbnail_square_paths]
    # Assume all thumbnails are the same size
    thumb_width, thumb_height = images[0].size
    # Calculate grid dimensions (e.g., 3 thumbnails per row)
    num_rows = math.ceil(len(images) / thumbs_per_row)
    # Create a new blank image for the combined thumbnails, accounting for line_width
    combined_width = thumb_width * thumbs_per_row + line_width * (thumbs_per_row - 1)
    combined_height = thumb_height * num_rows + line_width * (num_rows - 1)
    combined_image = Image.new('RGB', (combined_width, combined_height), (255, 255, 255))
    # Paste thumbnails into the combined image with white lines
    for idx, img in enumerate(images):
        row = idx // thumbs_per_row
        col = idx % thumbs_per_row
        x = col * (thumb_width + line_width)
        y = row * (thumb_height + line_width)
        combined_image.paste(img, (x, y))
    # Save the combined image
    combined_image.save(combined_square_output_path)
    print(f"Combined thumbnails saved to {combined_square_output_path}")
else:
    print("No thumbnails were generated.")
