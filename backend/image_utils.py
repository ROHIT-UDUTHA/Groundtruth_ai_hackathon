# backend/image_utils.py
from PIL import Image, ImageDraw, ImageFont
import os
from colorthief import ColorThief
import random


def ensure_fonts_exist(fonts_dir: str):
    """
    Ensures that the required TTF/OTF fonts exist.
    You already have Inter-SemiBold-Italic-600.otf.
    """
    if not os.path.exists(fonts_dir):
        raise RuntimeError(f"Fonts directory not found: {fonts_dir}")

    required = ["Inter-SemiBold-Italic-600.otf"]
    for f in required:
        path = os.path.join(fonts_dir, f)
        if not os.path.isfile(path):
            raise RuntimeError(f"Required font missing: {path}")


def pick_caption_color(image: Image.Image) -> str:
    """
    Extract a dominant color from the background using ColorThief,
    then invert or adjust brightness for visibility.
    """
    try:
        # Save temporarily for ColorThief
        temp = "_temp_color.jpg"
        image.convert("RGB").save(temp)
        ct = ColorThief(temp)
        dominant = ct.get_color(quality=3)
        os.remove(temp)

        r, g, b = dominant
        brightness = (r * 299 + g * 587 + b * 114) / 1000

        if brightness > 130:
            return "#0f0f0f"  # dark text for bright backgrounds
        else:
            return "#ffffff"  # white text for dark backgrounds

    except Exception:
        return "#ffffff"  # safe fallback


def choose_caption_position(img_w: int, img_h: int):
    """
    Select a dynamic caption position based on image size.
    Random but aesthetic.
    """
    choices = [
        (int(img_w * 0.08), int(img_h * 0.80)),  # bottom-left
        (int(img_w * 0.55), int(img_h * 0.80)),  # bottom-right
        (int(img_w * 0.08), int(img_h * 0.10)),  # top-left
        (int(img_w * 0.55), int(img_h * 0.10)),  # top-right
        (int(img_w * 0.20), int(img_h * 0.45)),  # center-left
        (int(img_w * 0.20), int(img_h * 0.65)),  # mid-bottom
    ]
    return random.choice(choices)


def overlay_caption_on_image(
    image: Image.Image,
    caption: str,
    out_path: str,
    preset: str,
    brand_name: str,
    fonts_dir: str
):
    """
    Draw a caption over the image using aesthetic presets.
    """
    img = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    img_w, img_h = img.size
    color = pick_caption_color(img)

    # Choose dynamic position
    x, y = choose_caption_position(img_w, img_h)

    # Font selection
    font_path = os.path.join(fonts_dir, "Inter-SemiBold-Italic-600.otf")
    base_size = int(img_h * 0.035)
    font = ImageFont.truetype(font_path, base_size)

    # Shadow effect (clean aesthetic)
    shadow_color = (0, 0, 0, 120)
    for ox, oy in [(1,1),(-1,-1),(1,-1),(-1,1), (2,2)]:
        draw.text((x+ox, y+oy), caption, font=font, fill=shadow_color)

    # Actual caption
    draw.text((x, y), caption, font=font, fill=color)

    img.save(out_path, "PNG")
    return out_path
