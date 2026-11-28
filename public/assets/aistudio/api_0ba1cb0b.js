/**
 * Smart Agri AI — API Service Layer
 * Place this file next to index.html (inside templates/ folder)
 * Add <script src="api.js"></script> BEFORE your main script block in index.html
 *
 * All methods return a Promise that resolves to the JSON response data.
 * Errors are thrown so callers can catch them and showToast().
 */

const API_BASE = "";   // Change in production

const apiService = (() => {

  /* ── Internal fetch helper ─────────────────────────────────────── */
  async function _post(endpoint, bodyObj) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyObj),
    });
    const json = await res.json();
    if (!res.ok || !json.success) {
      throw new Error(json.error || `HTTP ${res.status}`);
    }
    return json;
  }

  async function _postForm(endpoint, formData) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      body: formData,          // browser sets multipart content-type automatically
    });
    const json = await res.json();
    if (!res.ok || !json.success) {
      throw new Error(json.error || `HTTP ${res.status}`);
    }
    return json;
  }

  async function _get(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    const json = await res.json();
    if (!res.ok || !json.success) {
      throw new Error(json.error || `HTTP ${res.status}`);
    }
    return json;
  }

  /* ── Public API ────────────────────────────────────────────────── */

  /**
   * POST /api/crop/predict
   * @param {Object} soilData  { nitrogen, phosphorus, potassium, ph, district }
   * @returns {Promise<{crop_name, crop_name_ta, confidence, description_en,
   *                    description_ta, icon, yield_estimate}>}
   */
  async function predictCrop(soilData) {
    const json = await _post("/api/crop/predict", soilData);
    return json.data;
  }

  /**
   * POST /api/disease/detect
   * @param {File} imageFile  File object from <input type="file">
   * @returns {Promise<{disease_name, disease_name_ta, severity, confidence,
   *                    crop_name, crop_name_ta, treatment_en, treatment_ta}>}
   */
  async function detectDisease(imageFile) {
    const fd = new FormData();
    fd.append("image", imageFile);
    const json = await _postForm("/api/disease/detect", fd);
    return json.data;
  }

  /**
   * GET /api/market/prices?district=All
   * @param {string} district  District name or "All"
   * @returns {Promise<Array<{crop, crop_ta, price, district, change, up, date}>>}
   */
  async function getMarketPrices(district = "All") {
    const qs = district && district !== "All" ? `?district=${encodeURIComponent(district)}` : "";
    const json = await _get(`/api/market/prices${qs}`);
    return json.data;
  }

  /**
   * GET /api/weather/data
   * @returns {Promise<Array<{district, condition, condition_name, condition_ta,
   *                          temp, feels, humidity, rainfall, wind,
   *                          advisory_en, advisory_ta}>>}
   */
  async function getWeatherData() {
    const json = await _get("/api/weather/data");
    return json.data;
  }

  return { predictCrop, detectDisease, getMarketPrices, getWeatherData };
})();