from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from rembg import remove
import os
import colorsys
import mediapipe as mp

border_color = "#007286"  # Teal color
font_path = "../assets/fonts/cmunrm.ttf"
text_size = 128
line_spacing = 1.0
letter_spacing = 5.0  # In pixels
square_canvas_size = 720  # For the new 720x720 image
percentage_of_face_cropped = 0.18
x_start = 5
y_start = 20
reference_max_text_length = "Andreas"
headshot_to_border_padding = 30  # Padding of headshot from top and bottom borders
text_padding = -10  # New parameter: padding between text and headshot (replaces text_margin)

def detect_chin_and_hairline(input_image_path: str) -> tuple:
    """
    Detect the position of the chin, hairline, and left/right edges of the face in a headshot image.
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

    # Chin (landmark 152)
    chin_landmark = landmarks[152]
    chin_x = int(chin_landmark.x * width)
    chin_y = int(chin_landmark.y * height)

    # Forehead (landmark 10) for hairline estimation
    forehead_landmark = landmarks[10]
    forehead_x = int(forehead_landmark.x * width)
    forehead_y = int(forehead_landmark.y * height)

    face_height = chin_y - forehead_y
    hairline_offset = int(face_height * 0.15)
    hairline_x = forehead_x
    hairline_y = forehead_y - hairline_offset
    hairline_y = max(0, hairline_y)

    # Left edge of face (landmark 234, left cheek for more reliable outer edge)
    left_face_landmark = landmarks[234]
    left_face_x = int(left_face_landmark.x * width)
    left_face_y = int(left_face_landmark.y * height)

    # Right side of face (landmark 454, right cheek) for face width
    right_face_landmark = landmarks[454]
    right_face_x = int(right_face_landmark.x * width)
    right_face_y = int(right_face_landmark.y * height)

    face_mesh.close()
    return (chin_x, chin_y, hairline_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y)

def enhance_headshot(image: np.ndarray) -> np.ndarray:
    """
    Enhance the quality of the headshot image.
    """
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]
    rgb_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    rgb_bgr = cv2.bilateralFilter(rgb_bgr, d=5, sigmaColor=75, sigmaSpace=75)
    gaussian = cv2.GaussianBlur(rgb_bgr, (0, 0), sigmaX=2.0)
    sharpened = cv2.addWeighted(rgb_bgr, 1.5, gaussian, -0.5, 0)
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    enhanced_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    alpha_smoothed = cv2.GaussianBlur(alpha, (5, 5), 0)
    enhanced_rgba = np.dstack((enhanced_rgb, alpha_smoothed))
    return enhanced_rgba

def trim_left_space(image: Image.Image) -> Image.Image:
    """
    Trim transparent or near-white pixels from the left side of the image.
    """
    image_np = np.array(image)
    height, width, _ = image_np.shape
    alpha = image_np[:, :, 3]  # Alpha channel

    # Find the leftmost non-transparent/non-white pixel
    for x in range(width):
        column = image_np[:, x]
        if np.any(alpha[:, x] > 10):  # Threshold for transparency
            rgb = column[:, :3]
            if not np.all(rgb[alpha[:, x] > 10] > 240):  # Not all near-white
                return image.crop((x, 0, width, height))
    print("No non-transparent/non-white pixels found, returning original image.")
    return image

def create_square_image_with_half_headshot(
    input_image_path: str,
    output_image_path: str,
    name1: str,
    number: str,
    name2: str,
    debug: bool = False
):
    """
    Generate a 720x720 image with text, top/bottom borders, and a half-face headshot.
    """
    # Step 1: Load and remove background from the headshot
    input_image = Image.open(input_image_path).convert("RGBA")
    input_array = np.array(input_image)
    output_array = remove(input_array)
    enhanced_array = enhance_headshot(output_array)
    headshot = Image.fromarray(enhanced_array.astype(np.uint8)).convert("RGBA")

    # Trim left transparent/white space
    headshot = trim_left_space(headshot)

    # Step 1.5: Crop to show left half of the face based on face landmarks
    headshot_width, headshot_height = headshot.size
    detection_result = detect_chin_and_hairline(input_image_path)
    crop_left = 0  # Initialize for debug visualization
    if detection_result is None:
        print("Using default cropping due to failed detection.")
        crop_width = headshot_width // 2
        headshot = headshot.crop((0, 0, crop_width, headshot_height))
    else:
        chin_x, chin_y, hairline_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y = detection_result
        # Calculate face midline with slight extension
        faces = [
            {
                "text": "The quick brown fox jumps over the lazy dog",
                "color": "red"
            },
            {
                "text": "Lorem ipsum dolor sit amet",
                "color": "blue"
            }
        ]
        face_width = right_face_x - left_face_x
        face_midline = (left_face_x + right_face_x) // 2
        # Crop from slightly left of left cheek to slightly past midline
        crop_left = max(0, left_face_x - int(face_width * percentage_of_face_cropped))
        crop_right = min(headshot_width, face_midline + int(face_width * 0.1))  # Extend slightly past midline
        crop_width = crop_right - crop_left
        if crop_width <= 0:
            print("Invalid crop width, using default cropping.")
            crop_width = headshot_width // 2
            headshot = headshot.crop((0, 0, crop_width, headshot_height))
        else:
            headshot = headshot.crop((crop_left, 0, crop_right, headshot_height))

    # Save intermediate cropped headshot for inspection
    if debug:
        headshot.save("debug_cropped_headshot.png", "PNG")

    # Step 2: Detect chin and hairline and scale headshot
    headshot_width, headshot_height = headshot.size
    if detection_result is None:
        print("Failed to detect chin and hairline. Skipping ellipsoid drawing and scaling.")
        chin_x, chin_y, hairline_x, hairline_y = 0, 0, 0, 0
        target_height = square_canvas_size - 2 * headshot_to_border_padding
        aspect_ratio = headshot_width / headshot_height
        target_width = int(target_height * aspect_ratio)
    else:
        chin_x, chin_y, hairline_x, hairline_y, left_face_x, left_face_y, right_face_x, right_face_y = detection_result
        face_height_pixels = abs(chin_y - hairline_y)
        if face_height_pixels == 0:
            target_height = square_canvas_size - 2 * headshot_to_border_padding
            aspect_ratio = headshot_width / headshot_height
            target_width = int(target_height * aspect_ratio)
        else:
            target_face_height = square_canvas_size - 2 * headshot_to_border_padding
            scale_factor = target_face_height / face_height_pixels
            target_height = int(headshot_height * scale_factor)
            target_width = int(headshot_width * scale_factor)

    # Resize headshot
    headshot = headshot.resize((target_width, target_height), Image.LANCZOS)

    # Step 3: Create the canvas
    border_thickness = int(0.04 * square_canvas_size)
    canvas = Image.new("RGBA", (square_canvas_size, square_canvas_size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Step 4: Draw top and bottom borders only
    border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
    draw.line(
        [(0, 0), (square_canvas_size - 1, 0)],
        fill=border_rgb,
        width=border_thickness
    )
    draw.line(
        [(0, square_canvas_size - 1), (square_canvas_size - 1, square_canvas_size - 1)],
        fill=border_rgb,
        width=border_thickness
    )

    # Step 5: Adjust border color for name2
    name2_color = (*border_rgb, 255)

    # Step 6: Add text and calculate text width
    try:
        font = ImageFont.truetype(font_path, text_size)
    except:
        font = ImageFont.load_default()
        print("Font not found. Using default font.")

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
        return x

    # Calculate maximum width based on "Andreas"
    max_width = 0
    for i, char in enumerate(reference_max_text_length):
        char_bbox = font.getbbox(char)
        char_width = char_bbox[2] - char_bbox[0]
        max_width += char_width + (letter_spacing if i < len(reference_max_text_length) - 1 else 0)

    # Adjust font size for name1_first and name1_last if necessary
    def get_text_width(text, font, letter_spacing):
        width = 0
        for i, char in enumerate(text):
            char_bbox = font.getbbox(char)
            char_width = char_bbox[2] - char_bbox[0]
            width += char_width + (letter_spacing if i < len(text) - 1 else 0)
        return width

    def get_adjusted_font(text, initial_font, max_width, letter_spacing):
        font_size = text_size
        font = initial_font
        text_width = get_text_width(text, font, letter_spacing)
        while text_width > max_width and font_size > 10:  # Minimum font size
            font_size -= 2
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            text_width = get_text_width(text, font, letter_spacing)
        return font, font_size

    # Adjust font for name1_first
    font_name1_first = font
    font_size_name1_first = text_size
    if name1_first:
        text_width = get_text_width(name1_first, font, letter_spacing)
        if text_width > max_width:
            font_name1_first, font_size_name1_first = get_adjusted_font(name1_first, font, max_width, letter_spacing)

    # Adjust font for name1_last
    font_name1_last = font
    font_size_name1_last = text_size
    if name1_last:
        text_width = get_text_width(name1_last, font, letter_spacing)
        if text_width > max_width:
            font_name1_last, font_size_name1_last = get_adjusted_font(name1_last, font, max_width, letter_spacing)

    # Draw text and calculate widths
    text_widths = []
    if name1_first:
        final_x = draw_text_with_spacing(draw, (x_start, y_start), name1_first, font_name1_first, (0, 0, 0, 255), letter_spacing)
        text_widths.append(final_x - x_start)
    if name1_last:
        final_x = draw_text_with_spacing(draw, (x_start, y_start + 1 * line_gap), name1_last, font_name1_last, (0, 0, 0, 255), letter_spacing)
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

    max_text_width = max(text_widths) if text_widths else 0
    text_right_boundary = x_start + max_text_width + text_padding  # Use text_padding instead of text_margin

    # Step 7: Paste the headshot immediately to the right of the text
    if detection_result is not None:
        scale_x = target_width / headshot_width
        scale_y = target_height / headshot_height
        headshot_x = int(text_right_boundary)  # Place headshot directly at text boundary
        headshot_y = headshot_to_border_padding - int(hairline_y * scale_y)
    else:
        headshot_x = int(text_right_boundary)  # Place headshot directly at text boundary
        headshot_y = int(headshot_to_border_padding)

    canvas.paste(headshot, (headshot_x, headshot_y), headshot)

    if debug:
        draw.rectangle(
            [(text_right_boundary, 0), (text_right_boundary + 5, square_canvas_size)],
            fill=(0, 255, 0, 255)
        )

    # Step 8: Draw ellipsoids and debug lines for headshot boundaries
    if detection_result is not None and debug:
        canvas_chin_x = headshot_x + (chin_x - crop_left) * scale_x
        canvas_chin_y = headshot_y + chin_y * scale_y
        canvas_hairline_x = headshot_x + (hairline_x - crop_left) * scale_x
        canvas_hairline_y = headshot_y + hairline_y * scale_y
        canvas_left_face_x = headshot_x + (left_face_x - crop_left) * scale_x
        canvas_left_face_y = headshot_y + left_face_y * scale_y
        draw.ellipse(
            [(canvas_chin_x - 5, canvas_chin_y - 5), (canvas_chin_x + 5, canvas_chin_y + 5)],
            fill=(255, 0, 0, 255)  # Red for chin
        )
        draw.ellipse(
            [(canvas_hairline_x - 5, canvas_hairline_y - 5), (canvas_hairline_x + 5, canvas_hairline_y + 5)],
            fill=(0, 0, 255, 255)  # Blue for hairline
        )
        draw.ellipse(
            [(canvas_left_face_x - 5, canvas_left_face_y - 5), (canvas_left_face_x + 5, canvas_left_face_y + 5)],
            fill=(0, 255, 0, 255)  # Green for left face (cheek)
        )
        draw.line(
            [(headshot_x, 0), (headshot_x, square_canvas_size)],
            fill=(255, 255, 0, 255),  # Yellow for left edge
            width=2
        )
        draw.line(
            [(headshot_x + target_width, 0), (headshot_x + target_width, square_canvas_size)],
            fill=(255, 0, 255, 255),  # Magenta for right edge
            width=2
        )
        # Print debug info
        print(f"Crop left: {crop_left}, Crop right: {crop_right}, Left face x: {left_face_x}, Right face x: {right_face_x}")

    # Step 9: Save the output
    canvas.save(output_image_path, "PNG")

if __name__ == "__main__":
    # Example usage
    create_square_image_with_half_headshot(
        input_image_path="/home/aorthey/Downloads/headshot.png",
        output_image_path="output_square.png",
        name1="Wolfgang M. Srinivasa",
        number="1",
        name2="Andreas Orthey",
        debug=True
    )

