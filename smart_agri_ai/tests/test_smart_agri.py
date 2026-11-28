"""
Smart Agri AI — Verification & Regression Test Suite
Verifies Python syntax, SQL schema integrity, bilingual crop & disease catalogs,
frontend-backend bindings, and optional live Flask endpoint tests when Flask/MySQL
packages are available.
"""

import csv
import os
import py_compile
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SmartAgriStaticVerificationTests(unittest.TestCase):
    """Tests that run with Python standard library across any environment."""

    def test_python_files_compile_cleanly(self):
        py_files = [
            "app.py",
            "config.py",
            "database.py",
            "agro_catalog.py",
        ]
        for rel in py_files:
            full_path = os.path.join(BASE_DIR, rel)
            self.assertTrue(os.path.exists(full_path), f"Missing {rel}")
            py_compile.compile(full_path, doraise=True)

    def test_schema_sql_contains_all_required_tables_and_keys(self):
        schema_path = os.path.join(BASE_DIR, "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as fh:
            sql = fh.read()

        required_tables = [
            "farmers",
            "soil_test",
            "disease_history",
            "crop_prices",
            "weather_data",
        ]
        for tbl in required_tables:
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {tbl}", sql)

        self.assertIn("FOREIGN KEY (farmer_id) REFERENCES farmers(id)", sql)
        self.assertIn("UNIQUE KEY uq_farmers_email", sql)
        self.assertIn("UNIQUE KEY uq_farmers_phone", sql)

    def test_catalog_covers_all_ml_and_market_crops(self):
        from agro_catalog import CROP_CATALOG, DISEASE_DB, DISTRICT_COORDS

        crop_csv = os.path.join(BASE_DIR, "crop_data.csv")
        with open(crop_csv, "r", encoding="utf-8") as fh:
            ml_crops = {row["label"].strip().lower() for row in csv.DictReader(fh) if row.get("label")}

        for crop in ml_crops:
            self.assertIn(crop, CROP_CATALOG, f"Missing ML crop '{crop}' in CROP_CATALOG")
            entry = CROP_CATALOG[crop]
            self.assertTrue(entry.get("name_en"))
            self.assertTrue(entry.get("name_ta"))
            self.assertTrue(entry.get("desc_en"))
            self.assertTrue(entry.get("desc_ta"))

        market_csv = os.path.join(BASE_DIR, "market_data.csv")
        with open(market_csv, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            market_crops = set()
            market_districts = set()
            for idx, row in enumerate(reader):
                if row.get("crop"):
                    market_crops.add(row["crop"].strip().lower())
                if row.get("district"):
                    market_districts.add(row["district"].strip())
                if idx > 5000:
                    break

        for mcrop in market_crops:
            self.assertIn(mcrop, CROP_CATALOG, f"Missing market crop '{mcrop}' in CROP_CATALOG")
        for dist in market_districts:
            self.assertIn(dist, DISTRICT_COORDS, f"Missing district '{dist}' in DISTRICT_COORDS")

        self.assertGreaterEqual(len(DISEASE_DB), 38)
        for key, info in DISEASE_DB.items():
            self.assertIn("disease_name", info, key)
            self.assertIn("disease_name_ta", info, key)
            self.assertIn("treatment_en", info, key)
            self.assertIn("treatment_ta", info, key)

    def test_frontend_i18n_keys_and_button_ids_valid(self):
        html_path = os.path.join(BASE_DIR, "templates", "index.html")
        tr_path = os.path.join(BASE_DIR, "static", "js", "translations.js")
        api_path = os.path.join(BASE_DIR, "static", "js", "api.js")

        with open(html_path, "r", encoding="utf-8") as fh:
            html = fh.read()
        with open(tr_path, "r", encoding="utf-8") as fh:
            tr_js = fh.read()
        with open(api_path, "r", encoding="utf-8") as fh:
            api_js = fh.read()

        # Verify explicit IDs exist for Crop and Disease action buttons & Crop Lookup panel
        self.assertIn('id="cropPredictBtn"', html)
        self.assertIn('id="diseaseDetectBtn"', html)
        self.assertIn('id="cropDetailsSearchInput"', html)
        self.assertIn('id="cropDetailDisplay"', html)
        self.assertIn('document.getElementById("cropPredictBtn")', html)
        self.assertIn('document.getElementById("diseaseDetectBtn")', html)

        # Verify CSRF header, credentialed fetch, and searchCrops endpoint binding
        self.assertIn("X-CSRF-Token", api_js)
        self.assertIn('credentials: "same-origin"', api_js)
        self.assertIn("/api/crops/search", api_js)

        # Verify every data-i18n attribute key is defined in translations.js
        keys_in_html = set(re.findall(r'data-i18n(?:-placeholder)?="([^"]+)"', html))
        for k in keys_in_html:
            self.assertRegex(
                tr_js,
                rf"\b{re.escape(k)}\s*:",
                f"Translation key '{k}' missing from translations.js",
            )

        # Verify registration FormData & real-time validation hooks
        self.assertIn('id="regSubmitBtn"', html)
        self.assertIn('id="regPasswordChecklist"', html)
        self.assertIn("new FormData()", html)
        self.assertIn("_postForm(\"/api/auth/register\"", api_js)
        for rk in ("val_email_err", "val_email_ok", "pw_rule_len", "pw_rule_upper", "pw_rule_special"):
            self.assertRegex(tr_js, rf"\b{rk}\s*:", f"Missing validation i18n key '{rk}'")

    def test_no_hardcoded_fake_predictions_in_backend(self):
        app_path = os.path.join(BASE_DIR, "app.py")
        with open(app_path, "r", encoding="utf-8") as fh:
            src = fh.read()

        self.assertIn("if crop_model is None:", src)
        self.assertIn("if disease_model is None or class_indices is None:", src)
        self.assertIn("_extract_auth_payload", src)
        self.assertIn("is_password_complex", src)
        self.assertIn("IntegrityError", src)
        self.assertNotIn("MOCK_MARKET", src)
        self.assertNotIn("MOCK_WEATHER", src)


try:
    import flask  # noqa: F401
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


@unittest.skipUnless(HAS_FLASK, "Flask runtime packages not installed in this container")
class SmartAgriFlaskEndpointTests(unittest.TestCase):
    """Runs Flask test-client API checks when Flask & dependencies are installed."""

    def setUp(self):
        import app as flask_app

        self.client = flask_app.app.test_client()

    def test_csrf_token_and_health_route(self):
        res = self.client.get("/api/csrf-token")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["csrf_token"])

        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertIn("models", health.get_json())

    def test_protected_routes_require_login(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
