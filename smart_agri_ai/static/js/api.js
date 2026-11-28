/**
 * Smart Agri AI — API Service Layer
 * Connects Vanilla JS frontend to Flask backend endpoints with CSRF protection,
 * credentialed session cookies, JSON handling, and FormData file uploads.
 */

const API_BASE = "";

const apiService = (() => {
  let _csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
  let _previewSession = document.querySelector('meta[name="preview-session"]')?.getAttribute("content") || "";

  async function refreshCsrfToken() {
    const res = await fetch(`${API_BASE}/api/csrf-token`, {
      credentials: "same-origin",
      cache: "no-store",
      headers: _previewSession ? { "X-Preview-Session": _previewSession } : {},
    });
    const json = await res.json();
    if (json?.csrf_token) _csrfToken = json.csrf_token;
    if (json?.preview_session) _previewSession = json.preview_session;
    return _csrfToken;
  }

  async function ensureCsrfToken() {
    if (_csrfToken) return _csrfToken;
    return refreshCsrfToken();
  }

  function setCsrfToken(token) {
    if (token) _csrfToken = token;
  }

  function _baseHeaders(extra = {}) {
    const h = { ...extra };
    if (_previewSession) {
      h["X-Preview-Session"] = _previewSession;
    }
    return h;
  }

  async function _handleResponse(res) {
    let json = null;
    try {
      json = await res.json();
    } catch {
      if (res.status === 403) {
        throw new Error("Session verification failed (HTTP 403). Please reload the page and try again.");
      }
      throw new Error(`Server returned invalid response (HTTP ${res.status})`);
    }
    if (json && json.csrf_token) {
      _csrfToken = json.csrf_token;
    }
    if (json && json.preview_session) {
      _previewSession = json.preview_session;
    }
    if (!res.ok || !json.success) {
      const err = new Error(json?.error || `Request failed (HTTP ${res.status})`);
      err.status = res.status;
      err.loginRequired = Boolean(json?.login_required || res.status === 401);
      throw err;
    }
    return json;
  }

  async function _get(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "GET",
      credentials: "same-origin",
      headers: _baseHeaders(),
    });
    return _handleResponse(res);
  }

  async function _post(endpoint, bodyObj, retried = false) {
    const token = await ensureCsrfToken();
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      credentials: "same-origin",
      headers: _baseHeaders({
        "Content-Type": "application/json",
        "X-CSRF-Token": token,
      }),
      body: JSON.stringify(bodyObj),
    });
    if (res.status === 403 && !retried) {
      await refreshCsrfToken().catch(() => {});
      return _post(endpoint, bodyObj, true);
    }
    return _handleResponse(res);
  }

  async function _postForm(endpoint, formData, retried = false) {
    const token = await ensureCsrfToken();
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      credentials: "same-origin",
      headers: _baseHeaders({
        "X-CSRF-Token": token,
      }),
      body: formData,
    });
    if (res.status === 403 && !retried) {
      await refreshCsrfToken().catch(() => {});
      return _postForm(endpoint, formData, true);
    }
    return _handleResponse(res);
  }

  /* ── Auth & Session ───────────────────────────────────────────── */
  async function getMe() {
    return _get("/api/auth/me");
  }

  async function register(payload) {
    if (payload instanceof FormData) {
      return _postForm("/api/auth/register", payload);
    }
    return _post("/api/auth/register", payload);
  }

  async function login(payload) {
    return _post("/api/auth/login", payload);
  }

  async function logout() {
    return _post("/api/auth/logout", {});
  }

  /* ── Dashboard & History ──────────────────────────────────────── */
  async function getDashboard() {
    const json = await _get("/api/dashboard");
    return json.data;
  }

  async function getSoilTests() {
    const json = await _get("/api/soil-tests");
    return json.data;
  }

  async function getDiseaseHistory() {
    const json = await _get("/api/disease-history");
    return json.data;
  }

  /* ── ML & CNN Endpoints ───────────────────────────────────────── */
  async function predictCrop(soilData) {
    const json = await _post("/api/crop/predict", soilData);
    return json.data;
  }

  async function detectDisease(imageFile) {
    const fd = new FormData();
    fd.append("image", imageFile);
    const json = await _postForm("/api/disease/detect", fd);
    return json.data;
  }

  async function searchCrops(query = "") {
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return _get(`/api/crops/search${qs}`);
  }

  /* ── Market Prices & Weather ──────────────────────────────────── */
  async function getMarketPrices({ district = "All", search = "", sort = "date_desc" } = {}) {
    const params = new URLSearchParams();
    if (district && district !== "All") params.set("district", district);
    if (search) params.set("search", search);
    if (sort) params.set("sort", sort);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return _get(`/api/market-prices${qs}`);
  }

  async function getWeatherData({ district = "All", mode = "all" } = {}) {
    const params = new URLSearchParams();
    if (district && district !== "All") params.set("district", district);
    if (mode) params.set("mode", mode);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return _get(`/api/weather${qs}`);
  }

  return {
    setCsrfToken,
    ensureCsrfToken,
    getMe,
    register,
    login,
    logout,
    getDashboard,
    getSoilTests,
    getDiseaseHistory,
    predictCrop,
    detectDisease,
    searchCrops,
    getMarketPrices,
    getWeatherData,
  };
})();
