import os
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

from app.config import settings


def ensure_storage_dir() -> None:
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile, prefix: str) -> Tuple[str, int]:
    ensure_storage_dir()
    safe_name = file.filename.replace("/", "_")
    file_path = os.path.join(settings.storage_dir, f"{prefix}_{safe_name}")
    size_bytes = 0

    with open(file_path, "wb") as handle:
        data = file.file.read()
        handle.write(data)
        size_bytes = len(data)

    return file_path, size_bytes
