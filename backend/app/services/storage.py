from __future__ import annotations

import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
OVERLAY_DIR = BASE_DIR / 'data' / 'overlays'
MASK_DIR = BASE_DIR / 'data' / 'masks'
MODEL_DIR = BASE_DIR / 'data' / 'models'

for folder in (UPLOAD_DIR, OVERLAY_DIR, MASK_DIR, MODEL_DIR):
    folder.mkdir(parents=True, exist_ok=True)


class StorageService:
    def save_upload(self, filename: str, content: bytes) -> tuple[str, Path]:
        safe_name = filename.replace(' ', '_')
        inspection_id = uuid.uuid4().hex[:12]
        destination = UPLOAD_DIR / f'{inspection_id}_{safe_name}'
        destination.write_bytes(content)
        return inspection_id, destination

    def overlay_path(self, inspection_id: str) -> Path:
        return OVERLAY_DIR / f'{inspection_id}_overlay.png'

    def mask_path(self, inspection_id: str) -> Path:
        return MASK_DIR / f'{inspection_id}_mask.png'