# Smart Agri AI — Flask + MySQL + ML/CNN Full-Stack Application

**Smart Agri AI** is a bilingual (English & தமிழ்) intelligent farming platform built with **HTML5 / CSS3 / Vanilla JavaScript**, **Python Flask**, **MySQL (`smart_agri`)**, **Scikit-learn** (`crop_model.pkl`), **TensorFlow / Keras** (`disease_model.h5`), and **Open-Meteo Live Weather**.

---

## 1. Project Structure

```text
smart_agri_ai/
├── app.py                     # Flask backend, auth/sessions, CSRF, ML/CNN, Market & Weather APIs
├── config.py                  # Environment & configuration loader
├── database.py                # MySQL connection pool, schema bootstrap, non-destructive dataset seeding
├── agro_catalog.py            # Bilingual 38+ PlantVillage disease guide, 22 ML crops, TN district coordinates
├── schema.sql                 # Standalone MySQL schema for database `smart_agri`
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── crop_data.csv              # Crop training reference dataset (22 crops)
├── market_data.csv            # Tamil Nadu APMC price dataset
├── templates/
│   └── index.html             # Preserved Vanilla HTML5/CSS3/JS UI + Auth, Dashboard, ML, Market & Weather
├── static/
│   └── js/
│       ├── api.js             # Credentialed fetch() API client with automatic CSRF tokens
│       └── translations.js    # Centralized English & Tamil dictionaries
├── uploads/                   # Secure leaf upload directory (scoped per farmer)
└── tests/
    └── test_smart_agri.py     # Verification test suite
```

---

## 2. Model Files Placement

Place your trained model files directly inside the `smart_agri_ai/` root folder (alongside `app.py`):

- `crop_model.pkl`
- `crop_scaler.pkl`
- `crop_encoder.pkl`
- `crop_features.pkl`
- `disease_model.h5`
- `class_indices.pkl`

> **Note:** Smart Agri AI never fabricates predictions or dummy confidence scores. If a model file is missing, `/api/crop/predict` or `/api/disease/detect` returns a clear `503` error naming the missing artifact.

---

## 3. Local Setup & Running Instructions

### Step 1 — Create Python Virtual Environment & Install Dependencies
```bash
cd smart_agri_ai
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2 — Configure MySQL & Environment Variables
1. Ensure MySQL Server is running locally (default `127.0.0.1:3306`).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with a strong `FLASK_SECRET_KEY` and your `MYSQL_USER` / `MYSQL_PASSWORD`:
   ```env
   FLASK_SECRET_KEY=replace-with-a-random-64-char-hex-secret
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=smart_agri
   ```
4. *(Optional)* Run `schema.sql` manually if you prefer manual provisioning — otherwise `app.py` runs `init_db()` on startup, automatically creates `smart_agri` and all 5 tables (`farmers`, `soil_test`, `disease_history`, `crop_prices`, `weather_data`), and seeds empty `crop_prices` / `weather_data` tables non-destructively.

### Step 3 — Start the Flask Application
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 4. Symposium Verification Checklist

1. **Registration & Password Hashing**: Register a new farmer in **Register** → saved in MySQL `farmers` with `pbkdf2:sha256` hash; duplicate email/phone rejected (`409`).
2. **Login & Protected Dashboard**: Log in → redirected to **Dashboard** showing farmer details, farm size, soil type, counters, and local weather. Unauthenticated requests to `/api/dashboard` return `401`.
3. **Logout Confirmation**: Click **Logout** → confirmation screen → ends session cleanly.
4. **Crop Recommendation**: Enter N, P, K, pH, and District → executes `crop_model.pkl`, displays predicted crop + confidence + NPK summary, and persists to `soil_test`.
5. **Plant Disease Detection**: Upload leaf image → preview & validate → executes `disease_model.h5`, displays crop type, disease, confidence, description, and treatment, and saves image & row to `disease_history`.
6. **Market Prices**: Filter by district, search crops/districts, sort by date or price from MySQL `crop_prices`.
7. **Live + Historical Weather**: Toggle **Live (Open-Meteo)** and **Historical (MySQL)** and filter districts.
8. **Bilingual Toggle**: Switch between **English** and **தமிழ்**; choice persists across reloads via `localStorage`.

---

## 5. Run Automated Tests
```bash
python -m unittest discover -s tests -v
```
