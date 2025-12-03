# backend/app.py
from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Local utilities
from ai_utils import generate_images_from_inputs, generate_captions_for_images
from image_utils import overlay_caption_on_image, ensure_fonts_exist
from zip_utils import create_zip_from_folder

app = FastAPI(title="CreativeForge API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_COUNT = 10
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_DIR.mkdir(exist_ok=True, parents=True)


@app.get("/")
async def root():
    return {"status": "ok", "message": "CreativeForge Backend Running"}


@app.post("/generate")
async def generate(
    logo: UploadFile = File(...),
    product: UploadFile = File(...),
    brand_name: str = Form(""),
    tone: str = Form("premium"),
    preset: str = Form("B3"),
    count: int = Form(10)
):
    # Validate API keys
    if not os.getenv("FREEPIK_API_KEY"):
        raise HTTPException(500, "FREEPIK_API_KEY missing in backend/.env")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY missing in backend/.env")

    # Validate uploads
    if logo.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Logo must be JPG or PNG.")
    if product.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Product must be JPG or PNG.")

    count = min(10, max(1, count))

    # create temp dirs
    run_id = uuid.uuid4().hex[:10]
    base_tmp = Path(tempfile.gettempdir()) / f"creativeforge_{run_id}"
    input_dir = base_tmp / "input"
    output_dir = base_tmp / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # save files
    logo_path = input_dir / f"logo{Path(logo.filename).suffix}"
    product_path = input_dir / f"product{Path(product.filename).suffix}"

    with logo_path.open("wb") as f:
        f.write(await logo.read())
    with product_path.open("wb") as f:
        f.write(await product.read())

    ensure_fonts_exist(str(FONT_DIR))

    try:
        # generate images
        generated_images = generate_images_from_inputs(
            logo_path=str(logo_path),
            product_path=str(product_path),
            brand_name=brand_name,
            tone=tone,
            count=count,
            resolution="standard"
        )

        if not generated_images:
            raise HTTPException(500, "Image generation failed.")

        # captions
        captions = generate_captions_for_images(
            brand_name=brand_name,
            tone=tone,
            image_count=len(generated_images),
            language="english"
        )

        # apply captions
        for i, (img, caption) in enumerate(zip(generated_images, captions), start=1):
            out_file = output_dir / f"creative_{i:02d}.png"
            overlay_caption_on_image(
                image=img,
                caption=caption,
                out_path=str(out_file),
                preset=preset,
                brand_name=brand_name,
                fonts_dir=str(FONT_DIR)
            )

        # create ZIP
        zip_file = base_tmp / f"creative_pack_{run_id}.zip"
        create_zip_from_folder(str(output_dir), str(zip_file), filenames_sorted=True)

        # RETURN ZIP (do NOT delete temp yet!)
        return FileResponse(
            path=str(zip_file),
            media_type="application/zip",
            filename="creative_pack.zip",
            background=None  # important for Windows
        )

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(500, f"Internal Server Error: {str(e)}")

    # ❗ IMPORTANT: DO NOT DELETE FOLDER HERE.
    # Cleanup causes the ZIP to vanish before FastAPI serves it.
    # We leave the temp folder. OS will clear it eventually.
