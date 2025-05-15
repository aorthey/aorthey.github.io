from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from rembg import remove
import mediapipe as mp

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
percentage_of_face_to_crop = 0.15

def detect_face_landmarks(image_path: str) -> tuple:
    """Detect chin, hairline, and face edges using MediaPipe."""
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    height, width = image_np.shape[:2]
    results = face_mesh.process(image_np[:, :, ::-1])

    if not results.multi_face_landmarks:
        print("No face detected.")
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

def trim_left_space(image: Image.Image) -> Image.Image:
    """Trim transparent or near-white pixels from the left side."""
    image_np = np.array(image)
    height, width = image_np.shape[:2]
    alpha = image_np[:, :, 3]
    for x in range(width):
        if np.any(alpha[:, x] > 10) and not np.all(image_np[:, x, :3][alpha[:, x] > 10] > 240):
            return image.crop((x, 0, width, height))
    print("No non-transparent/non-white pixels found.")
    return image

def create_square_image(
    input_image_path: str,
    output_image_path: str,
    name1: str,
    number: str,
    name2: str,
    border_color: str,
    debug: bool = False
):
    """Generate a 720x720 image with text, borders, and a headshot, with full headshot aligned behind cropped headshot."""
    # Load and process headshot
    input_image = Image.open(input_image_path).convert("RGBA")
    output_array = remove(np.array(input_image))
    enhanced_array = enhance_headshot(output_array)
    headshot = Image.fromarray(enhanced_array.astype(np.uint8)).convert("RGBA")
    headshot = trim_left_space(headshot)

    # Create a copy of the full headshot
    full_headshot = headshot.copy()
    headshot_width, headshot_height = headshot.size

    # Crop headshot based on face landmarks for foreground
    landmarks = detect_face_landmarks(input_image_path)
    if landmarks is None:
        print("Using full headshot width for foreground.")
        crop_left = 0
    else:
        chin_x, chin_y, hairline_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y = landmarks
        face_width = right_face_x - left_face_x
        crop_left = max(0, left_face_x - int(face_width * percentage_of_face_to_crop))  # Include left ear
        crop_right = headshot_width  # Full width to avoid right cut
        crop_width = crop_right - crop_left
        if crop_width <= 0:
            print("Invalid crop width, using full width for foreground.")
            crop_right = headshot_width
            crop_width = headshot_width - crop_left
        headshot = headshot.crop((crop_left, 0, crop_right, headshot_height))

        # Debug: Save cropped headshot and print info
        if debug:
            headshot.save("debug_cropped_headshot.png", "PNG")
            print(f"Landmarks: Left cheek (x={left_face_x}, y={left_face_y}), Right cheek (x={right_face_x}, y={right_face_y})")
            print(f"Crop: Left={crop_left}, Right={crop_right}, Width={crop_width}")

    # Scale headshots
    headshot_width, headshot_height = headshot.size
    target_height = CANVAS_SIZE - 2 * HEADSHOT_PADDING
    if landmarks is None:
        aspect_ratio = headshot_width / headshot_height
        target_width = int(target_height * aspect_ratio)
    else:
        face_height_pixels = abs(chin_y - hairline_y)
        scale_factor = target_height / face_height_pixels if face_height_pixels > 0 else headshot_height
        target_width = int(headshot_width * scale_factor)
        target_height = int(headshot_height * scale_factor)
    headshot = headshot.resize((target_width, target_height), Image.LANCZOS)
    # Scale full headshot to match the same dimensions as the cropped headshot
    full_headshot = full_headshot.resize((int(full_headshot.size[0] * scale_factor), target_height), Image.LANCZOS)

    # Create canvas
    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Calculate alignment for full headshot to match cropped headshot
    text_widths = []
    try:
        font = ImageFont.truetype(FONT_PATH, TEXT_SIZE)
    except:
        font = ImageFont.load_default()
        print("Font not found, using default.")

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
    headshot_x = int(text_right)
    headshot_y = HEADSHOT_PADDING if landmarks is None else HEADSHOT_PADDING - int(hairline_y * (target_height / headshot_height))

    # Align full headshot to match cropped headshot
    full_headshot_x = headshot_x - int(crop_left * scale_factor)  # Adjust x to align with cropped portion
    full_headshot_y = headshot_y
    canvas.paste(full_headshot, (full_headshot_x, full_headshot_y), full_headshot)

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
        x_end = draw_text(draw, (X_START, Y_START), name1_first, font_name1_first, (0, 0, 0, 255), LETTER_SPACING)
        text_widths.append(x_end - X_START)
    if name1_last:
        x_end = draw_text(draw, (X_START, Y_START + line_gap), name1_last, font_name1_last, (0, 0, 0, 255), LETTER_SPACING)
        text_widths.append(x_end - X_START)
    x_end = draw_text(draw, (X_START, Y_START + 2 * line_gap), number_text, font, (128, 128, 128, 255), LETTER_SPACING)
    text_widths.append(x_end - X_START)
    if name2_first:
        x_end = draw_text(draw, (X_START, Y_START + 3 * line_gap), name2_first, font, (*border_rgb, 255), LETTER_SPACING)
        text_widths.append(x_end - X_START)
    if name2_last:
        x_end = draw_text(draw, (X_START, Y_START + 4 * line_gap), name2_last, font, (*border_rgb, 255), LETTER_SPACING)
        text_widths.append(x_end - X_START)

    # Place cropped headshot in foreground
    canvas.paste(headshot, (headshot_x, headshot_y), headshot)

    # Debug: Mark text boundary
    if debug:
        draw.rectangle([(text_right, 0), (text_right + 5, CANVAS_SIZE)], fill=(0, 255, 0, 255))
        print(f"Text right boundary: {text_right}")
        print(f"Full headshot x: {full_headshot_x}, Cropped headshot x: {headshot_x}")

    # Save output
    canvas.save(output_image_path, "PNG")

if __name__ == "__main__":
    create_square_image(
        input_image_path="assets/podcast/02_steven_lavalle/headshot.png",
        output_image_path="output_square.png",
        name1="Hans P. S. Random",
        number="12",
        name2="Andreas Orthey",
        border_color="#2e73ae",
        debug=False
    )
