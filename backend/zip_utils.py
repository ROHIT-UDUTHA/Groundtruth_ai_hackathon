# backend/zip_utils.py
"""
Simple ZIP utilities for CreativeForge.

Provides:
- create_zip_from_folder(folder_path, zip_path, filenames_sorted=True)

This zips only image files (PNG/JPG/JPEG) found in `folder_path` into `zip_path`.
By default files are sorted alphabetically so creative_01.png ... creative_10.png
appear in order inside the archive.
"""
import os
import zipfile
from pathlib import Path
from typing import Iterable


def _iter_image_files(folder_path: str) -> Iterable[Path]:
    """Yield Path objects for PNG/JPG/JPEG files in the folder (non-recursive)."""
    p = Path(folder_path)
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"):
        for f in p.glob(ext):
            yield f


def create_zip_from_folder(folder_path: str, zip_path: str, filenames_sorted: bool = True) -> str:
    """
    Create a zip archive at `zip_path` containing all image files in `folder_path`.
    Returns the path to the created zip file (as string).

    Parameters:
    - folder_path: directory containing final creatives
    - zip_path: desired full path (including filename) for the zip file
    - filenames_sorted: whether to sort filenames alphabetically before zipping
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    # Collect image files
    files = list(_iter_image_files(folder_path))
    if filenames_sorted:
        files = sorted(files, key=lambda p: p.name)

    # Ensure the zip parent dir exists
    zip_parent = Path(zip_path).parent
    zip_parent.mkdir(parents=True, exist_ok=True)

    # Create zip
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            # Archive name should be only the filename (no full paths)
            zf.write(f, arcname=f.name)

    return str(zip_path)
