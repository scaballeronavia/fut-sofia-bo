from __future__ import annotations
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Sof-IA BO"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    demo_mode: bool = True
    model_version: str = "demo-audit-calibrado-0.4.0"
    default_simulations: int = 50_000
    default_seed: int = 26062026
    data_cutoff: str = "2026-06-26T00:00:00-04:00"


class HealthStatus(BaseModel):
    status: str
    app: str
    environment: str
    demo_mode: bool
    model_version: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
