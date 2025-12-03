import os
import io
import time
import json
import base64
from typing import List
import PIL
from PIL import Image,ImageDraw
import requests
from openai import OpenAI

# Load env vars
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")

# Create OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("⚠ WARNING: OPENAI_API_KEY not found. Captions will fallback.")

# size settings
SIZE_MAP = {"standard": (1024, 1024), "hd": (2048, 2048)}

FREEPIK_IMAGE_ENDPOINT = "https://api.freepik.com/v1/ai/text-to-image"

# ------------------------------
# UTILS
# ------------------------------
def _b64_to_pil(b64_str: str) -> Image.Image:
    if b64_str.startswith("data:"):
        b64_str = b64_str.split(",", 1)[1]
    raw = base64.b64decode(b64_str)
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def _url_to_pil(url: str) -> Image.Image:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")


# ------------------------------
# FREEPIK IMAGE GENERATION
# ------------------------------
def _call_freepik(prompt: str, size: str = "standard") -> Image.Image:
    if not FREEPIK_API_KEY:
        raise RuntimeError("FREEPIK_API_KEY not found in .env")

    payload = {
        "prompt": prompt,
        "width": SIZE_MAP.get(size, SIZE_MAP["standard"])[0],
        "height": SIZE_MAP.get(size, SIZE_MAP["standard"])[1],
    }

    headers = {
        "X-Freepik-API-Key": FREEPIK_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    r = requests.post(FREEPIK_IMAGE_ENDPOINT, json=payload, headers=headers, timeout=60)

    try:
        data = r.json()
    except:
        raise RuntimeError(f"Freepik returned non-JSON: {r.text[:200]}")

    # Possible structures:
    if "data" in data and isinstance(data["data"], list):
        item = data["data"][0]
        if "b64" in item:
            return _b64_to_pil(item["b64"])
        if "url" in item:
            return _url_to_pil(item["url"])

    if "image_base64" in data:
        return _b64_to_pil(data["image_base64"])

    raise RuntimeError(f"Unrecognized Freepik structure: {data}")


# ------------------------------
# FALLBACK IMAGE (when Freepik fails)
# ------------------------------
def _fallback_background(resolution="standard"):
    w, h = SIZE_MAP.get(resolution, SIZE_MAP["standard"])
    img = Image.new("RGBA", (w, h), (225, 225, 225, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, h], fill=(235, 235, 235))
    return img


# ------------------------------
# MAIN IMAGE GENERATOR
# ------------------------------
def generate_images_from_inputs(logo_path, product_path, brand_name, tone, count, resolution="standard"):
    count = min(10, max(1, count))

    product = Image.open(product_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    results = []

    for i in range(count):
        prompt = (
            f"Create a premium advertising background for {brand_name or 'a brand'}. "
            f"Tone: {tone}. Do not add text."
        )

        # Try Freepik
        try:
            bg = _call_freepik(prompt, resolution)
        except Exception as e:
            print("Freepik failed → using fallback. Reason:", e)
            bg = _fallback_background(resolution)

        # Composite
        bg_w, bg_h = bg.size
        short = min(bg_w, bg_h)
        product_w = int(short * 0.45)
        prod_w, prod_h = product.size
        new_h = int((prod_h / prod_w) * product_w)
        prod_resized = product.resize((product_w, new_h), Image.LANCZOS)

        # center
        px = int((bg_w - product_w) / 2)
        py = int((bg_h - new_h) / 2)

        composite = bg.copy()
        composite.paste(prod_resized, (px, py), prod_resized)

        # logo
        lw = int(short * 0.12)
        lg_w, lg_h = logo.size
        new_logo_h = int((lg_h / lg_w) * lw)
        logo_resized = logo.resize((lw, new_logo_h), Image.LANCZOS)

        composite.paste(logo_resized, (bg_w - lw - 40, 40), logo_resized)

        results.append(composite.convert("RGBA"))

    return results


# ------------------------------
# CAPTION GENERATION (NEW OpenAI API)
# ------------------------------
def generate_captions_for_images(brand_name, tone, image_count, language="english"):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    captions = []

    for i in range(image_count):

        prompt = f"""
        Create a premium, minimal, 4–7 word advertising caption.
        Brand: {brand_name}
        Tone: {tone}
        Language: {language}
        No emojis. No hashtags. No special characters.
        """

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=20,
            )

            text = resp.choices[0].message.content.strip()
            captions.append(text)

        except Exception as e:
            print("OpenAI failed → using fallback:", e)
            captions.append(f"Discover {brand_name} today.")

    return captions
