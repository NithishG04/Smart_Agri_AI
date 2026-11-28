"""
Smart Agri AI — Complete Flask Backend
Integrates MySQL database, Flask session authentication + CSRF protection,
Scikit-learn Crop Recommendation (crop_model.pkl), TensorFlow/Keras Plant Disease
Detection (disease_model.h5), Market Prices (MySQL crop_prices), and
Live + Historical Weather (Open-Meteo + MySQL weather_data).
"""

import csv
from datetime import date, datetime
from functools import wraps
import io
import math
import os
import pickle
import re
import secrets
import time
import traceback
import uuid

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    session,
)
from mysql.connector import DataError, IntegrityError
import numpy as np
from PIL import Image, UnidentifiedImageError
import requests
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from agro_catalog import (
    CROP_CATALOG,
    DEFAULT_DISEASE,
    DISEASE_DB,
    DISTRICT_COORDS,
    WMO_WEATHER_MAP,
    build_weather_advisory,
)
from config import Config
from database import (
    DatabaseUnavailableError,
    execute_write,
    init_db,
    query_all,
    query_one,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ─── ML ARTIFACT HOLDERS ──────────────────────────────────────────────────────
disease_model = None
class_indices = None
crop_model = None
crop_scaler = None
crop_encoder = None
crop_features = None
model_status = {
    "crop_model": False,
    "disease_model": False,
    "crop_error": None,
    "disease_error": None,
}

IMG_SIZE = (224, 224)

# Short-lived in-memory cache for Open-Meteo responses (5 minutes)
_weather_cache = {"ts": 0.0, "records": {}}
WEATHER_CACHE_TTL = 300


def load_models():
    """Load trained ML and CNN models from disk if present."""
    global disease_model, class_indices, crop_model, crop_scaler, crop_encoder, crop_features

    # 1. Plant Disease CNN model (.h5 + class_indices.pkl)
    try:
        if not os.path.exists(Config.DISEASE_MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found: {os.path.basename(Config.DISEASE_MODEL_PATH)}"
            )
        if not os.path.exists(Config.CLASS_INDICES_PATH):
            raise FileNotFoundError(
                f"Class mapping not found: {os.path.basename(Config.CLASS_INDICES_PATH)}"
            )
        import tensorflow as tf

        disease_model = tf.keras.models.load_model(Config.DISEASE_MODEL_PATH)
        with open(Config.CLASS_INDICES_PATH, "rb") as fh:
            raw = pickle.load(fh)
        if isinstance(raw, dict) and raw:
            first_val = next(iter(raw.values()))
            class_indices = (
                {int(v): str(k) for k, v in raw.items()}
                if isinstance(first_val, (int, np.integer))
                else {int(k): str(v) for k, v in raw.items()}
            )
        else:
            raise ValueError("Invalid class_indices.pkl structure")

        model_status["disease_model"] = True
        model_status["disease_error"] = None
        print(f"✅ Disease model loaded ({len(class_indices)} classes)")
    except Exception as exc:
        disease_model = None
        class_indices = None
        model_status["disease_model"] = False
        model_status["disease_error"] = str(exc)
        print(f"⚠️  Disease model unavailable: {exc}")

    # 2. Crop Recommendation ML pipeline (.pkl)
    try:
        if not os.path.exists(Config.CROP_MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found: {os.path.basename(Config.CROP_MODEL_PATH)}"
            )
        with open(Config.CROP_MODEL_PATH, "rb") as fh:
            crop_model = pickle.load(fh)

        if os.path.exists(Config.CROP_SCALER_PATH):
            with open(Config.CROP_SCALER_PATH, "rb") as fh:
                crop_scaler = pickle.load(fh)
        if os.path.exists(Config.CROP_ENCODER_PATH):
            with open(Config.CROP_ENCODER_PATH, "rb") as fh:
                crop_encoder = pickle.load(fh)
        if os.path.exists(Config.CROP_FEATURES_PATH):
            with open(Config.CROP_FEATURES_PATH, "rb") as fh:
                crop_features = list(pickle.load(fh))
        else:
            crop_features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

        model_status["crop_model"] = True
        model_status["crop_error"] = None
        print("✅ Crop recommendation model loaded")
    except Exception as exc:
        crop_model = None
        crop_scaler = None
        crop_encoder = None
        crop_features = None
        model_status["crop_model"] = False
        model_status["crop_error"] = str(exc)
        print(f"⚠️  Crop model unavailable: {exc}")


# ─── SECURITY: CSRF & AUTH HELPERS ────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9\s-]{8,24}$")


def is_password_complex(password: str) -> bool:
    """Enforce 8–128 chars with uppercase, lowercase, digit, and special character."""
    if not (8 <= len(password) <= 128):
        return False
    return bool(
        re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[^A-Za-z0-9\s]", password)
    )


def get_or_create_csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


@app.before_request
def enforce_csrf_on_mutations():
    """Verify CSRF token for all state-changing API requests."""
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and request.path.startswith("/api/"):
        expected = session.get("csrf_token")
        provided = (
            request.headers.get("X-CSRF-Token")
            or request.form.get("csrf_token")
            or (request.get_json(silent=True) or {}).get("csrf_token")
        )
        if not expected or not provided or not secrets.compare_digest(str(expected), str(provided)):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid or missing CSRF token. Please refresh and try again.",
                    }
                ),
                403,
            )


def _sanitize_farmer(row: dict) -> dict:
    """Return farmer profile without password hash."""
    if not row:
        return None
    return {
        "id": int(row["id"]),
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "farm_location": row["farm_location"],
        "farm_size": float(row["farm_size"]),
        "soil_type": row["soil_type"],
        "created_at": (
            row["created_at"].isoformat()
            if isinstance(row.get("created_at"), (datetime, date))
            else str(row.get("created_at") or "")
        ),
    }


def login_required(fn):
    """Protect routes so only authenticated farmers can access them."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        farmer_id = session.get("farmer_id")
        if not farmer_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication required. Please log in to continue.",
                        "login_required": True,
                    }
                ),
                401,
            )
        farmer = query_one(
            "SELECT id, name, email, phone, farm_location, farm_size, soil_type, created_at "
            "FROM farmers WHERE id = %s",
            (farmer_id,),
        )
        if not farmer:
            session.clear()
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Session expired. Please log in again.",
                        "login_required": True,
                    }
                ),
                401,
            )
        return fn(farmer, *args, **kwargs)

    return wrapper


# ─── CENTRALIZED ERROR HANDLERS ───────────────────────────────────────────────
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_err):
    return (
        jsonify(
            {
                "success": False,
                "error": f"Uploaded file exceeds maximum allowed size ({Config.MAX_UPLOAD_MB} MB).",
            }
        ),
        413,
    )


@app.errorhandler(DatabaseUnavailableError)
def handle_db_error(err):
    return jsonify({"success": False, "error": str(err)}), 503


@app.errorhandler(404)
def handle_not_found(_err):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "API endpoint not found"}), 404
    return render_template("index.html", initial_section="home", csrf_token=get_or_create_csrf_token())


@app.errorhandler(500)
def handle_server_error(err):
    traceback.print_exc()
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ─── PAGE ROUTES (PRESERVING SINGLE-PAGE APP + CLEAN SECTION URLS) ───────────
@app.route("/")
def index():
    return render_template("index.html", initial_section="home", csrf_token=get_or_create_csrf_token())


@app.route("/login")
def page_login():
    return render_template("index.html", initial_section="login", csrf_token=get_or_create_csrf_token())


@app.route("/register")
def page_register():
    return render_template("index.html", initial_section="register", csrf_token=get_or_create_csrf_token())


@app.route("/dashboard")
def page_dashboard():
    return render_template("index.html", initial_section="dashboard", csrf_token=get_or_create_csrf_token())


@app.route("/disease")
def page_disease():
    return render_template("index.html", initial_section="disease", csrf_token=get_or_create_csrf_token())


@app.route("/market-prices")
def page_market():
    return render_template("index.html", initial_section="market", csrf_token=get_or_create_csrf_token())


@app.route("/weather")
def page_weather():
    return render_template("index.html", initial_section="weather", csrf_token=get_or_create_csrf_token())


@app.route("/logout")
def page_logout():
    return render_template("index.html", initial_section="logout", csrf_token=get_or_create_csrf_token())


# ─── CSRF & HEALTH ROUTES ─────────────────────────────────────────────────────
@app.after_request
def add_no_store_for_dynamic_routes(response):
    if request.path == "/api/csrf-token" or response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/csrf-token", methods=["GET"])
def api_csrf_token():
    return jsonify({"success": True, "csrf_token": get_or_create_csrf_token()})


@app.route("/api/health", methods=["GET"])
def api_health():
    db_ok = True
    try:
        query_one("SELECT 1 AS ok")
    except Exception:
        db_ok = False
    return jsonify(
        {
            "success": True,
            "database": db_ok,
            "models": model_status,
        }
    )


# ─── AUTHENTICATION API ───────────────────────────────────────────────────────
def _extract_auth_payload() -> dict:
    """Read auth fields from JSON body or multipart/urlencoded FormData."""
    json_data = request.get_json(silent=True)
    if isinstance(json_data, dict) and json_data:
        return json_data
    if request.form:
        return request.form.to_dict(flat=True)
    return {}


@app.route("/api/auth/register", methods=["POST"])
def register_farmer():
    data = _extract_auth_payload()

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    phone_raw = str(data.get("phone", "")).strip()
    phone = re.sub(r"[\s-]+", "", phone_raw)
    phone_digits = re.sub(r"\D", "", phone)
    farm_location = str(data.get("farm_location", "")).strip()
    soil_type = str(data.get("soil_type", "")).strip() or "Alluvial Soil"
    password = str(data.get("password", ""))

    try:
        farm_size = float(data.get("farm_size", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Farm size must be a valid number."}), 400

    if len(name) < 2 or len(name) > 120:
        return jsonify({"success": False, "error": "Full name must be between 2 and 120 characters."}), 400
    if len(email) > 160 or not EMAIL_RE.match(email):
        return jsonify({"success": False, "error": "Please enter a valid email address (max 160 characters)."}), 400
    if not PHONE_RE.match(phone_raw) or len(phone) > 24 or not (10 <= len(phone_digits) <= 15):
        return jsonify({"success": False, "error": "Please enter a valid 10 to 15 digit phone number."}), 400
    if not farm_location or len(farm_location) > 100:
        return jsonify({"success": False, "error": "Please select a valid farm location / district (max 100 characters)."}), 400
    if not math.isfinite(farm_size) or farm_size < 0.1 or farm_size > 10000:
        return jsonify({"success": False, "error": "Farm size must be between 0.1 and 10,000 acres."}), 400
    if len(soil_type) > 80:
        return jsonify({"success": False, "error": "Soil type must be 80 characters or fewer."}), 400
    if not is_password_complex(password):
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "Password must be 8–128 characters and include at least one uppercase letter, "
                        "one lowercase letter, one number, and one special character."
                    ),
                }
            ),
            400,
        )

    existing_email = query_one("SELECT id FROM farmers WHERE email = %s", (email,))
    if existing_email:
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

    existing_phone = query_one("SELECT id FROM farmers WHERE phone = %s", (phone,))
    if existing_phone:
        return jsonify({"success": False, "error": "An account with this phone number already exists."}), 409

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        farmer_id = execute_write(
            """
            INSERT INTO farmers (name, email, phone, farm_location, farm_size, soil_type, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (name, email, phone, farm_location, round(farm_size, 2), soil_type, password_hash),
        )
    except IntegrityError as exc:
        err_msg = str(exc)
        print(
            f"[SmartAgri DB] IntegrityError during farmer registration "
            f"(errno={getattr(exc, 'errno', None)}): {err_msg}"
        )
        if "uq_farmers_phone" in err_msg or "phone" in err_msg.lower():
            return jsonify({"success": False, "error": "An account with this phone number already exists."}), 409
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409
    except DataError as exc:
        print(
            f"[SmartAgri DB] DataError during farmer registration "
            f"(errno={getattr(exc, 'errno', None)}): {exc}"
        )
        return (
            jsonify(
                {
                    "success": False,
                    "error": "One or more registration fields violate database column constraints.",
                }
            ),
            400,
        )

    session.permanent = True
    session["farmer_id"] = farmer_id
    session["farmer_name"] = name
    new_csrf = secrets.token_urlsafe(32)
    session["csrf_token"] = new_csrf

    farmer = query_one(
        "SELECT id, name, email, phone, farm_location, farm_size, soil_type, created_at "
        "FROM farmers WHERE id = %s",
        (farmer_id,),
    )
    return (
        jsonify(
            {
                "success": True,
                "message": "Registration successful.",
                "csrf_token": new_csrf,
                "farmer": _sanitize_farmer(farmer),
            }
        ),
        201,
    )


@app.route("/api/auth/login", methods=["POST"])
def login_farmer():
    data = _extract_auth_payload()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(email) > 160 or not EMAIL_RE.match(email) or not password:
        return jsonify({"success": False, "error": "Valid email and password are required."}), 400

    farmer = query_one(
        "SELECT id, name, email, phone, farm_location, farm_size, soil_type, password, created_at "
        "FROM farmers WHERE email = %s",
        (email,),
    )
    if not farmer or not check_password_hash(farmer["password"], password):
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    session.permanent = True
    session["farmer_id"] = int(farmer["id"])
    session["farmer_name"] = farmer["name"]
    new_csrf = secrets.token_urlsafe(32)
    session["csrf_token"] = new_csrf

    return jsonify(
        {
            "success": True,
            "message": "Login successful.",
            "csrf_token": new_csrf,
            "farmer": _sanitize_farmer(farmer),
        }
    )


@app.route("/api/auth/logout", methods=["POST"])
def logout_farmer():
    session.clear()
    new_csrf = get_or_create_csrf_token()
    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully.",
            "csrf_token": new_csrf,
        }
    )


@app.route("/api/auth/me", methods=["GET"])
def current_farmer():
    farmer_id = session.get("farmer_id")
    if not farmer_id:
        return jsonify({"success": False, "authenticated": False, "farmer": None}), 401

    farmer = query_one(
        "SELECT id, name, email, phone, farm_location, farm_size, soil_type, created_at "
        "FROM farmers WHERE id = %s",
        (farmer_id,),
    )
    if not farmer:
        session.clear()
        return jsonify({"success": False, "authenticated": False, "farmer": None}), 401

    return jsonify(
        {
            "success": True,
            "authenticated": True,
            "csrf_token": get_or_create_csrf_token(),
            "farmer": _sanitize_farmer(farmer),
        }
    )


# ─── WEATHER SERVICE (OPEN-METEO LIVE + MYSQL HISTORICAL) ─────────────────────
def _fetch_open_meteo_for_district(district: str):
    """Fetch live weather for a Tamil Nadu district from Open-Meteo API."""
    coords = DISTRICT_COORDS.get(district)
    if not coords:
        return None
    lat, lon = coords
    resp = requests.get(
        Config.OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "timezone": "Asia/Kolkata",
        },
        timeout=Config.WEATHER_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    payload = resp.json()
    current = payload.get("current") or {}
    code = int(current.get("weather_code", 0))
    icon, cond_en, cond_ta = WMO_WEATHER_MAP.get(code, ("⛅", "Partly Cloudy", "பகுதியளவு மேகமூட்டம்"))
    temp = round(float(current.get("temperature_2m", 30.0)), 1)
    feels = round(float(current.get("apparent_temperature", temp)), 1)
    humidity = round(float(current.get("relative_humidity_2m", 65.0)), 1)
    rainfall = round(float(current.get("precipitation", 0.0)), 1)
    wind = round(float(current.get("wind_speed_10m", 12.0)), 1)
    adv_en, adv_ta = build_weather_advisory(temp, humidity, rainfall)

    return {
        "district": district,
        "condition": icon,
        "condition_name": cond_en,
        "condition_ta": cond_ta,
        "temp": temp,
        "feels": feels,
        "humidity": humidity,
        "rainfall": rainfall,
        "wind": wind,
        "advisory_en": adv_en,
        "advisory_ta": adv_ta,
        "source": "open-meteo-live",
        "is_live": True,
        "date": date.today().isoformat(),
    }


def _get_live_weather_map(target_districts=None):
    """Fetch live Open-Meteo records with 5-min caching and safe error reporting."""
    now = time.time()
    districts_to_fetch = target_districts or list(DISTRICT_COORDS.keys())
    results = {}
    live_error = None

    if now - _weather_cache["ts"] < WEATHER_CACHE_TTL and _weather_cache["records"]:
        for dist in districts_to_fetch:
            if dist in _weather_cache["records"]:
                results[dist] = _weather_cache["records"][dist]
        if len(results) == len(districts_to_fetch):
            return results, None

    # Open-Meteo supports multi-location batch requests with comma-separated lat/lon!
    try:
        lats = ",".join(str(DISTRICT_COORDS[d][0]) for d in districts_to_fetch)
        lons = ",".join(str(DISTRICT_COORDS[d][1]) for d in districts_to_fetch)
        resp = requests.get(
            Config.OPEN_METEO_URL,
            params={
                "latitude": lats,
                "longitude": lons,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "Asia/Kolkata",
            },
            timeout=Config.WEATHER_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        payload = resp.json()
        items = payload if isinstance(payload, list) else [payload]

        today_str = date.today().isoformat()
        for dist, item in zip(districts_to_fetch, items):
            current = item.get("current") or {}
            code = int(current.get("weather_code", 0))
            icon, cond_en, cond_ta = WMO_WEATHER_MAP.get(
                code, ("⛅", "Partly Cloudy", "பகுதியளவு மேகமூட்டம்")
            )
            temp = round(float(current.get("temperature_2m", 30.0)), 1)
            feels = round(float(current.get("apparent_temperature", temp)), 1)
            humidity = round(float(current.get("relative_humidity_2m", 65.0)), 1)
            rainfall = round(float(current.get("precipitation", 0.0)), 1)
            wind = round(float(current.get("wind_speed_10m", 12.0)), 1)
            adv_en, adv_ta = build_weather_advisory(temp, humidity, rainfall)

            rec = {
                "district": dist,
                "condition": icon,
                "condition_name": cond_en,
                "condition_ta": cond_ta,
                "temp": temp,
                "feels": feels,
                "humidity": humidity,
                "rainfall": rainfall,
                "wind": wind,
                "advisory_en": adv_en,
                "advisory_ta": adv_ta,
                "source": "open-meteo-live",
                "is_live": True,
                "date": today_str,
            }
            results[dist] = rec
            _weather_cache["records"][dist] = rec

            # Persist today's live reading into MySQL weather_data as 'live' snapshot
            try:
                execute_write(
                    """
                    INSERT INTO weather_data
                        (district, temperature, humidity, rainfall, wind_speed, condition_name, source, date)
                    VALUES (%s, %s, %s, %s, %s, %s, 'live', %s)
                    ON DUPLICATE KEY UPDATE
                        temperature = VALUES(temperature),
                        humidity = VALUES(humidity),
                        rainfall = VALUES(rainfall),
                        wind_speed = VALUES(wind_speed),
                        condition_name = VALUES(condition_name)
                    """,
                    (dist, temp, humidity, rainfall, wind, cond_en, today_str),
                )
            except Exception:
                pass

        _weather_cache["ts"] = now
    except Exception as exc:
        live_error = f"Live weather API unavailable: {exc}"

    return results, live_error


def _condition_meta_from_name(name: str):
    lower = (name or "").lower()
    if "thunder" in lower:
        return "⛈️", "Thunderstorm", "இடியுடன் மழை"
    if "heavy rain" in lower:
        return "🌧️", name, "கனமழை"
    if "rain" in lower or "drizzle" in lower or "shower" in lower:
        return "🌦️", name, "லேசான மழை"
    if "overcast" in lower:
        return "☁️", name, "மேகமூட்டம்"
    if "cloud" in lower:
        return "⛅", name, "பகுதியளவு மேகமூட்டம்"
    return "☀️", name or "Clear Sky", "தெளிவான வானம்"


def _get_historical_weather(district_filter: str = ""):
    if district_filter:
        rows = query_all(
            """
            SELECT district, temperature, humidity, rainfall, wind_speed, condition_name, source, date
            FROM weather_data
            WHERE LOWER(district) = LOWER(%s)
            ORDER BY date DESC, FIELD(source, 'historical', 'live')
            LIMIT 20
            """,
            (district_filter,),
        )
    else:
        rows = query_all(
            """
            SELECT district, temperature, humidity, rainfall, wind_speed, condition_name, source, date
            FROM weather_data
            ORDER BY date DESC, district ASC
            LIMIT 40
            """
        )

    out = []
    for r in rows:
        temp = float(r["temperature"])
        hum = float(r["humidity"])
        rain = float(r["rainfall"])
        wind = float(r.get("wind_speed") or 12.0)
        icon, cond_en, cond_ta = _condition_meta_from_name(r.get("condition_name"))
        adv_en, adv_ta = build_weather_advisory(temp, hum, rain)
        out.append(
            {
                "district": r["district"],
                "condition": icon,
                "condition_name": cond_en,
                "condition_ta": cond_ta,
                "temp": temp,
                "feels": round(temp + (1.5 if hum > 70 else 0.5), 1),
                "humidity": hum,
                "rainfall": rain,
                "wind": wind,
                "advisory_en": adv_en,
                "advisory_ta": adv_ta,
                "source": r["source"],
                "is_live": False,
                "date": r["date"].isoformat() if isinstance(r["date"], (date, datetime)) else str(r["date"]),
            }
        )
    return out


def _resolve_district_climate(district: str):
    """Look up live or historical climate values for a district for 7-feature crop ML."""
    live_map, _ = _get_live_weather_map([district] if district in DISTRICT_COORDS else [])
    if district in live_map:
        w = live_map[district]
        return float(w["temp"]), float(w["humidity"]), max(float(w["rainfall"]) * 25.0, 60.0)

    row = query_one(
        "SELECT temperature, humidity, rainfall FROM weather_data "
        "WHERE LOWER(district) = LOWER(%s) ORDER BY date DESC LIMIT 1",
        (district,),
    )
    if row:
        return (
            float(row["temperature"]),
            float(row["humidity"]),
            max(float(row["rainfall"]) * 25.0, 60.0),
        )
    return 27.0, 72.0, 120.0


@app.route("/api/weather", methods=["GET"])
@app.route("/api/weather/data", methods=["GET"])
def get_weather():
    district = str(request.args.get("district", "")).strip()
    mode = str(request.args.get("mode", "all")).strip().lower()

    if district and district.lower() != "all":
        matched = next(
            (d for d in DISTRICT_COORDS.keys() if d.lower() == district.lower()),
            None,
        )
        if not matched:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Unknown district '{district}'. Choose a valid Tamil Nadu district.",
                    }
                ),
                400,
            )
        target = [matched]
        district_filter = matched
    else:
        target = list(DISTRICT_COORDS.keys())
        district_filter = ""

    live_list = []
    live_error = None
    if mode in ("all", "live"):
        live_map, live_error = _get_live_weather_map(target)
        live_list = [live_map[d] for d in target if d in live_map]

    historical_list = []
    if mode in ("all", "historical") or (mode == "live" and not live_list):
        historical_list = _get_historical_weather(district_filter)

    combined = live_list if live_list else historical_list

    return jsonify(
        {
            "success": True,
            "data": combined,
            "live_data": live_list,
            "historical_data": historical_list,
            "live_available": len(live_list) > 0,
            "live_error": live_error,
            "districts": sorted(DISTRICT_COORDS.keys()),
        }
    )


# ─── FARMER DASHBOARD & HISTORY API ───────────────────────────────────────────
@app.route("/api/dashboard", methods=["GET"])
@login_required
def get_dashboard(farmer):
    farmer_id = int(farmer["id"])

    soil_count_row = query_one(
        "SELECT COUNT(*) AS cnt FROM soil_test WHERE farmer_id = %s", (farmer_id,)
    )
    disease_count_row = query_one(
        "SELECT COUNT(*) AS cnt FROM disease_history WHERE farmer_id = %s", (farmer_id,)
    )
    latest_soil = query_one(
        """
        SELECT id, nitrogen, phosphorus, potassium, ph, district, confidence, recommendation, date
        FROM soil_test
        WHERE farmer_id = %s
        ORDER BY date DESC, id DESC
        LIMIT 1
        """,
        (farmer_id,),
    )
    recent_soil = query_all(
        """
        SELECT id, nitrogen, phosphorus, potassium, ph, district, confidence, recommendation, date
        FROM soil_test
        WHERE farmer_id = %s
        ORDER BY date DESC, id DESC
        LIMIT 5
        """,
        (farmer_id,),
    )
    recent_diseases = query_all(
        """
        SELECT id, crop_type, disease_name, confidence, severity, image_path, date
        FROM disease_history
        WHERE farmer_id = %s
        ORDER BY date DESC, id DESC
        LIMIT 5
        """,
        (farmer_id,),
    )

    activities = []
    for s in recent_soil:
        crop_key = (s["recommendation"] or "").strip().lower()
        meta = CROP_CATALOG.get(crop_key, {})
        activities.append(
            {
                "type": "soil_test",
                "icon": meta.get("icon", "🌾"),
                "title_en": f"Crop Recommendation — {s['recommendation']}",
                "title_ta": f"பயிர் பரிந்துரை — {meta.get('name_ta', s['recommendation'])}",
                "sub_en": f"N:{float(s['nitrogen']):.0f} P:{float(s['phosphorus']):.0f} K:{float(s['potassium']):.0f} • Confidence {float(s['confidence'] or 0):.1f}%",
                "sub_ta": f"N:{float(s['nitrogen']):.0f} P:{float(s['phosphorus']):.0f} K:{float(s['potassium']):.0f} • நம்பகத்தன்மை {float(s['confidence'] or 0):.1f}%",
                "date": s["date"].isoformat() if isinstance(s["date"], (datetime, date)) else str(s["date"]),
            }
        )
    for d in recent_diseases:
        activities.append(
            {
                "type": "disease_scan",
                "icon": "🔬",
                "title_en": f"Disease Scan — {d['disease_name']} ({d['crop_type']})",
                "title_ta": f"நோய் ஸ்கேன் — {d['disease_name']} ({d['crop_type']})",
                "sub_en": f"Confidence {float(d['confidence']):.1f}% • Severity: {str(d['severity']).title()}",
                "sub_ta": f"நம்பகத்தன்மை {float(d['confidence']):.1f}% • தீவிரம்: {str(d['severity']).title()}",
                "date": d["date"].isoformat() if isinstance(d["date"], (datetime, date)) else str(d["date"]),
            }
        )
    activities.sort(key=lambda item: item["date"], reverse=True)

    # Latest weather for the farmer's farm location
    loc = farmer["farm_location"]
    weather_info = None
    if loc in DISTRICT_COORDS:
        live_map, _ = _get_live_weather_map([loc])
        weather_info = live_map.get(loc)
    if weather_info is None:
        hist = _get_historical_weather(loc)
        weather_info = hist[0] if hist else None

    latest_rec_formatted = None
    if latest_soil:
        ckey = (latest_soil["recommendation"] or "").strip().lower()
        cmeta = CROP_CATALOG.get(ckey, {})
        latest_rec_formatted = {
            "crop_name": latest_soil["recommendation"],
            "crop_name_ta": cmeta.get("name_ta", latest_soil["recommendation"]),
            "confidence": float(latest_soil["confidence"] or 0),
            "nitrogen": float(latest_soil["nitrogen"]),
            "phosphorus": float(latest_soil["phosphorus"]),
            "potassium": float(latest_soil["potassium"]),
            "date": (
                latest_soil["date"].isoformat()
                if isinstance(latest_soil["date"], (datetime, date))
                else str(latest_soil["date"])
            ),
        }

    return jsonify(
        {
            "success": True,
            "data": {
                "farmer": _sanitize_farmer(farmer),
                "total_soil_tests": int(soil_count_row["cnt"]) if soil_count_row else 0,
                "total_disease_detections": int(disease_count_row["cnt"]) if disease_count_row else 0,
                "latest_recommendation": latest_rec_formatted,
                "recent_activity": activities[:8],
                "weather": weather_info,
            },
        }
    )


@app.route("/api/soil-tests", methods=["GET"])
@login_required
def list_soil_tests(farmer):
    rows = query_all(
        """
        SELECT id, nitrogen, phosphorus, potassium, ph, district,
               temperature, humidity, rainfall, confidence, recommendation, date
        FROM soil_test
        WHERE farmer_id = %s
        ORDER BY date DESC, id DESC
        LIMIT 25
        """,
        (farmer["id"],),
    )
    items = []
    for r in rows:
        ckey = (r["recommendation"] or "").strip().lower()
        cmeta = CROP_CATALOG.get(ckey, {})
        items.append(
            {
                "id": int(r["id"]),
                "nitrogen": float(r["nitrogen"]),
                "phosphorus": float(r["phosphorus"]),
                "potassium": float(r["potassium"]),
                "ph": float(r["ph"]),
                "district": r["district"],
                "confidence": float(r["confidence"] or 0),
                "recommendation": r["recommendation"],
                "recommendation_ta": cmeta.get("name_ta", r["recommendation"]),
                "icon": cmeta.get("icon", "🌱"),
                "date": r["date"].isoformat() if isinstance(r["date"], (datetime, date)) else str(r["date"]),
            }
        )
    return jsonify({"success": True, "data": items})


@app.route("/api/disease-history", methods=["GET"])
@login_required
def list_disease_history(farmer):
    rows = query_all(
        """
        SELECT id, crop_type, disease_name, confidence, severity, image_path, treatment, date
        FROM disease_history
        WHERE farmer_id = %s
        ORDER BY date DESC, id DESC
        LIMIT 25
        """,
        (farmer["id"],),
    )
    items = [
        {
            "id": int(r["id"]),
            "crop_type": r["crop_type"],
            "disease_name": r["disease_name"],
            "confidence": float(r["confidence"]),
            "severity": r["severity"],
            "image_url": f"/uploads/{os.path.basename(r['image_path'])}",
            "treatment": r["treatment"],
            "date": r["date"].isoformat() if isinstance(r["date"], (datetime, date)) else str(r["date"]),
        }
        for r in rows
    ]
    return jsonify({"success": True, "data": items})


# ─── CROP RECOMMENDATION (ML INTEGRATION) ─────────────────────────────────────
@app.route("/api/crop/predict", methods=["POST"])
@login_required
def predict_crop(farmer):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "error": "No soil data provided."}), 400

    try:
        nitrogen = float(data.get("nitrogen"))
        phosphorus = float(data.get("phosphorus"))
        potassium = float(data.get("potassium"))
    except (TypeError, ValueError):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Nitrogen (N), Phosphorus (P), and Potassium (K) must be valid numbers.",
                }
            ),
            400,
        )

    if not (0 <= nitrogen <= 300 and 0 <= phosphorus <= 300 and 0 <= potassium <= 300):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "NPK values must be between 0 and 300 kg/ha.",
                }
            ),
            400,
        )

    try:
        ph = float(data.get("ph", 6.5))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Soil pH must be a valid number."}), 400
    if not (3.0 <= ph <= 10.0):
        return jsonify({"success": False, "error": "Soil pH must be between 3.0 and 10.0."}), 400

    district = str(data.get("district") or farmer["farm_location"] or "").strip()
    if not district:
        return jsonify({"success": False, "error": "Please select a district."}), 400

    if crop_model is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "Crop recommendation model (crop_model.pkl) is not loaded on this server. "
                        f"Details: {model_status.get('crop_error') or 'Missing model file'}"
                    ),
                }
            ),
            503,
        )

    default_temp, default_hum, default_rain = _resolve_district_climate(district)
    try:
        temperature = float(data["temperature"]) if data.get("temperature") not in (None, "") else default_temp
        humidity = float(data["humidity"]) if data.get("humidity") not in (None, "") else default_hum
        rainfall = float(data["rainfall"]) if data.get("rainfall") not in (None, "") else default_rain
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Climate parameters must be numeric."}), 400

    feature_names = crop_features or ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    feat_map = {
        "N": nitrogen,
        "P": phosphorus,
        "K": potassium,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
    }
    features = np.array([[feat_map.get(name, 0.0) for name in feature_names]], dtype=np.float64)

    if crop_scaler is not None:
        features = crop_scaler.transform(features)

    prediction = crop_model.predict(features)
    proba = crop_model.predict_proba(features) if hasattr(crop_model, "predict_proba") else None
    if proba is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Loaded crop model does not expose probability estimates.",
                }
            ),
            500,
        )
    confidence = round(float(np.max(proba)) * 100.0, 1)

    crop_raw = prediction[0]
    if crop_encoder is not None:
        try:
            crop_raw = crop_encoder.inverse_transform(prediction)[0]
        except Exception:
            pass
    crop_key = str(crop_raw).strip().lower()

    meta = CROP_CATALOG.get(crop_key, {})
    crop_name_en = meta.get("name_en", str(crop_raw).strip().title())
    crop_name_ta = meta.get("name_ta", crop_name_en)
    desc_en = meta.get(
        "desc_en",
        f"Based on your soil NPK ({nitrogen:.0f}/{phosphorus:.0f}/{potassium:.0f}) and pH {ph:.1f}, {crop_name_en} is recommended.",
    )
    desc_ta = meta.get(
        "desc_ta",
        f"உங்கள் மண் NPK ({nitrogen:.0f}/{phosphorus:.0f}/{potassium:.0f}) மற்றும் pH {ph:.1f} அடிப்படையில் {crop_name_ta} பரிந்துரைக்கப்படுகிறது.",
    )
    icon = meta.get("icon", "🌱")

    now_dt = datetime.now().replace(microsecond=0)
    record_id = execute_write(
        """
        INSERT INTO soil_test
            (farmer_id, nitrogen, phosphorus, potassium, ph, district,
             temperature, humidity, rainfall, confidence, recommendation, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            farmer["id"],
            round(nitrogen, 2),
            round(phosphorus, 2),
            round(potassium, 2),
            round(ph, 2),
            district,
            round(temperature, 2),
            round(humidity, 2),
            round(rainfall, 2),
            confidence,
            crop_name_en,
            now_dt,
        ),
    )

    return jsonify(
        {
            "success": True,
            "data": {
                "id": record_id,
                "crop_name": crop_name_en,
                "crop_name_ta": crop_name_ta,
                "confidence": confidence,
                "description_en": desc_en,
                "description_ta": desc_ta,
                "icon": icon,
                "npk_summary": {
                    "nitrogen": nitrogen,
                    "phosphorus": phosphorus,
                    "potassium": potassium,
                    "ph": ph,
                    "district": district,
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "rainfall": round(rainfall, 1),
                },
                "date": now_dt.isoformat(),
            },
        }
    )


# ─── PLANT DISEASE DETECTION (CNN INTEGRATION) ────────────────────────────────
def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def _preprocess_image(img_bytes: bytes) -> np.ndarray:
    with Image.open(io.BytesIO(img_bytes)) as verify_img:
        verify_img.verify()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def _class_key_to_display(class_key: str):
    parts = class_key.split("___")
    plant = parts[0].replace("_", " ").strip() if len(parts) > 0 else "Unknown"
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    return plant, disease


@app.route("/api/disease/detect", methods=["POST"])
@login_required
def detect_disease(farmer):
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided."}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid file type. Allowed formats: PNG, JPG, JPEG, WEBP.",
                }
            ),
            400,
        )

    img_bytes = file.read()
    if not img_bytes:
        return jsonify({"success": False, "error": "Uploaded file is empty."}), 400
    if len(img_bytes) > Config.MAX_CONTENT_LENGTH:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Image exceeds {Config.MAX_UPLOAD_MB} MB size limit.",
                }
            ),
            413,
        )

    if disease_model is None or class_indices is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "Plant disease CNN model (disease_model.h5) is not loaded on this server. "
                        f"Details: {model_status.get('disease_error') or 'Missing model file'}"
                    ),
                }
            ),
            503,
        )

    try:
        img_array = _preprocess_image(img_bytes)
    except (UnidentifiedImageError, OSError):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Uploaded file is not a valid readable image.",
                }
            ),
            400,
        )

    predictions = disease_model.predict(img_array, verbose=0)
    pred_idx = int(np.argmax(predictions[0]))
    confidence = round(float(np.max(predictions[0])) * 100.0, 1)

    class_key = class_indices.get(pred_idx, "")
    if not class_key:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Model predicted unmapped class index: {pred_idx}.",
                }
            ),
            500,
        )

    info = DISEASE_DB.get(class_key)
    if info is None:
        normalized = class_key.lower().replace(" ", "")
        for db_key, db_val in DISEASE_DB.items():
            if db_key.lower().replace(" ", "") == normalized:
                info = db_val
                break
    if info is None:
        plant, disease = _class_key_to_display(class_key)
        info = dict(DEFAULT_DISEASE)
        info["disease_name"] = disease
        info["crop_name"] = plant
        info["disease_name_ta"] = disease
        info["crop_name_ta"] = plant

    original_clean = secure_filename(file.filename) or "leaf.jpg"
    unique_name = f"farmer_{farmer['id']}_{uuid.uuid4().hex[:12]}_{original_clean}"
    upload_dir = os.path.abspath(app.config["UPLOAD_FOLDER"])
    save_path = os.path.abspath(os.path.join(upload_dir, unique_name))
    if os.path.commonpath([upload_dir, save_path]) != upload_dir:
        return jsonify({"success": False, "error": "Invalid upload filename."}), 400

    with open(save_path, "wb") as out_fh:
        out_fh.write(img_bytes)

    now_dt = datetime.now().replace(microsecond=0)
    record_id = execute_write(
        """
        INSERT INTO disease_history
            (farmer_id, crop_type, disease_name, confidence, severity, image_path, treatment, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            farmer["id"],
            info["crop_name"],
            info["disease_name"],
            confidence,
            info["severity"],
            unique_name,
            info["treatment_en"],
            now_dt,
        ),
    )

    return jsonify(
        {
            "success": True,
            "data": {
                "id": record_id,
                "disease_name": info["disease_name"],
                "disease_name_ta": info["disease_name_ta"],
                "severity": info["severity"],
                "confidence": confidence,
                "crop_name": info["crop_name"],
                "crop_name_ta": info["crop_name_ta"],
                "description_en": info.get("description_en", ""),
                "description_ta": info.get("description_ta", ""),
                "treatment_en": info["treatment_en"],
                "treatment_ta": info["treatment_ta"],
                "class_key": class_key,
                "image_url": f"/uploads/{unique_name}",
                "date": now_dt.isoformat(),
            },
        }
    )


@app.route("/uploads/<path:filename>", methods=["GET"])
@login_required
def uploaded_file(farmer, filename):
    clean_name = os.path.basename(filename)
    upload_dir = os.path.abspath(app.config["UPLOAD_FOLDER"])
    target_path = os.path.abspath(os.path.join(upload_dir, clean_name))
    if os.path.commonpath([upload_dir, target_path]) != upload_dir:
        return jsonify({"success": False, "error": "Invalid file path."}), 400

    owned = query_one(
        "SELECT id FROM disease_history WHERE farmer_id = %s AND image_path = %s",
        (farmer["id"], clean_name),
    )
    if not owned:
        return jsonify({"success": False, "error": "Access denied."}), 403

    return send_from_directory(upload_dir, clean_name)


# ─── MARKET PRICES API (MYSQL crop_prices) ────────────────────────────────────
@app.route("/api/market-prices", methods=["GET"])
@app.route("/api/market/prices", methods=["GET"])
def get_market_prices():
    district = str(request.args.get("district", "All")).strip()
    search = str(request.args.get("search", "")).strip()
    sort_by = str(request.args.get("sort", "date_desc")).strip().lower()

    where_clauses = []
    params = []

    if district and district.lower() != "all":
        where_clauses.append("LOWER(district) = LOWER(%s)")
        params.append(district)

    if search:
        where_clauses.append("(LOWER(crop_name) LIKE %s OR LOWER(district) LIKE %s)")
        like_val = f"%{search.lower()}%"
        params.extend([like_val, like_val])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    order_map = {
        "price_asc": "price ASC, crop_name ASC",
        "price_desc": "price DESC, crop_name ASC",
        "crop_asc": "crop_name ASC, district ASC",
        "date_desc": "date_recorded DESC, crop_name ASC, district ASC",
    }
    order_sql = order_map.get(sort_by, order_map["date_desc"])

    rows = query_all(
        f"""
        SELECT id, crop_name, price, previous_price, district, date_recorded
        FROM crop_prices
        {where_sql}
        ORDER BY {order_sql}
        LIMIT 250
        """,
        tuple(params),
    )

    distinct_districts = query_all(
        "SELECT DISTINCT district FROM crop_prices ORDER BY district ASC"
    )

    records = []
    for r in rows:
        price = float(r["price"])
        prev = float(r["previous_price"]) if r.get("previous_price") is not None else price
        diff = round(price - prev, 2)
        pct = round((diff / prev) * 100.0, 1) if prev > 0 else 0.0
        ckey = r["crop_name"].strip().lower()
        cmeta = CROP_CATALOG.get(ckey, {})
        records.append(
            {
                "id": int(r["id"]),
                "crop": r["crop_name"],
                "crop_ta": cmeta.get("name_ta", r["crop_name"]),
                "price": price,
                "district": r["district"],
                "change": f"{'+' if diff >= 0 else ''}{pct:.1f}%",
                "change_amount": diff,
                "up": diff >= 0,
                "date": (
                    r["date_recorded"].isoformat()
                    if isinstance(r["date_recorded"], (date, datetime))
                    else str(r["date_recorded"])
                ),
            }
        )

    return jsonify(
        {
            "success": True,
            "data": records,
            "districts": [d["district"] for d in distinct_districts],
            "total": len(records),
        }
    )


# ─── CROP DETAILS REAL-TIME SEARCH API ────────────────────────────────────────
_crop_stats_cache = None


def _load_crop_dataset_stats() -> dict:
    """Compute empirical soil NPK & climate ranges per crop from crop_data.csv."""
    global _crop_stats_cache
    if _crop_stats_cache is not None:
        return _crop_stats_cache

    stats = {}
    csv_path = os.path.join(Config.BASE_DIR, "crop_data.csv")
    if not os.path.exists(csv_path):
        _crop_stats_cache = stats
        return stats

    buckets = {}
    numeric_cols = ("N", "P", "K", "temperature", "humidity", "ph", "rainfall")
    with open(csv_path, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            label = (row.get("label") or "").strip().lower()
            if not label:
                continue
            bucket = buckets.setdefault(label, {col: [] for col in numeric_cols})
            for col in numeric_cols:
                try:
                    bucket[col].append(float(row[col]))
                except (KeyError, TypeError, ValueError):
                    pass

    for label, cols in buckets.items():
        if not cols["N"]:
            continue
        summary = {}
        for col, vals in cols.items():
            if vals:
                key = col.lower()
                summary[f"{key}_min"] = round(min(vals), 1)
                summary[f"{key}_max"] = round(max(vals), 1)
                summary[f"{key}_avg"] = round(sum(vals) / len(vals), 1)
        summary["samples"] = len(cols["N"])
        stats[label] = summary

    _crop_stats_cache = stats
    return stats


@app.route("/api/crops/search", methods=["GET"])
def search_crops():
    query_text = str(request.args.get("q", "")).strip().lower()
    stats_map = _load_crop_dataset_stats()

    # Optional APMC price average per crop from MySQL if available
    market_avg = {}
    try:
        price_rows = query_all(
            "SELECT LOWER(crop_name) AS ckey, ROUND(AVG(price), 2) AS avg_price, "
            "MIN(price) AS min_price, MAX(price) AS max_price "
            "FROM crop_prices GROUP BY LOWER(crop_name)"
        )
        for pr in price_rows:
            market_avg[pr["ckey"]] = {
                "avg_price": float(pr["avg_price"]),
                "min_price": float(pr["min_price"]),
                "max_price": float(pr["max_price"]),
            }
    except Exception:
        market_avg = {}

    results = []
    for key, meta in CROP_CATALOG.items():
        haystack = " ".join(
            [
                key,
                meta.get("name_en", ""),
                meta.get("name_ta", ""),
                meta.get("desc_en", ""),
                meta.get("desc_ta", ""),
            ]
        ).lower()
        if query_text and query_text not in haystack:
            continue

        crop_stats = stats_map.get(key)
        results.append(
            {
                "key": key,
                "name_en": meta.get("name_en", key.title()),
                "name_ta": meta.get("name_ta", meta.get("name_en", key.title())),
                "icon": meta.get("icon", "🌱"),
                "desc_en": meta.get("desc_en", ""),
                "desc_ta": meta.get("desc_ta", ""),
                "is_ml_crop": crop_stats is not None,
                "stats": crop_stats,
                "market": market_avg.get(key) or market_avg.get(meta.get("name_en", "").lower()),
            }
        )

    # Sort exact prefix matches first, then ML crops alphabetically
    results.sort(
        key=lambda item: (
            0 if (query_text and item["name_en"].lower().startswith(query_text)) else 1,
            0 if item["is_ml_crop"] else 1,
            item["name_en"].lower(),
        )
    )
    return jsonify({"success": True, "data": results, "total": len(results)})


# ─── STARTUP ──────────────────────────────────────────────────────────────────
init_db()
load_models()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.PORT)
