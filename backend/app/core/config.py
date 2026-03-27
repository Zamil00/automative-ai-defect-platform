from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'ARRK AI Visual Defect Platform'
    environment: str = 'development'
    api_v1_prefix: str = '/api/v1'
    database_url: str = 'sqlite:///./arrk_ai.db'
    cors_origins: list[str] | str = ['http://localhost:5173']
    model_path: Path = Path('./data/models/defect_classifier.joblib')
    auto_init_db: bool = True

    @field_validator('cors_origins', mode='before')
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
