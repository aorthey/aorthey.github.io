from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
from rembg import remove
import os
import colorsys
import mediapipe as mp

font_path = "../assets/fonts/cmunrm.ttf"
text_size = 128
line_spacing = 1.0
letter_spacing = 5.0  # In pixels
canvas_width = 1280
canvas_height = 720
x_start = 50
y_start = 20
text_margin = 50  # Margin between text and headshot
headshot_to_border_padding = 30  # Padding of headshot from top and bottom borders

def generate_thumbnail_background(
    name1: str,
    number: str,
    name2: str,
    border_color: str):
    # Step 1: Create the canvas
    border_thickness = int(0.04 * canvas_height)
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Step 2: Draw the border
    border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
    draw.rectangle(
        [(0, 0), (canvas_width - 1, canvas_height - 1)],
        outline=border_rgb,
        width=border_thickness
    )

    # Calculate text widths to determine headshot position
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

    # Define name2 color before text width calculation
    name2_color = (*border_rgb, 255)

    def draw_text_with_spacing(draw, position, text, font, fill, letter_spacing):
        x, y = position
        for i, char in enumerate(text):
            draw.text((x, y), char, font=font, fill=fill)
            char_bbox = font.getbbox(char)
            char_width = char_bbox[2] - char_bbox[0]
            x += char_width + letter_spacing
        return x  # Return final x position for width calculation

    # Calculate text widths
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

    return (canvas, text_right_boundary)

def detect_chin_and_hairline(input_image_path: str) -> tuple:
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

def enhance_headshot(image: np.ndarray) -> np.ndarray:
    """Enhance headshot quality with filters and contrast adjustment."""
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    bgr = cv2.bilateralFilter(bgr, d=5, sigmaColor=75, sigmaSpace=75)
    gaussian = cv2.GaussianBlur(bgr, (0, 0), sigmaX=2.0)
    sharpened = cv2.addWeighted(bgr, 1.5, gaussian, -0.5, 0)
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    enhanced_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    alpha_smoothed = cv2.GaussianBlur(alpha, (5, 5), 0)
    return np.dstack((enhanced_rgb, alpha_smoothed))

def draw_debug_ellipsoids(
    draw: ImageDraw.Draw,
    detection_result: tuple,
    headshot_x: int,
    headshot_y: int,
    scale_x: float,
    scale_y: float,
    upscale_factor: float
):
    """Draw debug ellipsoids for chin and hairline on the canvas."""
    chin_x, chin_y, hairline_x, hairline_y = detection_result
    canvas_chin_x = headshot_x + (chin_x * scale_x * upscale_factor)
    canvas_chin_y = headshot_y + (chin_y * scale_y * upscale_factor)
    canvas_hairline_x = headshot_x + (hairline_x * scale_x * upscale_factor)
    canvas_hairline_y = headshot_y + (hairline_y * scale_y * upscale_factor)

    draw.ellipse(
        [(canvas_chin_x - 5, canvas_chin_y - 5), (canvas_chin_x + 5, canvas_chin_y + 5)],
        fill=(255, 0, 0, 255)
    )
    draw.ellipse(
        [(canvas_hairline_x - 5, canvas_hairline_y - 5), (canvas_hairline_x + 5, canvas_hairline_y + 5)],
        fill=(0, 0, 255, 255)
    )

