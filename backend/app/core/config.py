import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "JEV Decision Model API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Model configuration
    MODEL_ID: str = "LiquidAI/d1-omni-600M"
    MODEL_DEVICE: str = "auto"  # auto, mps, cuda, cpu
    MODEL_CACHE_DIR: str = str(BASE_DIR / ".cache" / "models")

    # When True, switching between models keeps previously loaded weights resident
    # ("simple cache"); when False, only the active model is kept in memory.
    MODEL_CACHE_ENABLED: bool = False
    
    # EdgeJev (pip package `edgejev`) runtime configuration.
    # The ONNX/INT8 model directory is produced by `edgejev build`.
    EDGEJEV_MODEL_DIR: str = str(BASE_DIR / ".cache" / "edgejev")
    EDGEJEV_BACKEND: str = "laya"
    EDGEJEV_AUTO_BUILD: bool = True
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/jev_decision.db"
    
    # Static Directory for Frontend Assets
    STATIC_DIR: str = str(BASE_DIR / "static")
    
    # API Key Configuration
    API_KEY_PREFIX: str = "jev-live-"
    DEFAULT_KEY_QUOTA: int = 500000  # Default 500k tokens per generated key
    DEFAULT_RATE_LIMIT_RPM: int = 120  # 120 requests per minute
    
    # Admin Authentication (configured in .env)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    JWT_SECRET: str = "jev_platform_jwt_secret_key_liquidai_2026_super_secure_32bytes_min"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "*",
    ]

    class Config:
        env_file = (str(BASE_DIR / ".env"), str(BASE_DIR.parent / ".env"), ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
