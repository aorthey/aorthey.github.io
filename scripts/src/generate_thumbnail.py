from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cv2
import numpy as np
from rembg import remove
import os
import colorsys
import mediapipe as mp
from scipy.ndimage import binary_dilation, binary_erosion

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_thumbnail_helpers import *

headshot_to_border_padding = 30  # Padding of headshot from top and bottom borders
headshot_edge_blur_radius = 2  # Slightly increased for smoother edge antialiasing
headshot_border_thickness = 50  # Increased for wider glow area
headshot_glow_blur_radius = 30  # Increased for wider glow area

def create_image_with_headshot(
    input_image_path: str,
    output_image_path: str,
    name1: str,
    number: str,
    name2: str,
    border_color: str,
    debug: bool = False
):
    canvas, text_right_boundary = generate_thumbnail_background(name1, number, name2, border_color)
    draw = ImageDraw.Draw(canvas)

    ################################################################################
    # Process Headshot and Paste It
    ################################################################################
    # Step 1: Load headshot and enhance quality
    input_image = Image.open(input_image_path).convert("RGBA")

    original_width, original_height = input_image.size

    # Apply denoising (gentle Gaussian blur) and sharpening
    # input_image = input_image.filter(ImageFilter.GaussianBlur(radius=0.5))  # Light denoising
    # input_image = ImageEnhance.Sharpness(input_image).enhance(1.5)  # Moderate sharpening

    # Step 2: Dynamic upscale for higher quality
    target_min_dimension = 1500  # Increased target for better quality
    if max(original_width, original_height) < target_min_dimension:
        upscale_factor = target_min_dimension / max(original_width, original_height)
        upscaled_size = (int(original_width * upscale_factor), int(original_height * upscale_factor))
        input_image = input_image.resize(upscaled_size, Image.LANCZOS)
    else:
        upscale_factor = 1  # No upscaling if already large enough

    # Step 3: Remove background from the enhanced (possibly upscaled) headshot
    # input_array = np.array(input_image)
    # output_array = remove(input_array)
    # headshot = Image.fromarray(output_array).convert("RGBA")
    input_array = np.array(input_image)
    headshot = Image.fromarray(input_array).convert("RGBA")

    # Step 4: Enhance alpha channel for antialiasing
    alpha = headshot.split()[3]
    alpha_array = np.array(alpha)
    # Threshold alpha channel to make it binary (fully opaque or fully transparent)
    alpha_binary = (alpha_array > 20).astype(np.uint8) * 255
    alpha_clean = Image.fromarray(alpha_binary)

    # Step 5: Apply cleaned alpha channel to headshot
    headshot_clean = Image.new("RGBA", headshot.size)
    headshot_clean.paste(headshot, (0, 0), alpha_clean)
    headshot = headshot_clean

    # Step 5.5: Create a white glow and apply antialiasing to headshot edges
    # Create an edge mask for antialiasing and glow
    alpha_np = np.array(alpha_clean)
    dilated_alpha = binary_dilation(alpha_np, structure=np.ones((headshot_border_thickness, headshot_border_thickness))).astype(np.uint8) * 255
    eroded_alpha = binary_erosion(alpha_np, structure=np.ones((headshot_border_thickness, headshot_border_thickness))).astype(np.uint8) * 255
    edge_mask = dilated_alpha - eroded_alpha

    # Apply Gaussian blur to the alpha channel for smooth antialiasing
    blurred_alpha = alpha_clean.filter(ImageFilter.GaussianBlur(radius=headshot_edge_blur_radius))
    blurred_alpha_np = np.array(blurred_alpha)
    final_alpha_np = np.where(edge_mask > 0, blurred_alpha_np, alpha_np)
    final_alpha = Image.fromarray(final_alpha_np)

    # Update headshot with antialiased edges
    headshot_clean = Image.new("RGBA", headshot.size)
    headshot_clean.paste(headshot, (0, 0), final_alpha)
    headshot = headshot_clean

    # Create a white glow layer with a smooth fade
    glow_alpha = Image.fromarray(edge_mask).filter(ImageFilter.GaussianBlur(radius=headshot_glow_blur_radius))
    glow_layer = Image.new("RGBA", headshot.size, (0, 0, 0, 0))  # Fully transparent base
    glow_layer.paste((255, 255, 255, 255), (0, 0), glow_alpha)  # White glow only where edge_mask is non-zero

    # Step 6: Detect chin and hairline (on original image, not enhanced, for accuracy)
    detection_result = detect_chin_and_hairline(input_image_path)
    if detection_result is None:
        print("Failed to detect chin and hairline. Skipping ellipsoid drawing and scaling.")
        chin_x, chin_y, hairline_x, hairline_y = 0, 0, 0, 0
        headshot_width, headshot_height = headshot.size
        target_height = canvas_height - 2 * headshot_to_border_padding
        aspect_ratio = headshot_width / headshot_height
        target_width = int(target_height * aspect_ratio)
    else:
        chin_x, chin_y, hairline_x, hairline_y = detection_result
        headshot_width, headshot_height = headshot.size
        face_height_pixels = abs(chin_y - hairline_y) * upscale_factor  # Adjust for upscaling
        if face_height_pixels == 0:
            print("Invalid face height detected. Using fallback scaling.")
            target_height = canvas_height - 2 * headshot_to_border_padding
            aspect_ratio = headshot_width / headshot_height
            target_width = int(target_height * aspect_ratio)
        else:
            target_face_height = canvas_height - 2 * headshot_to_border_padding
            scale_factor = target_face_height / face_height_pixels
            target_height = int(headshot_height * scale_factor)
            target_width = int(headshot_width * scale_factor)

    # Resize headshot and glow layer with antialiasing
    headshot = headshot.resize((target_width, target_height), Image.LANCZOS)
    glow_layer = glow_layer.resize((target_width, target_height), Image.LANCZOS)

    # Step 7: Calculate paste position
    if detection_result is not None:
        scale_x = target_width / headshot_width
        scale_y = target_height / headshot_height
        headshot_y = headshot_to_border_padding - int(hairline_y * scale_y * upscale_factor)  # Adjust for upscaling
    else:
        headshot_y = headshot_to_border_padding

    headshot_x = int(text_right_boundary + ((canvas_width - headshot_to_border_padding) - text_right_boundary - target_width) / 2)

    # Step 8: Paste glow layer and headshot onto canvas
    canvas.paste(glow_layer, (headshot_x, headshot_y), glow_layer)
    canvas.paste(headshot, (headshot_x, headshot_y), headshot)

    # Step 9: Draw debug ellipsoids if enabled
    if detection_result is not None and debug:
        draw_debug_ellipsoids(draw, detection_result, headshot_x, headshot_y, scale_x, scale_y, upscale_factor)

    # Step 10: Save the output
    combined_image = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
    combined_image.paste(canvas, (0, 0))
    combined_image.save(output_image_path, "PNG")

if __name__ == "__main__":
    create_image_with_headshot(
        input_image_path="assets/podcast/04_sean_murray/headshot.png",
        output_image_path="output.png",
        name1="Hans P. S. Random",
        number="123",
        name2="Andreas Orthey",
        border_color = "#6da3c5"
    )
