"""
Smart Agri AI — Application Configuration
Loads settings from environment variables (.env) with safe defaults.
"""

import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Central configuration for Flask, MySQL, uploads, and ML artifacts."""

    BASE_DIR = BASE_DIR

    # Security & Sessions
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
    SESSION_COOKIE_NAME = "smart_agri_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _as_bool(os.environ.get("SESSION_COOKIE_SECURE"), False)
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Server
    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG"), False)
    PORT = int(os.environ.get("FLASK_PORT", 5000))

    # MySQL Database
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "smart_agri")

    # File Uploads
    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 10))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    UPLOAD_FOLDER = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("UPLOAD_FOLDER", "uploads"))
    )
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "gif"}

    # ML Artifacts & Datasets
    CROP_MODEL_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("CROP_MODEL_PATH", "crop_model.pkl"))
    )
    CROP_SCALER_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("CROP_SCALER_PATH", "crop_scaler.pkl"))
    )
    CROP_ENCODER_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("CROP_ENCODER_PATH", "crop_encoder.pkl"))
    )
    CROP_FEATURES_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("CROP_FEATURES_PATH", "crop_features.pkl"))
    )
    DISEASE_MODEL_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("DISEASE_MODEL_PATH", "disease_model.h5"))
    )
    CLASS_INDICES_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("CLASS_INDICES_PATH", "class_indices.pkl"))
    )
    MARKET_CSV_PATH = os.path.abspath(
        os.path.join(BASE_DIR, os.environ.get("MARKET_CSV_PATH", "market_data.csv"))
    )

    # Weather API
    OPEN_METEO_URL = os.environ.get(
        "OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast"
    )
    WEATHER_TIMEOUT_SECONDS = int(os.environ.get("WEATHER_TIMEOUT_SECONDS", 6))
