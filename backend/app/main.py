from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
app = FastAPI(title=settings.app_name, version='2.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

base_dir = Path(__file__).resolve().parents[1]
upload_dir = base_dir / 'data' / 'uploads'
overlay_dir = base_dir / 'data' / 'overlays'
mask_dir = base_dir / 'data' / 'masks'

for directory in (upload_dir, overlay_dir, mask_dir):
    directory.mkdir(parents=True, exist_ok=True)

app.mount('/files/uploads', StaticFiles(directory=upload_dir), name='uploads')
app.mount('/files/overlays', StaticFiles(directory=overlay_dir), name='overlays')
app.mount('/files/masks', StaticFiles(directory=mask_dir), name='masks')

if settings.auto_init_db:
    Base.metadata.create_all(bind=engine)

app.include_router(router, prefix=settings.api_v1_prefix)