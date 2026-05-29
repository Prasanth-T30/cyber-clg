"""
FusionGuardNet – Core Configuration
Loads settings from environment variables (with .env support via python-dotenv).
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ─────────────────────────────────────────────────────────────────
    APP_NAME: str = "FusionGuardNet"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Server ──────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── InstantDB ────────────────────────────────────────────────────────────
    INSTANTDB_APP_ID: str = "your-instantdb-app-id"
    INSTANTDB_ADMIN_TOKEN: str = "your-instantdb-admin-token"
    INSTANTDB_BASE_URL: str = "https://api.instantdb.com"

    # ── Security ────────────────────────────────────────────────────────────
    SECRET_KEY: str = "fusionguardnet-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── ML Settings ─────────────────────────────────────────────────────────
    MODEL_SAVE_DIR: str = "app/ml/saved_models"
    CNN_SEQUENCE_LENGTH: int = 100      # bytes per packet window
    LSTM_SEQUENCE_LENGTH: int = 10      # packets per sequence window
    DETECTION_THRESHOLD: float = 0.65  # confidence threshold for alerts

    # ── Packet Sniffer ───────────────────────────────────────────────────────
    SNIFFER_INTERFACE: str = "lo"       # loopback for dev; change to eth0/en0 in prod
    SNIFFER_SIMULATION_MODE: bool = True  # True = generate synthetic packets

    # ── Alert Settings ───────────────────────────────────────────────────────
    ALERT_HISTORY_LIMIT: int = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
