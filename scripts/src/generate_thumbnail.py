from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from rembg import remove
import os
import colorsys
import mediapipe as mp

#border_color = "#008080"  # Teal color
border_color = "#007286"
font_path = "../assets/fonts/cmunrm.ttf"
text_size = 128
line_spacing = 1.0
letter_spacing = 5.0  # In pixels
canvas_width = 1280
canvas_height = 720
x_start = 50
y_start = 20
headshot_to_border_padding = 30  # Padding of headshot from top and bottom borders
text_margin = 50  # Margin between text and headshot

def detect_chin_and_hairline(input_image_path: str) -> tuple:
    """
    Detect the position of the chin and hairline (or estimated hairline) in a headshot image.

    Args:
        input_image_path (str): Path to the input headshot image.

    Returns:
        tuple: (chin_x, chin_y, hairline_x, hairline_y) representing the coordinates of the chin
               and hairline (or estimated hairline). Returns None if detection fails.
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    )

    image = Image.open(input_image_path).convert("RGB")
    image_np = np.array(image)
    height, width, _ = image_np.shape
    image_rgb = image_np[:, :, ::-1]
    results = face_mesh.process(image_rgb)

    if not results.multi_face_landmarks:
        print("No face detected in the image.")
        face_mesh.close()
        return None

    face_landmarks = results.multi_face_landmarks[0]
    landmarks = face_landmarks.landmark

    chin_landmark = landmarks[152]
    chin_x = int(chin_landmark.x * width)
    chin_y = int(chin_landmark.y * height)

    forehead_landmark = landmarks[10]
    forehead_x = int(forehead_landmark.x * width)
    forehead_y = int(forehead_landmark.y * height)

    face_height = chin_y - forehead_y
    hairline_offset = int(face_height * 0.15)
    hairline_x = forehead_x
    hairline_y = forehead_y - hairline_offset
    hairline_y = max(0, hairline_y)

    face_mesh.close()
    return (chin_x, chin_y, hairline_x, hairline_y)

def create_image_with_headshot(
    input_image_path: str,
    output_image_path: str,
    name1: str,
    number: str,
    name2: str,
    debug: bool = False
):
    # Step 1: Load and remove background from the headshot
    input_image = Image.open(input_image_path).convert("RGBA")
    input_array = np.array(input_image)
    output_array = remove(input_array)
    headshot = Image.fromarray(output_array).convert("RGBA")

    # Step 2: Detect chin and hairline
    detection_result = detect_chin_and_hairline(input_image_path)
    if detection_result is None:
        print("Failed to detect chin and hairline. Skipping ellipsoid drawing and scaling.")
        chin_x, chin_y, hairline_x, hairline_y = 0, 0, 0, 0
        # Fallback: Use original resizing logic
        headshot_width, headshot_height = headshot.size
        target_height = canvas_height - 2 * headshot_to_border_padding
        aspect_ratio = headshot_width / headshot_height
        target_width = int(target_height * aspect_ratio)
    else:
        chin_x, chin_y, hairline_x, hairline_y = detection_result
        # Step 3: Scale headshot so chin-to-hairline distance matches
        # canvas_height - 2 * headshot_to_border_padding
        headshot_width, headshot_height = headshot.size
        face_height_pixels = abs(chin_y - hairline_y)  # Distance in original image
        if face_height_pixels == 0:
            print("Invalid face height detected. Using fallback scaling.")
            target_height = canvas_height - 2 * headshot_to_border_padding
            aspect_ratio = headshot_width / headshot_height
            target_width = int(target_height * aspect_ratio)
        else:
            # Calculate scaling factor so face height matches canvas height
            # minus headshot_to_border_padding
            target_face_height = canvas_height - 2 * headshot_to_border_padding
            scale_factor = target_face_height / face_height_pixels
            target_height = int(headshot_height * scale_factor)
            target_width = int(headshot_width * scale_factor)

    # Resize headshot
    headshot = headshot.resize((target_width, target_height), Image.LANCZOS)

    # Step 4: Create the canvas
    border_thickness = int(0.04 * canvas_height)
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Step 5: Draw the border
    border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
    draw.rectangle(
        [(0, 0), (canvas_width - 1, canvas_height - 1)],
        outline=border_rgb,
        width=border_thickness
    )

    # Step 6: Adjust border color for name2
    name2_color = (*border_rgb, 255)

    # Step 7: Add text and calculate text width
    try:
        font = ImageFont.truetype(font_path, text_size)
    except:
        font = ImageFont.load_default()
        print("Font not found. Using default font.")

    # Process names: Keep only first word and last word
    def get_first_last(name):
        words = name.strip().split()
        if not words:
            return "", ""
        first_name = words[0]
        last_name = words[-1] if len(words) > 1 else ""
        return first_name, last_name

    name1_first, name1_last = get_first_last(name1)
    name2_first, name2_last = get_first_last(name2)
    line_gap = int(text_size * line_spacing)

    def draw_text_with_spacing(draw, position, text, font, fill, letter_spacing):
        x, y = position
        for i, char in enumerate(text):
            draw.text((x, y), char, font=font, fill=fill)
            char_bbox = font.getbbox(char)
            char_width = char_bbox[2] - char_bbox[0]
            x += char_width + letter_spacing
        return x  # Return final x position for width calculation

    # Calculate text widths and draw text
    text_widths = []
    if name1_first:
        final_x = draw_text_with_spacing(draw, (x_start, y_start), name1_first, font, (0, 0, 0, 255), letter_spacing)
        text_widths.append(final_x - x_start)
    if name1_last:
        final_x = draw_text_with_spacing(draw, (x_start, y_start + 1 * line_gap), name1_last, font, (0, 0, 0, 255), letter_spacing)
        text_widths.append(final_x - x_start)
    number_text = f"#{number}"
    final_x = draw_text_with_spacing(draw, (x_start, y_start + 2 * line_gap), number_text, font, (128, 128, 128, 255), letter_spacing)
    text_widths.append(final_x - x_start)
    if name2_first:
        final_x = draw_text_with_spacing(draw, (x_start, y_start + 3 * line_gap), name2_first, font, name2_color, letter_spacing)
        text_widths.append(final_x - x_start)
    if name2_last:
        final_x = draw_text_with_spacing(draw, (x_start, y_start + 4 * line_gap), name2_last, font, name2_color, letter_spacing)
        text_widths.append(final_x - x_start)

    # Calculate maximum text width
    max_text_width = max(text_widths) if text_widths else 0
    text_right_boundary = x_start + max_text_width + text_margin

    # Step 8: Paste the headshot centered between text boundary and right border
    if detection_result is not None:
        # Calculate scaling factor used
        scale_x = target_width / headshot_width
        scale_y = target_height / headshot_height
        # Calculate where hairline should be (padding from top)
        headshot_y = headshot_to_border_padding - int(hairline_y * scale_y)  # Offset so hairline_y maps to padding
        # Center headshot horizontally
        available_width = (canvas_width - headshot_to_border_padding) - text_right_boundary
        headshot_x = int(text_right_boundary + (available_width - target_width) / 2)
    else:
        # Fallback positioning
        headshot_x = int(text_right_boundary + ((canvas_width - headshot_to_border_padding) - text_right_boundary - target_width) / 2)
        headshot_y = headshot_to_border_padding  # Center vertically within padded area

    canvas.paste(headshot, (headshot_x, headshot_y), headshot)

    # Step 9: Draw ellipsoids on the canvas at transformed coordinates
    if detection_result is not None and debug:
        # Transform chin and hairline coordinates to canvas
        canvas_chin_x = headshot_x + chin_x * scale_x
        canvas_chin_y = headshot_y + chin_y * scale_y
        canvas_hairline_x = headshot_x + hairline_x * scale_x
        canvas_hairline_y = headshot_y + hairline_y * scale_y

        # Draw red ellipsoid for chin
        draw.ellipse(
            [(canvas_chin_x - 5, canvas_chin_y - 5), (canvas_chin_x + 5, canvas_chin_y + 5)],
            fill=(255, 0, 0, 255)  # Red
        )

        # Draw blue ellipsoid for hairline
        draw.ellipse(
            [(canvas_hairline_x - 5, canvas_hairline_y - 5), (canvas_hairline_x + 5, canvas_hairline_y + 5)],
            fill=(0, 0, 255, 255)  # Blue
        )

    # Step 10: Save the output
    canvas.save(output_image_path, "PNG")

if __name__ == "__main__":
    create_image_with_headshot(
        input_image_path="/home/aorthey/Downloads/headshot.png",
        output_image_path="output.png",
        name1="Wolfgang M. LaValle",
        number="1",
        name2="Andreas Orthey",
    )
