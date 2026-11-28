/**
 * ═══════════════════════════════════════════════════════════════════════════
 *  Smart Agri AI — index.html JS REPLACEMENTS
 *  Copy each function below and REPLACE the matching function in index.html.
 *  Everything else in the <script> block stays exactly the same.
 *
 *  PREREQUISITE: Add this line to <head> BEFORE the closing </head> tag:
 *    <script src="api.js"></script>
 * ═══════════════════════════════════════════════════════════════════════════
 */


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 1 — predictCrop()
   Old function used hardcoded if/else logic.
   New function calls the Flask API and updates the same DOM IDs.
═══════════════════════════════════════════════════════════ */
async function predictCrop() {
  const n    = parseFloat(document.getElementById("inp_n").value);
  const p    = parseFloat(document.getElementById("inp_p").value);
  const k    = parseFloat(document.getElementById("inp_k").value);
  const ph   = parseFloat(document.getElementById("inp_ph").value);
  const dist = document.getElementById("inp_district").value;

  // Validation
  if (isNaN(n) || isNaN(p) || isNaN(k) || isNaN(ph) || !dist) {
    showToast(t("toast_error"), "error");
    return;
  }

  // Loading state
  const btn = document.querySelector(".btn-predict");
  const originalText = btn.textContent;
  btn.textContent = currentLang === "ta" ? "⏳ கணிக்கிறது..." : "⏳ Predicting...";
  btn.disabled = true;

  try {
    // API call
    const data = await apiService.predictCrop({
      nitrogen:    n,
      phosphorus:  p,
      potassium:   k,
      ph:          ph,
      district:    dist,
    });

    // Update DOM
    document.getElementById("res_icon").textContent    = data.icon;
    document.getElementById("res_name").textContent    = data.crop_name;
    document.getElementById("res_conf_pct").textContent = data.confidence + "%";
    document.getElementById("res_desc").textContent    =
      currentLang === "ta" ? data.description_ta : data.description_en;

    // Hide placeholder, show result card
    document.getElementById("crop-placeholder").style.display = "none";
    const rc = document.getElementById("crop-result");
    rc.classList.add("show");

    // Animate confidence bar
    setTimeout(() => {
      document.getElementById("conf_bar").style.width = data.confidence + "%";
    }, 100);

    // Toast
    const msg = currentLang === "ta"
      ? `✅ பயிர்: ${data.crop_name_ta}`
      : `✅ Crop: ${data.crop_name}`;
    showToast(msg, "success");

  } catch (err) {
    console.error("predictCrop API error:", err);
    showToast(
      currentLang === "ta"
        ? "❌ பிழை ஏற்பட்டது"
        : "❌ Error: " + err.message,
      "error"
    );
  } finally {
    // Restore button
    btn.textContent = originalText;
    btn.disabled = false;
  }
}


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 2 — detectDisease()
   Old function used Math.random() on a hardcoded array.
   New function sends the actual uploaded file to the API.
═══════════════════════════════════════════════════════════ */
async function detectDisease() {
  // Guard: image must be uploaded
  const fileInput = document.getElementById("fileInput");
  if (!hasImage || !fileInput.files[0]) {
    showToast(t("toast_no_image"), "error");
    return;
  }

  // Loading state
  const btn = document.querySelector(".btn-detect");
  const originalText = btn.textContent;
  btn.textContent = currentLang === "ta" ? "⏳ கண்டறிகிறது..." : "⏳ Detecting...";
  btn.disabled = true;

  try {
    // API call
    const data = await apiService.detectDisease(fileInput.files[0]);

    // Show result
    document.getElementById("disease-placeholder").style.display = "none";
    const dr = document.getElementById("disease-result");

    // Disease name
    document.getElementById("dis_name").textContent =
      currentLang === "ta" ? data.disease_name_ta : data.disease_name;

    // Severity badge
    const sb = document.getElementById("dis_severity");
    const sevMap = {
      high:   { cls: "sev-high", en: "⚠ High Severity",   ta: "⚠ அதிக தீவிரம்"     },
      medium: { cls: "sev-med",  en: "⚡ Medium Severity", ta: "⚡ நடுத்தர தீவிரம்"  },
      low:    { cls: "sev-low",  en: "✅ Low Severity",    ta: "✅ குறைந்த தீவிரம்" },
    };
    const sev = sevMap[data.severity] || sevMap.medium;
    sb.className   = "severity-badge " + sev.cls;
    sb.textContent = currentLang === "ta" ? sev.ta : sev.en;

    // Other fields
    document.getElementById("dis_conf").textContent = data.confidence + "%";
    document.getElementById("dis_crop").textContent =
      currentLang === "ta" ? data.crop_name_ta : data.crop_name;
    document.getElementById("dis_treatment_text").textContent =
      currentLang === "ta" ? data.treatment_ta : data.treatment_en;

    dr.classList.add("show");
    showToast(t("toast_detected"), "success");

  } catch (err) {
    console.error("detectDisease API error:", err);
    showToast(
      currentLang === "ta"
        ? "❌ நோய் கண்டறிய முடியவில்லை"
        : "❌ Detection failed",
      "error"
    );
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 3 — filterMarket() + searchMarket()
═══════════════════════════════════════════════════════════ */

// Keep this exactly as-is:
function renderMarketTable(data) {
  const tbody = document.getElementById("marketTableBody");
  if (!tbody) return;
  tbody.innerHTML = data.map(r => `
    <tr>
      <td><div class="crop-flag"><div class="crop-dot"></div>${currentLang === "ta" ? r.crop_ta : r.crop}</div></td>
      <td><strong>₹${Number(r.price).toLocaleString()}</strong></td>
      <td>${r.district}</td>
      <td class="${r.up ? "price-up" : "price-down"}">${r.up ? "↑" : "↓"} ${r.change}</td>
      <td style="color:var(--text-muted)">${r.date}</td>
    </tr>`).join("");
}

// REPLACE filterMarket with this API version:
async function filterMarket(dist, el) {
  activeDistrict = dist;
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  el.classList.add("active");

  const tbody = document.getElementById("marketTableBody");
  if (tbody) tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:2rem;color:var(--text-muted)">${currentLang === "ta" ? "⏳ தரவு ஏற்றுகிறது..." : "⏳ Loading..."}</td></tr>`;

  try {
    const data = await apiService.getMarketPrices(dist);
    const search = document.getElementById("marketSearch")?.value?.toLowerCase() || "";
    const filtered = search
      ? data.filter(r => r.crop.toLowerCase().includes(search) || r.crop_ta.includes(search))
      : data;
    renderMarketTable(filtered);
  } catch (err) {
    renderMarketTable(marketData);
  }
}

// REPLACE searchMarket with this version:
async function searchMarket(val) {
  try {
    const data = await apiService.getMarketPrices(activeDistrict);
    const filtered = data.filter(r =>
      r.crop.toLowerCase().includes(val.toLowerCase()) ||
      r.crop_ta.includes(val)
    );
    renderMarketTable(filtered);
  } catch (err) {
    const filtered = marketData.filter(r =>
      (activeDistrict === "All" || r.district === activeDistrict) &&
      (r.crop.toLowerCase().includes(val.toLowerCase()) || r.crop_ta.includes(val))
    );
    renderMarketTable(filtered);
  }
}


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 4 — renderWeather()
═══════════════════════════════════════════════════════════ */
async function renderWeather() {
  let weatherArr;
  try {
    weatherArr = await apiService.getWeatherData();
  } catch (err) {
    weatherArr = typeof weatherData !== "undefined" ? weatherData : [];
  }

  const wc = document.getElementById("weatherCards");
  const wt = document.getElementById("weatherTableBody");
  if (!wc || !wt) return;

  const featured = weatherArr.slice(0, 3);
  wc.innerHTML = featured.map(w => `
    <div class="weather-card">
      <div class="wc-district">${w.district}</div>
      <div class="wc-condition">${w.condition}</div>
      <div class="wc-temp">${w.temp}°C</div>
      <div class="wc-feels">${currentLang === "ta" ? "உணர்வு நிலை" : "Feels like"} ${w.feels}°C</div>
      <div class="wc-stats">
        <div class="wcs-item"><label>${currentLang === "ta" ? "ஈரப்பதம்" : "Humidity"}</label><span>${w.humidity}%</span></div>
        <div class="wcs-item"><label>${currentLang === "ta" ? "மழை" : "Rainfall"}</label><span>${w.rainfall} mm</span></div>
        <div class="wcs-item"><label>${currentLang === "ta" ? "காற்று" : "Wind"}</label><span>${w.wind} km/h</span></div>
        <div class="wcs-item"><label>${currentLang === "ta" ? "நிலை" : "Status"}</label><span style="color:var(--green-light)">${currentLang === "ta" ? w.condition_ta : w.condition_name}</span></div>
      </div>
    </div>`).join("");

  wt.innerHTML = weatherArr.map(w => `
    <tr>
      <td style="font-weight:600">${w.district}</td>
      <td><div class="w-condition-cell">${w.condition} ${currentLang === "ta" ? w.condition_ta : w.condition_name}</div></td>
      <td>${w.temp}°C</td>
      <td>${w.humidity}%</td>
      <td>${w.rainfall} mm</td>
      <td>${w.wind} km/h</td>
      <td style="font-size:.8rem">${currentLang === "ta" ? w.advisory_ta : w.advisory_en}</td>
    </tr>`).join("");
}


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 5 — DOMContentLoaded
═══════════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", async () => {
  initFadeUp();
  try {
    const mdata = await apiService.getMarketPrices("All");
    renderMarketTable(mdata);
  } catch (_) {
    renderMarketTable(marketData);
  }
  await renderWeather();
});


/* ═══════════════════════════════════════════════════════════
   REPLACEMENT 6 — toggleLang()
═══════════════════════════════════════════════════════════ */
async function toggleLang() {
  currentLang = currentLang === "en" ? "ta" : "en";
  document.getElementById("langLabel").textContent = currentLang === "en" ? "தமிழ்" : "English";
  document.getElementById("mobileLangBtn").textContent = currentLang === "en" ? "தமிழ்க்கு மாறு" : "Switch to English";
  applyTranslations();

  try {
    const mdata = await apiService.getMarketPrices(activeDistrict || "All");
    renderMarketTable(mdata);
  } catch (_) {
    renderMarketTable(marketData);
  }
  await renderWeather();

  showToast(
    currentLang === "ta" ? "தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது" : "English selected",
    "info"
  );
}