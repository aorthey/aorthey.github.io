from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import numpy as np
from rembg import remove
import mediapipe as mp

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_thumbnail_helpers import *

# Configuration
BORDER_COLOR = "#007286"  # Teal
FONT_PATH = "../assets/fonts/cmunrm.ttf"
TEXT_SIZE = 128
LINE_SPACING = 1.0
LETTER_SPACING = 5.0  # Pixels
CANVAS_SIZE = 720  # 720x720 image
X_START = 5
Y_START = 20
REFERENCE_TEXT = "Andreas"  # For max text width
HEADSHOT_PADDING = 30  # Padding from top/bottom borders
TEXT_FACE_BUFFER = 30  # Buffer between text and face

def detect_face_landmarks(image_path: str) -> tuple:
    """Detect chin, hairline, and face edges using MediaPipe."""
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    height, width = image_np.shape[:2]
    results = face_mesh.process(image_np[:, :, ::-1])

    if not results.multi_face_landmarks:
        face_mesh.close()
        return None

    landmarks = results.multi_face_landmarks[0].landmark
    chin_x = int(landmarks[152].x * width)  # Chin (152)
    chin_y = int(landmarks[152].y * height)
    forehead_x = int(landmarks[10].x * width)  # Forehead (10)
    forehead_y = int(landmarks[10].y * height)
    face_height = chin_y - forehead_y
    hairline_y = max(0, forehead_y - int(face_height * 0.15))
    left_face_x = int(landmarks[234].x * width)  # Left cheek (234)
    left_face_y = int(landmarks[234].y * height)
    right_face_x = int(landmarks[454].x * width)  # Right cheek (454)
    right_face_y = int(landmarks[454].y * height)

    face_mesh.close()
    return (chin_x, chin_y, forehead_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y)

def trim_left_space(image: Image.Image) -> tuple:
    """Trim transparent or near-white pixels from the left side, return image and trim amount."""
    image_np = np.array(image)
    height, width = image_np.shape[:2]
    alpha = image_np[:, :, 3]
    trim_left = 0
    for x in range(width):
        if np.any(alpha[:, x] > 10) and not np.all(image_np[:, x, :3][alpha[:, x] > 10] > 240):
            trim_left = x
            break
    else:
        trim_left = 0
    return image.crop((trim_left, 0, width, height)), trim_left

def create_square_image(
    input_image_path: str,
    output_image_path: str,
    name1: str,
    number: str,
    name2: str,
    border_color: str
):
    """Generate a 720x720 image with text, borders, and a headshot."""
    # Load and process headshot
    input_image = Image.open(input_image_path).convert("RGBA")
    output_array = remove(np.array(input_image))
    enhanced_array = enhance_headshot(output_array)
    headshot = Image.fromarray(enhanced_array.astype(np.uint8)).convert("RGBA")
    headshot, trim_left = trim_left_space(headshot)

    # Get headshot dimensions
    headshot_width, headshot_height = headshot.size

    # Detect face landmarks
    landmarks = detect_face_landmarks(input_image_path)
    scale_factor = 1.0
    if landmarks is None:
        # No cropping, use full headshot
        target_height = CANVAS_SIZE - 2 * HEADSHOT_PADDING
        aspect_ratio = headshot_width / headshot_height
        target_width = int(target_height * aspect_ratio)
    else:
        chin_x, chin_y, hairline_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y = landmarks
        # Adjust left_face_x for trimming
        left_face_x -= trim_left
        # No left cropping, use full headshot width
        target_height = CANVAS_SIZE - 2 * HEADSHOT_PADDING
        face_height_pixels = abs(chin_y - hairline_y)
        scale_factor = target_height / face_height_pixels if face_height_pixels > 0 else headshot_height
        target_width = int(headshot_width * scale_factor)
        target_height = int(headshot_height * scale_factor)

    # Scale headshot
    headshot = headshot.resize((target_width, target_height), Image.LANCZOS)

    # Create canvas
    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Calculate text widths
    try:
        font = ImageFont.truetype(FONT_PATH, TEXT_SIZE)
    except:
        font = ImageFont.load_default()

    def get_text_width(text, font, spacing):
        width = 0
        for i, char in enumerate(text):
            char_width = font.getbbox(char)[2]
            width += char_width + (spacing if i < len(text) - 1 else 0)
        return width

    def adjust_font(text, font, max_width, spacing):
        font_size = TEXT_SIZE
        while get_text_width(text, font, spacing) > max_width and font_size > 10:
            font_size -= 2
            try:
                font = ImageFont.truetype(FONT_PATH, font_size)
            except:
                font = ImageFont.load_default()
        return font

    max_width = get_text_width(REFERENCE_TEXT, font, LETTER_SPACING)
    name1_parts = name1.strip().split()
    name1_first = name1_parts[0] if name1_parts else ""
    name1_last = name1_parts[-1] if len(name1_parts) > 1 else ""
    name2_parts = name2.strip().split()
    name2_first = name2_parts[0] if name2_parts else ""
    name2_last = name2_parts[-1] if len(name2_parts) > 1 else ""

    font_name1_first = adjust_font(name1_first, font, max_width, LETTER_SPACING) if name1_first else font
    font_name1_last = adjust_font(name1_last, font, max_width, LETTER_SPACING) if name1_last else font

    text_widths = []
    if name1_first:
        text_widths.append(get_text_width(name1_first, font_name1_first, LETTER_SPACING))
    if name1_last:
        text_widths.append(get_text_width(name1_last, font_name1_last, LETTER_SPACING))
    number_text = f"#{number}"
    text_widths.append(get_text_width(number_text, font, LETTER_SPACING))
    if name2_first:
        text_widths.append(get_text_width(name2_first, font, LETTER_SPACING))
    if name2_last:
        text_widths.append(get_text_width(name2_last, font, LETTER_SPACING))

    text_right = X_START + max(text_widths) if text_widths else X_START

    # Position headshot to avoid text overlap
    if landmarks is None:
        headshot_x = int(text_right + TEXT_FACE_BUFFER)
    else:
        face_left_scaled = left_face_x * scale_factor
        headshot_x = int(text_right + TEXT_FACE_BUFFER - face_left_scaled)

    headshot_y = HEADSHOT_PADDING if landmarks is None else HEADSHOT_PADDING - int(hairline_y * (target_height / headshot_height))

    # Draw top and bottom borders
    border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
    border_thickness = int(0.04 * CANVAS_SIZE)
    draw.line([(0, 0), (CANVAS_SIZE - 1, 0)], fill=border_rgb, width=border_thickness)
    draw.line([(0, CANVAS_SIZE - 1), (CANVAS_SIZE - 1, CANVAS_SIZE - 1)], fill=border_rgb, width=border_thickness)

    # Add text
    def draw_text(draw, pos, text, font, fill, spacing):
        x, y = pos
        for i, char in enumerate(text):
            draw.text((x, y), char, font=font, fill=fill)
            char_width = font.getbbox(char)[2]
            x += char_width + spacing
        return x

    line_gap = int(TEXT_SIZE * LINE_SPACING)
    if name1_first:
        draw_text(draw, (X_START, Y_START), name1_first, font_name1_first, (0, 0, 0, 255), LETTER_SPACING)
    if name1_last:
        draw_text(draw, (X_START, Y_START + line_gap), name1_last, font_name1_last, (0, 0, 0, 255), LETTER_SPACING)
    draw_text(draw, (X_START, Y_START + 2 * line_gap), number_text, font, (128, 128, 128, 255), LETTER_SPACING)
    if name2_first:
        draw_text(draw, (X_START, Y_START + 3 * line_gap), name2_first, font, (*border_rgb, 255), LETTER_SPACING)
    if name2_last:
        draw_text(draw, (X_START, Y_START + 4 * line_gap), name2_last, font, (*border_rgb, 255), LETTER_SPACING)

    # Place headshot
    canvas.paste(headshot, (headshot_x, headshot_y), headshot)

    # Save output
    canvas.save(output_image_path, "PNG")

if __name__ == "__main__":
    create_square_image(
        input_image_path="assets/podcast/07_oliver_brock/headshot.png",
        output_image_path="output_square.png",
        name1="Oliver P. S. Brock",
        number="12",
        name2="Andreas Orthey",
        border_color="#2e73ae"
    )
