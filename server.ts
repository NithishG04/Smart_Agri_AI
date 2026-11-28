/**
 * Smart Agri AI — Express Preview & Verification Server (Port 3000)
 * Serves the preserved Vanilla HTML5/CSS3/JS frontend from smart_agri_ai/
 * and mirrors the Flask REST API contract for live preview in AI Studio.
 * Full MySQL + Scikit-learn (crop_model.pkl) + TensorFlow/Keras (disease_model.h5)
 * execution runs via smart_agri_ai/app.py.
 */

import "dotenv/config";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import express, { NextFunction, Request, Response } from "express";
import multer from "multer";
import { GoogleGenAI, Type } from "@google/genai";

const PORT = 3000;
const SMART_AGRI_DIR = path.resolve(process.cwd(), "smart_agri_ai");
const TEMPLATE_PATH = path.join(SMART_AGRI_DIR, "templates", "index.html");
const STATIC_DIR = path.join(SMART_AGRI_DIR, "static");
const MARKET_CSV_PATH = path.join(SMART_AGRI_DIR, "market_data.csv");
const CROP_DATA_CSV_PATH = path.join(SMART_AGRI_DIR, "crop_data.csv");
const DISEASE_CATALOG_PATH = path.join(SMART_AGRI_DIR, "disease_catalog.json");
const PREVIEW_DB_PATH = path.join(SMART_AGRI_DIR, "smart_agri_preview.db");
const UPLOAD_DIR = path.resolve(SMART_AGRI_DIR, "uploads");

interface FarmerRecord {
  id: number;
  name: string;
  email: string;
  phone: string;
  farm_location: string;
  farm_size: number;
  soil_type: string;
  passwordHash: string;
  created_at: string;
}

interface SessionData {
  id: string;
  csrfToken: string;
  farmerId?: number;
}

interface MarketPriceRow {
  id: number;
  crop: string;
  crop_ta: string;
  price: number;
  previous_price: number;
  district: string;
  change: string;
  change_amount: number;
  up: boolean;
  date: string;
}

interface WeatherRow {
  district: string;
  condition: string;
  condition_name: string;
  condition_ta: string;
  temp: number;
  feels: number;
  humidity: number;
  rainfall: number;
  wind: number;
  advisory_en: string;
  advisory_ta: string;
  source: string;
  is_live: boolean;
  date: string;
}

interface SoilTestRecord {
  id: number;
  farmer_id: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  ph: number;
  district: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  confidence: number;
  recommendation: string;
  recommendation_ta: string;
  icon: string;
  date: string;
}

interface CropSampleRow {
  features: number[];
  label: string;
}

interface DiseaseCatalogEntry {
  disease_name: string;
  disease_name_ta: string;
  severity: "low" | "medium" | "high";
  crop_name: string;
  crop_name_ta: string;
  description_en: string;
  description_ta: string;
  treatment_en: string;
  treatment_ta: string;
}

interface DiseaseRecord {
  id: number;
  farmer_id: number;
  crop_type: string;
  disease_name: string;
  confidence: number;
  severity: "low" | "medium" | "high";
  image_filename: string;
  treatment: string;
  date: string;
}

interface StoredUploadImage {
  farmerId: number;
  mimeType: string;
  buffer: Buffer;
}

interface AuthenticatedRequest extends Request {
  farmer?: FarmerRecord;
}

const CROP_TAMIL_MAP: Record<string, string> = {
  rice: "நெல் (அரிசி)",
  maize: "மக்காச்சோளம்",
  cotton: "பருத்தி",
  sugarcane: "கரும்பு",
  turmeric: "மஞ்சள்",
  groundnut: "நிலக்கடலை",
  banana: "வாழை",
  coconut: "தேங்காய்",
  tomato: "தக்காளி",
  onion: "வெங்காயம்",
  chilli: "மிளகாய்",
  ragi: "கேழ்வரகு",
  blackgram: "உளுந்து",
  greengram: "பச்சைப் பயறு",
  sesame: "எள்",
  mango: "மாம்பழம்",
  potato: "உருளைக்கிழங்கு",
  soybean: "சோயாபீன்ஸ்",
  sunflower: "சூரியகாந்தி",
  wheat: "கோதுமை",
};

const DISTRICT_COORDS: Record<string, [number, number]> = {
  Thanjavur: [10.787, 79.1378],
  Coimbatore: [11.0168, 76.9558],
  Madurai: [9.9252, 78.1198],
  Salem: [11.6643, 78.146],
  Trichy: [10.7905, 78.7047],
  Vellore: [12.9165, 79.1325],
  Tirunelveli: [8.7139, 77.7567],
  Erode: [11.341, 77.7172],
  Dindigul: [10.3624, 77.9695],
  Chennai: [13.0827, 80.2707],
  Cuddalore: [11.748, 79.7714],
  Kancheepuram: [12.8342, 79.7036],
  Karur: [10.9601, 78.0766],
  Krishnagiri: [12.5186, 78.2137],
  Virudhunagar: [9.568, 77.9624],
};

const WMO_WEATHER_MAP: Record<number, [string, string, string]> = {
  0: ["☀️", "Clear Sky", "தெளிவான வானம்"],
  1: ["🌤️", "Mainly Clear", "பெரும்பாலும் தெளிவு"],
  2: ["⛅", "Partly Cloudy", "பகுதியளவு மேகமூட்டம்"],
  3: ["☁️", "Overcast", "மேகமூட்டம்"],
  45: ["🌫️", "Foggy", "மூடுபனி"],
  51: ["🌦️", "Light Drizzle", "லேசான தூறல்"],
  61: ["🌦️", "Light Rain", "லேசான மழை"],
  63: ["🌧️", "Moderate Rain", "மிதமான மழை"],
  65: ["🌧️", "Heavy Rain", "கனமழை"],
  80: ["🌦️", "Rain Showers", "மழைத் தூறல்"],
  95: ["⛈️", "Thunderstorm", "இடியுடன் மழை"],
};

function buildAdvisory(temp: number, humidity: number, rainfall: number): [string, string] {
  if (rainfall >= 8) {
    return [
      "Heavy rain alert: ensure field drainage and postpone fertilizer or pesticide spraying.",
      "கனமழை எச்சரிக்கை: வயலில் நீர் வடிய ஏற்பாடு செய்து உரம்/மருந்து தெளிப்பை ஒத்திவைக்கவும்.",
    ];
  }
  if (temp >= 35) {
    return [
      "High heat: irrigate early morning or late evening and apply crop mulching.",
      "அதிக வெப்பம்: காலை அல்லது மாலையில் நீர்ப்பாசனம் செய்து மூடாக்கு இடவும்.",
    ];
  }
  if (humidity >= 80) {
    return [
      "High humidity increases fungal risk: inspect leaves closely for early blight or mildew.",
      "அதிக ஈரப்பதம் பூஞ்சை நோயை தூண்டும்: இலைகளை கவனமாக பரிசோதிக்கவும்.",
    ];
  }
  return [
    "Favorable field conditions for sowing, weeding, and nutrient application.",
    "விதைப்பு, களையெடுப்பு மற்றும் உரமிடுதலுக்கு உகந்த வானிலை.",
  ];
}

// ─── PERSISTENT SQLITE PREVIEW DATABASE (FOR EXPRESS PREVIEW RUNTIME) ─────────
fs.mkdirSync(UPLOAD_DIR, { recursive: true });
const db = new DatabaseSync(PREVIEW_DB_PATH);
db.exec(`
  PRAGMA journal_mode = WAL;
  PRAGMA foreign_keys = ON;

  CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL UNIQUE,
    farm_location TEXT NOT NULL,
    farm_size REAL NOT NULL,
    soil_type TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    csrf_token TEXT NOT NULL,
    farmer_id INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
    updated_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS soil_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    nitrogen REAL NOT NULL,
    phosphorus REAL NOT NULL,
    potassium REAL NOT NULL,
    ph REAL NOT NULL,
    district TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    rainfall REAL NOT NULL,
    confidence REAL NOT NULL,
    recommendation TEXT NOT NULL,
    recommendation_ta TEXT NOT NULL,
    icon TEXT NOT NULL,
    date TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS disease_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    crop_type TEXT NOT NULL,
    disease_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    severity TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    treatment TEXT NOT NULL,
    date TEXT NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_soil_farmer_date ON soil_test(farmer_id, date DESC, id DESC);
  CREATE INDEX IF NOT EXISTS idx_disease_farmer_date ON disease_history(farmer_id, date DESC, id DESC);
  CREATE INDEX IF NOT EXISTS idx_disease_img ON disease_history(image_filename);
`);

function getOrCreateSigningSecret(): Buffer {
  const envSecret = process.env.SESSION_SECRET?.trim();
  if (envSecret && envSecret.length >= 16) {
    return crypto.createHash("sha256").update(envSecret).digest();
  }
  const existing = db
    .prepare("SELECT value FROM app_meta WHERE key = 'session_signing_secret'")
    .get() as { value: string } | undefined;
  if (existing?.value) {
    return Buffer.from(existing.value, "hex");
  }
  const generated = crypto.randomBytes(32);
  db.prepare(
    "INSERT OR REPLACE INTO app_meta (key, value) VALUES ('session_signing_secret', ?)"
  ).run(generated.toString("hex"));
  return generated;
}

function mapFarmerRow(row: Record<string, unknown> | undefined): FarmerRecord | null {
  if (!row) return null;
  return {
    id: Number(row.id),
    name: String(row.name),
    email: String(row.email),
    phone: String(row.phone),
    farm_location: String(row.farm_location),
    farm_size: Number(row.farm_size),
    soil_type: String(row.soil_type),
    passwordHash: String(row.password_hash),
    created_at: String(row.created_at),
  };
}

function getFarmerById(id: number): FarmerRecord | null {
  const row = db
    .prepare(
      "SELECT id, name, email, phone, farm_location, farm_size, soil_type, password_hash, created_at FROM farmers WHERE id = ?"
    )
    .get(id) as Record<string, unknown> | undefined;
  return mapFarmerRow(row);
}

function getFarmerByEmail(email: string): FarmerRecord | null {
  const row = db
    .prepare(
      "SELECT id, name, email, phone, farm_location, farm_size, soil_type, password_hash, created_at FROM farmers WHERE LOWER(email) = LOWER(?)"
    )
    .get(email) as Record<string, unknown> | undefined;
  return mapFarmerRow(row);
}

function loadDiseaseCatalog(): {
  diseases: Record<string, DiseaseCatalogEntry>;
  defaultEntry: DiseaseCatalogEntry;
} {
  const fallbackDefault: DiseaseCatalogEntry = {
    disease_name: "Unknown Condition",
    disease_name_ta: "அறியப்படாத நிலை",
    severity: "medium",
    crop_name: "Unknown Crop",
    crop_name_ta: "அறியப்படாத பயிர்",
    description_en: "Detected condition is not in the detailed advisory table; consult a local agricultural specialist.",
    description_ta: "கண்டறியப்பட்ட நிலை விரிவான ஆலோசனை அட்டவணையில் இல்லை; உள்ளூர் வேளாண் அதிகாரியை அணுகவும்.",
    treatment_en: "Please consult your local agricultural extension officer for proper diagnosis and treatment recommendations.",
    treatment_ta: "சரியான நோயறிதல் மற்றும் சிகிச்சை பரிந்துரைகளுக்கு உங்கள் உள்ளூர் விவசாய விரிவாக்க அதிகாரியை அணுகவும்.",
  };
  if (!fs.existsSync(DISEASE_CATALOG_PATH)) {
    return { diseases: {}, defaultEntry: fallbackDefault };
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(DISEASE_CATALOG_PATH, "utf-8")) as {
      diseases?: Record<string, DiseaseCatalogEntry>;
      default?: DiseaseCatalogEntry;
    };
    return {
      diseases: parsed.diseases ?? {},
      defaultEntry: parsed.default ?? fallbackDefault,
    };
  } catch {
    return { diseases: {}, defaultEntry: fallbackDefault };
  }
}

const { diseases: DISEASE_CATALOG, defaultEntry: DEFAULT_DISEASE_ENTRY } = loadDiseaseCatalog();
const DISEASE_CLASS_KEYS = Object.keys(DISEASE_CATALOG);

function loadMarketCatalog(): MarketPriceRow[] {
  if (!fs.existsSync(MARKET_CSV_PATH)) return [];
  const raw = fs.readFileSync(MARKET_CSV_PATH, "utf-8");
  const lines = raw.split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const dateIdx = headers.indexOf("date");
  const cropIdx = headers.indexOf("crop");
  const distIdx = headers.indexOf("district");
  const priceIdx = headers.indexOf("price");
  if (dateIdx < 0 || cropIdx < 0 || distIdx < 0 || priceIdx < 0) return [];

  const historyMap = new Map<string, Array<{ date: string; price: number }>>();

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]?.trim();
    if (!line) continue;
    const parts = line.split(",");
    if (parts.length <= Math.max(dateIdx, cropIdx, distIdx, priceIdx)) continue;
    const dt = parts[dateIdx].trim();
    const crop = parts[cropIdx].trim();
    const district = parts[distIdx].trim();
    const price = Number.parseFloat(parts[priceIdx]);
    if (!crop || !district || !dt || Number.isNaN(price)) continue;

    const key = `${crop}|||${district}`;
    const arr = historyMap.get(key) ?? [];
    arr.push({ date: dt, price: Math.round(price * 100) / 100 });
    if (arr.length > 4) {
      arr.sort((a, b) => b.date.localeCompare(a.date));
      historyMap.set(key, arr.slice(0, 2));
    } else {
      historyMap.set(key, arr);
    }
  }

  const out: MarketPriceRow[] = [];
  let rowId = 1;
  for (const [key, entries] of historyMap.entries()) {
    entries.sort((a, b) => b.date.localeCompare(a.date));
    const latest = entries[0];
    const prev = entries[1] ?? latest;
    const diff = Math.round((latest.price - prev.price) * 100) / 100;
    const pct = prev.price > 0 ? Math.round((diff / prev.price) * 1000) / 10 : 0;
    const [crop, district] = key.split("|||");
    out.push({
      id: rowId++,
      crop,
      crop_ta: CROP_TAMIL_MAP[crop.toLowerCase()] ?? crop,
      price: latest.price,
      previous_price: prev.price,
      district,
      change: `${diff >= 0 ? "+" : ""}${pct.toFixed(1)}%`,
      change_amount: diff,
      up: diff >= 0,
      date: latest.date,
    });
  }
  return out;
}

const marketRows = loadMarketCatalog();

interface CropCatalogEntry {
  name_en: string;
  name_ta: string;
  icon: string;
  desc_en: string;
  desc_ta: string;
}

const CROP_DETAILS_CATALOG: Record<string, CropCatalogEntry> = {
  rice: { name_en: "Rice", name_ta: "நெல்", icon: "🌾", desc_en: "Ideal for alluvial and clay-loam soils with high water retention and warm humid conditions.", desc_ta: "அதிக நீர் தேக்கம் கொண்ட வண்டல் மற்றும் களிமண் நிலங்களுக்கு ஏற்றது. வெப்ப ஈரப்பதமான சூழலில் சிறப்பாக வளரும்." },
  maize: { name_en: "Maize", name_ta: "மக்காச்சோளம்", icon: "🌽", desc_en: "Well-suited for fertile, well-drained loamy soils with balanced nitrogen and potassium.", desc_ta: "சமநிலையான நைட்ரஜன் மற்றும் பொட்டாசியம் கொண்ட வளமான, வடிகால் வசதியுள்ள மண்ணிற்கு சிறந்தது." },
  chickpea: { name_en: "Chickpea", name_ta: "கொண்டைக்கடலை", icon: "🫘", desc_en: "Thrives in cooler semi-arid conditions with moderate phosphorus and low rainfall.", desc_ta: "மிதமான பாஸ்பரஸ் மற்றும் குறைந்த மழைப்பொழிவு உள்ள குளிர்ந்த வறண்ட பகுதிகளில் சிறப்பாக வளரும்." },
  kidneybeans: { name_en: "Kidney Beans", name_ta: "ராஜ்மா", icon: "🫘", desc_en: "Prefers well-drained neutral-to-slightly-acidic soil with cool to moderate temperatures.", desc_ta: "நல்ல வடிகால் வசதியுள்ள நடுநிலை முதல் சற்று அமில மண் மற்றும் மிதமான வெப்பநிலையில் நன்கு வளரும்." },
  pigeonpeas: { name_en: "Pigeon Peas", name_ta: "துவரை", icon: "🌿", desc_en: "Drought-tolerant pulse crop suited for red and black soils with moderate rainfall.", desc_ta: "வறட்சியைத் தாங்கும் பருப்பு வகைப் பயிர்; சிவப்பு மற்றும் கரிசல் மண்ணில் சிறப்பாக வளரும்." },
  mothbeans: { name_en: "Moth Beans", name_ta: "மொத்து பயறு", icon: "🌱", desc_en: "Highly drought-resistant legume ideal for arid sandy soils and warm climates.", desc_ta: "வறண்ட மணல் மண் மற்றும் வெப்பமான காலநிலைக்கு ஏற்ற வறட்சி தாங்கும் பயறு வகை." },
  mungbean: { name_en: "Mung Bean", name_ta: "பாசிப்பயறு", icon: "🫛", desc_en: "Short-duration pulse crop suited for warm humid weather and well-drained loamy soils.", desc_ta: "வெப்ப ஈரப்பதமான காலநிலை மற்றும் வடிகால் வசதியுள்ள மண்ணிற்கு ஏற்ற குறுகிய கால பயறு பயிர்." },
  blackgram: { name_en: "Black Gram", name_ta: "உளுந்து", icon: "🫘", desc_en: "Performs well in warm regions and rice-fallow delta soils with balanced NPK.", desc_ta: "நெல் தரிசு நிலங்கள் மற்றும் வெப்ப பகுதிகளில் சமநிலையான NPK உடன் நன்கு விளையும்." },
  lentil: { name_en: "Lentil", name_ta: "மைசூர் பருப்பு", icon: "🫘", desc_en: "Suited for cool, dry conditions and well-drained soils with moderate phosphorus.", desc_ta: "குளிர்ந்த வறண்ட காலநிலை மற்றும் மிதமான பாஸ்பரஸ் உள்ள மண்ணிற்கு ஏற்றது." },
  pomegranate: { name_en: "Pomegranate", name_ta: "மாதுளை", icon: "🍎", desc_en: "Thrives in semi-arid climates with hot summers and well-drained loamy soils.", desc_ta: "வறண்ட வெப்பமான காலநிலை மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் சிறப்பாக விளையும்." },
  banana: { name_en: "Banana", name_ta: "வாழை", icon: "🍌", desc_en: "Requires potassium-rich fertile soil, steady moisture, and warm tropical weather.", desc_ta: "பொட்டாசியம் நிறைந்த வளமான மண், நிலையான ஈரப்பதம் மற்றும் வெப்பமண்டல காலநிலை தேவை." },
  mango: { name_en: "Mango", name_ta: "மாம்பழம்", icon: "🥭", desc_en: "Performs best in deep well-drained alluvial or red loamy soils with warm dry flowering weather.", desc_ta: "ஆழமான வடிகால் வசதியுள்ள வண்டல் அல்லது செம்மண்ணில் பூக்கும் கால வறண்ட வானிலையில் சிறப்பாக வளரும்." },
  grapes: { name_en: "Grapes", name_ta: "திராட்சை", icon: "🍇", desc_en: "Requires potassium-rich sandy loam soil and dry sunny weather for sweet fruit development.", desc_ta: "பொட்டாசியம் செறிந்த மணல் கலந்த மண் மற்றும் இனிமையான பழ வளர்ச்சிக்கு வெயிலான வானிலை தேவை." },
  watermelon: { name_en: "Watermelon", name_ta: "தர்பூசணி", icon: "🍉", desc_en: "Ideal for warm sunny conditions and well-drained sandy loam soils.", desc_ta: "வெப்பமான வெயில் சூழல் மற்றும் வடிகால் வசதியுள்ள மணல் கலந்த மண்ணிற்கு சிறந்தது." },
  muskmelon: { name_en: "Muskmelon", name_ta: "முலாம்பழம்", icon: "🍈", desc_en: "Grows rapidly in warm dry climates with sandy loam soil and good drainage.", desc_ta: "வெப்ப வறண்ட காலநிலை மற்றும் மணல் கலந்த மண்ணில் விரைவாக வளரும்." },
  apple: { name_en: "Apple", name_ta: "ஆப்பிள்", icon: "🍏", desc_en: "Requires cool temperate highland climate and well-drained loamy soil rich in potassium.", desc_ta: "குளிர்ந்த மலைப்பகுதி காலநிலை மற்றும் பொட்டாசியம் நிறைந்த வண்டல் மண் தேவை." },
  orange: { name_en: "Orange", name_ta: "ஆரஞ்சு", icon: "🍊", desc_en: "Suitable for subtropical climates with slightly acidic to neutral well-drained soils.", desc_ta: "மிதவெப்பமண்டல காலநிலை மற்றும் சற்று அமில முதல் நடுநிலை மண்ணிற்கு ஏற்றது." },
  papaya: { name_en: "Papaya", name_ta: "பப்பாளி", icon: "🍈", desc_en: "Fast-growing tropical fruit thriving in warm humid conditions and fertile drained soil.", desc_ta: "வெப்ப ஈரப்பதமான சூழல் மற்றும் வளமான வடிகால் வசதியுள்ள மண்ணில் விரைவாக வளரும்." },
  coconut: { name_en: "Coconut", name_ta: "தேங்காய்", icon: "🥥", desc_en: "Ideal for coastal and tropical humid districts with high rainfall and sandy loam soils.", desc_ta: "கடற்கரை மற்றும் அதிக மழைப்பொழிவு உள்ள ஈரப்பதமான மாவட்டங்களுக்கு மிகவும் ஏற்றது." },
  cotton: { name_en: "Cotton", name_ta: "பருத்தி", icon: "🌸", desc_en: "Thrives in black cotton and deep loamy soils with high nitrogen and warm sunny weather.", desc_ta: "கரிசல் மண் மற்றும் ஆழமான மண்ணில் அதிக நைட்ரஜன் மற்றும் வெயிலான வானிலையில் சிறப்பாக வளரும்." },
  jute: { name_en: "Jute", name_ta: "சணல்", icon: "🌾", desc_en: "Best suited for warm, very humid alluvial plains with abundant rainfall.", desc_ta: "அதிக மழைப்பொழிவு மற்றும் ஈரப்பதம் கொண்ட வெப்பமான வண்டல் சமவெளிகளுக்கு ஏற்றது." },
  coffee: { name_en: "Coffee", name_ta: "காபி", icon: "☕", desc_en: "Suited for cool humid hill tracts with rich organic acidic soils and high rainfall.", desc_ta: "குளிர்ந்த ஈரப்பதமான மலைப்பகுதிகள் மற்றும் கரிம அமில மண்ணிற்கு ஏற்றது." },
  sugarcane: { name_en: "Sugarcane", name_ta: "கரும்பு", icon: "🎋", desc_en: "Long-duration cash crop thriving in fertile alluvial soil with reliable irrigation.", desc_ta: "வளமான வண்டல் மண் மற்றும் நிலையான நீர்ப்பாசனத்துடன் சிறப்பாக விளையும் பணப்பயிர்." },
  groundnut: { name_en: "Groundnut", name_ta: "நிலக்கடலை", icon: "🥜", desc_en: "Oilseed crop well-suited for friable red sandy loam soils.", desc_ta: "செம்மண் மற்றும் மணல் கலந்த மண்ணிற்கு ஏற்ற எண்ணெய் வித்துப் பயிர்." },
  turmeric: { name_en: "Turmeric", name_ta: "மஞ்சள்", icon: "🌿", desc_en: "High-value rhizome crop well-adapted to Erode, Salem, and Coimbatore regions.", desc_ta: "ஈரோடு, சேலம் மற்றும் கோயம்புத்தூர் பகுதிகளுக்கு ஏற்ற அதிக மதிப்புள்ள கிழங்கு பயிர்." },
  onion: { name_en: "Onion", name_ta: "வெங்காயம்", icon: "🧅", desc_en: "Prefers well-drained friable loamy soil with mild dry harvest conditions.", desc_ta: "நல்ல வடிகால் வசதியுள்ள மண் மற்றும் மிதமான வறண்ட அறுவடை காலநிலைக்கு ஏற்றது." },
  potato: { name_en: "Potato", name_ta: "உருளைக்கிழங்கு", icon: "🥔", desc_en: "Cool-season tuber crop suited for well-drained sandy loam soils.", desc_ta: "குளிர்ந்த பருவம் மற்றும் வடிகால் வசதியுள்ள மணல் கலந்த மண்ணிற்கு ஏற்ற கிழங்கு பயிர்." },
  tomato: { name_en: "Tomato", name_ta: "தக்காளி", icon: "🍅", desc_en: "Versatile vegetable crop growing well in fertile neutral soils.", desc_ta: "வளமான நடுநிலை மண்ணில் நன்கு விளையும் காய்கறி பயிர்." },
  wheat: { name_en: "Wheat", name_ta: "கோதுமை", icon: "🌾", desc_en: "Cool-season cereal crop adapted to well-drained loamy soils.", desc_ta: "வடிகால் வசதியுள்ள வண்டல் மண்ணிற்கு ஏற்ற குளிர் பருவ தானியப் பயிர்." },
  chilli: { name_en: "Chilli", name_ta: "மிளகாய்", icon: "🌶️", desc_en: "Warm-season spice crop thriving in well-drained black and loamy soils.", desc_ta: "நல்ல வடிகால் வசதியுள்ள கரிசல் மற்றும் வண்டல் மண்ணில் விளையும் நறுமணப் பயிர்." },
  soybean: { name_en: "Soybean", name_ta: "சோயாபீன்", icon: "🫘", desc_en: "Protein-rich oilseed legume suited for well-drained fertile loams.", desc_ta: "வளமான மண்ணிற்கு ஏற்ற புரதம் நிறைந்த எண்ணெய் வித்துப் பயிர்." },
  sunflower: { name_en: "Sunflower", name_ta: "சூரியகாந்தி", icon: "🌻", desc_en: "Hardy oilseed crop adaptable to moderate rainfall and sunny conditions.", desc_ta: "மிதமான மழை மற்றும் வெயிலான சூழலுக்கு ஏற்ற எண்ணெய் வித்துப் பயிர்." },
};

function loadCropDatasetStats(): Record<string, Record<string, number>> {
  if (!fs.existsSync(CROP_DATA_CSV_PATH)) return {};
  const raw = fs.readFileSync(CROP_DATA_CSV_PATH, "utf-8");
  const lines = raw.split(/\r?\n/);
  if (lines.length < 2) return {};

  const headers = lines[0].split(",").map((h) => h.trim());
  const cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"];
  const colIndices = cols.map((c) => headers.indexOf(c));
  const labelIdx = headers.indexOf("label");
  if (labelIdx < 0) return {};

  const buckets = new Map<string, number[][]>();
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]?.trim();
    if (!line) continue;
    const parts = line.split(",");
    const label = (parts[labelIdx] ?? "").trim().toLowerCase();
    if (!label) continue;

    let bucket = buckets.get(label);
    if (!bucket) {
      bucket = cols.map(() => []);
      buckets.set(label, bucket);
    }
    cols.forEach((_, idx) => {
      const ci = colIndices[idx];
      if (ci >= 0) {
        const val = Number.parseFloat(parts[ci]);
        if (!Number.isNaN(val)) bucket![idx].push(val);
      }
    });
  }

  const out: Record<string, Record<string, number>> = {};
  for (const [label, arrs] of buckets.entries()) {
    if (!arrs[0].length) continue;
    const summary: Record<string, number> = { samples: arrs[0].length };
    cols.forEach((col, idx) => {
      const vals = arrs[idx];
      if (vals.length) {
        const k = col.toLowerCase();
        summary[`${k}_min`] = Math.round(Math.min(...vals) * 10) / 10;
        summary[`${k}_max`] = Math.round(Math.max(...vals) * 10) / 10;
        summary[`${k}_avg`] = Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10) / 10;
      }
    });
    out[label] = summary;
  }
  return out;
}

const cropDatasetStats = loadCropDatasetStats();

interface CropClassifierState {
  samples: CropSampleRow[];
  means: number[];
  stds: number[];
}

function loadCropClassifier(): CropClassifierState | null {
  if (!fs.existsSync(CROP_DATA_CSV_PATH)) return null;
  const raw = fs.readFileSync(CROP_DATA_CSV_PATH, "utf-8");
  const lines = raw.split(/\r?\n/);
  if (lines.length < 2) return null;

  const headers = lines[0].split(",").map((h) => h.trim());
  const cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"];
  const colIndices = cols.map((c) => headers.indexOf(c));
  const labelIdx = headers.indexOf("label");
  if (labelIdx < 0 || colIndices.some((i) => i < 0)) return null;

  const rawSamples: CropSampleRow[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]?.trim();
    if (!line) continue;
    const parts = line.split(",");
    const label = (parts[labelIdx] ?? "").trim().toLowerCase();
    if (!label) continue;
    const vec = colIndices.map((idx) => Number.parseFloat(parts[idx]));
    if (vec.some((v) => Number.isNaN(v))) continue;
    rawSamples.push({ features: vec, label });
  }
  if (!rawSamples.length) return null;

  const n = rawSamples.length;
  const dim = cols.length;
  const means = new Array<number>(dim).fill(0);
  for (const s of rawSamples) {
    for (let j = 0; j < dim; j++) means[j] += s.features[j];
  }
  for (let j = 0; j < dim; j++) means[j] /= n;

  const variances = new Array<number>(dim).fill(0);
  for (const s of rawSamples) {
    for (let j = 0; j < dim; j++) {
      const d = s.features[j] - means[j];
      variances[j] += d * d;
    }
  }
  const stds = variances.map((v) => Math.sqrt(v / n) || 1);

  const normalizedSamples: CropSampleRow[] = rawSamples.map((s) => ({
    label: s.label,
    features: s.features.map((v, j) => (v - means[j]) / stds[j]),
  }));

  return { samples: normalizedSamples, means, stds };
}

const cropClassifier = loadCropClassifier();

function predictCropFromDataset(inputVec: number[]): { cropKey: string; confidence: number } | null {
  if (!cropClassifier) return null;
  const norm = inputVec.map((v, j) => (v - cropClassifier.means[j]) / cropClassifier.stds[j]);
  const K = 11;
  const distances: Array<{ dist: number; label: string }> = [];

  for (const sample of cropClassifier.samples) {
    let sumSq = 0;
    for (let j = 0; j < norm.length; j++) {
      const d = norm[j] - sample.features[j];
      sumSq += d * d;
    }
    distances.push({ dist: Math.sqrt(sumSq), label: sample.label });
  }

  distances.sort((a, b) => a.dist - b.dist);
  const topK = distances.slice(0, K);

  const weights = new Map<string, number>();
  let totalWeight = 0;
  for (const neighbor of topK) {
    const w = 1 / (neighbor.dist + 1e-4);
    weights.set(neighbor.label, (weights.get(neighbor.label) ?? 0) + w);
    totalWeight += w;
  }

  let bestLabel = topK[0].label;
  let bestWeight = 0;
  for (const [lbl, w] of weights.entries()) {
    if (w > bestWeight) {
      bestWeight = w;
      bestLabel = lbl;
    }
  }
  const confidence = totalWeight > 0 ? Math.round((bestWeight / totalWeight) * 1000) / 10 : 0;
  return { cropKey: bestLabel, confidence };
}

const marketSummaryByCrop = (() => {
  const agg = new Map<string, { sum: number; min: number; max: number; count: number }>();
  for (const r of marketRows) {
    const k = r.crop.trim().toLowerCase();
    const cur = agg.get(k) ?? { sum: 0, min: r.price, max: r.price, count: 0 };
    cur.sum += r.price;
    cur.min = Math.min(cur.min, r.price);
    cur.max = Math.max(cur.max, r.price);
    cur.count += 1;
    agg.set(k, cur);
  }
  const out: Record<string, { avg_price: number; min_price: number; max_price: number }> = {};
  for (const [k, v] of agg.entries()) {
    out[k] = {
      avg_price: Math.round((v.sum / v.count) * 100) / 100,
      min_price: v.min,
      max_price: v.max,
    };
  }
  return out;
})();

const yesterday = new Date(Date.now() - 86400 * 1000).toISOString().slice(0, 10);
const historicalWeather: WeatherRow[] = [
  ["Thanjavur", 33.4, 76, 2.4, 16.5, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Coimbatore", 30.2, 64, 0.0, 18.2, "Clear Sky", "☀️", "தெளிவான வானம்"],
  ["Madurai", 34.8, 58, 0.5, 14.0, "Mostly Sunny", "🌤️", "வெயில்"],
  ["Salem", 32.1, 66, 1.2, 13.4, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Trichy", 34.5, 70, 0.8, 17.1, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Vellore", 32.8, 61, 0.0, 15.6, "Clear Sky", "☀️", "தெளிவான வானம்"],
  ["Tirunelveli", 31.6, 74, 4.2, 19.0, "Light Rain", "🌦️", "லேசான மழை"],
  ["Erode", 30.9, 68, 1.8, 12.5, "Overcast", "☁️", "மேகமூட்டம்"],
  ["Dindigul", 29.8, 67, 2.0, 14.8, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Chennai", 33.0, 79, 3.1, 21.4, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Cuddalore", 32.6, 80, 4.5, 20.1, "Light Rain", "🌦️", "லேசான மழை"],
  ["Kancheepuram", 33.2, 75, 1.0, 16.0, "Mostly Sunny", "🌤️", "வெயில்"],
  ["Karur", 33.9, 60, 0.0, 15.2, "Clear Sky", "☀️", "தெளிவான வானம்"],
  ["Krishnagiri", 28.7, 69, 1.5, 13.8, "Partly Cloudy", "⛅", "பகுதியளவு மேகமூட்டம்"],
  ["Virudhunagar", 34.1, 59, 0.2, 16.2, "Mostly Sunny", "🌤️", "வெயில்"],
].map(([district, temp, humidity, rainfall, wind, condEn, icon, condTa]) => {
  const [advEn, advTa] = buildAdvisory(Number(temp), Number(humidity), Number(rainfall));
  return {
    district: String(district),
    condition: String(icon),
    condition_name: String(condEn),
    condition_ta: String(condTa),
    temp: Number(temp),
    feels: Math.round((Number(temp) + (Number(humidity) > 70 ? 1.5 : 0.5)) * 10) / 10,
    humidity: Number(humidity),
    rainfall: Number(rainfall),
    wind: Number(wind),
    advisory_en: advEn,
    advisory_ta: advTa,
    source: "historical",
    is_live: false,
    date: yesterday,
  };
});

let weatherCacheTs = 0;
const weatherCacheMap = new Map<string, WeatherRow>();

async function getLiveWeather(districts: string[]): Promise<{ records: WeatherRow[]; error: string | null }> {
  const now = Date.now();
  if (now - weatherCacheTs < 300_000 && weatherCacheMap.size > 0) {
    const cached = districts.map((d) => weatherCacheMap.get(d)).filter((x): x is WeatherRow => Boolean(x));
    if (cached.length === districts.length) {
      return { records: cached, error: null };
    }
  }

  try {
    const lats = districts.map((d) => DISTRICT_COORDS[d][0]).join(",");
    const lons = districts.map((d) => DISTRICT_COORDS[d][1]).join(",");
    const url =
      `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lats)}` +
      `&longitude=${encodeURIComponent(lons)}` +
      `&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m` +
      `&timezone=Asia%2FKolkata`;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 6000);
    const resp = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    const payload = (await resp.json()) as unknown;
    const items = Array.isArray(payload) ? payload : [payload];
    const today = new Date().toISOString().slice(0, 10);
    const records: WeatherRow[] = [];

    districts.forEach((dist, idx) => {
      const item = (items[idx] ?? {}) as { current?: Record<string, number> };
      const cur = item.current ?? {};
      const code = Number(cur.weather_code ?? 0);
      const [icon, condEn, condTa] = WMO_WEATHER_MAP[code] ?? ["⛅", "Partly Cloudy", "பகுதியளவு மேகமூட்டம்"];
      const temp = Math.round(Number(cur.temperature_2m ?? 30) * 10) / 10;
      const feels = Math.round(Number(cur.apparent_temperature ?? temp) * 10) / 10;
      const humidity = Math.round(Number(cur.relative_humidity_2m ?? 65) * 10) / 10;
      const rainfall = Math.round(Number(cur.precipitation ?? 0) * 10) / 10;
      const wind = Math.round(Number(cur.wind_speed_10m ?? 12) * 10) / 10;
      const [advEn, advTa] = buildAdvisory(temp, humidity, rainfall);
      const rec: WeatherRow = {
        district: dist,
        condition: icon,
        condition_name: condEn,
        condition_ta: condTa,
        temp,
        feels,
        humidity,
        rainfall,
        wind,
        advisory_en: advEn,
        advisory_ta: advTa,
        source: "open-meteo-live",
        is_live: true,
        date: today,
      };
      weatherCacheMap.set(dist, rec);
      records.push(rec);
    });

    weatherCacheTs = now;
    return { records, error: null };
  } catch (err) {
    return { records: [], error: `Live weather API unavailable: ${(err as Error).message}` };
  }
}

// ─── SECURITY HELPERS ─────────────────────────────────────────────────────────
const SESSION_COOKIE = "smart_agri_session";
const SESSION_SIGNING_SECRET = getOrCreateSigningSecret();
const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
const PHONE_RE = /^\+?[0-9\s-]{8,24}$/;

function isPasswordComplex(password: string): boolean {
  if (password.length < 8 || password.length > 128) return false;
  return (
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password) &&
    /[^A-Za-z0-9\s]/.test(password)
  );
}

function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString("hex");
  const derived = crypto.scryptSync(password, salt, 64).toString("hex");
  return `${salt}:${derived}`;
}

function verifyPassword(password: string, stored: string): boolean {
  const [salt, key] = stored.split(":");
  if (!salt || !key) return false;
  const derived = crypto.scryptSync(password, salt, 64);
  const keyBuf = Buffer.from(key, "hex");
  return keyBuf.length === derived.length && crypto.timingSafeEqual(keyBuf, derived);
}

function signSessionId(sid: string): string {
  const sig = crypto
    .createHmac("sha256", SESSION_SIGNING_SECRET)
    .update(sid)
    .digest("base64url");
  return `${sid}.${sig}`;
}

function verifySignedSessionId(token: string | undefined): string | null {
  if (!token) return null;
  const dotIdx = token.indexOf(".");
  if (dotIdx <= 0) return null;
  const sid = token.slice(0, dotIdx);
  const expected = signSessionId(sid);
  if (token.length !== expected.length) return null;
  const ok = crypto.timingSafeEqual(Buffer.from(token), Buffer.from(expected));
  return ok ? sid : null;
}

function parseCookies(req: Request): Record<string, string> {
  const header = req.headers.cookie ?? "";
  const out: Record<string, string> = {};
  for (const part of header.split(";")) {
    const idx = part.indexOf("=");
    if (idx > 0) {
      const k = part.slice(0, idx).trim();
      const v = part.slice(idx + 1).trim();
      out[k] = decodeURIComponent(v);
    }
  }
  return out;
}

function isExternalHttpsRequest(req: Request): boolean {
  const fwdProto = String(req.headers["x-forwarded-proto"] ?? "").toLowerCase();
  const origin = String(req.headers.origin ?? "").toLowerCase();
  const referer = String(req.headers.referer ?? "").toLowerCase();
  const fwdHost = String(req.headers["x-forwarded-host"] ?? "").toLowerCase();
  const isRemoteProxy =
    Boolean(fwdHost) &&
    !fwdHost.startsWith("localhost") &&
    !fwdHost.startsWith("127.0.0.1");
  return (
    req.secure ||
    fwdProto === "https" ||
    origin.startsWith("https://") ||
    referer.startsWith("https://") ||
    isRemoteProxy
  );
}

function setSessionCookie(req: Request, res: Response, sid: string): void {
  const isHttps = isExternalHttpsRequest(req);
  const attrs = [
    `${SESSION_COOKIE}=${encodeURIComponent(sid)}`,
    "Path=/",
    "HttpOnly",
    isHttps ? "SameSite=None; Secure; Partitioned" : "SameSite=Lax",
  ];
  res.setHeader("Set-Cookie", attrs.join("; "));
}

function findSessionById(sid: string): SessionData | null {
  const row = db
    .prepare("SELECT id, csrf_token, farmer_id FROM sessions WHERE id = ?")
    .get(sid) as { id: string; csrf_token: string; farmer_id: number | null } | undefined;
  if (!row) return null;
  return {
    id: row.id,
    csrfToken: row.csrf_token,
    farmerId: row.farmer_id !== null && row.farmer_id !== undefined ? Number(row.farmer_id) : undefined,
  };
}

function saveSession(sess: SessionData): void {
  db.prepare(
    "INSERT OR REPLACE INTO sessions (id, csrf_token, farmer_id, updated_at) VALUES (?, ?, ?, ?)"
  ).run(sess.id, sess.csrfToken, sess.farmerId ?? null, new Date().toISOString());
}

function getOrCreateSession(req: Request, res: Response): SessionData {
  const cookies = parseCookies(req);
  const cookieSid = cookies[SESSION_COOKIE];
  if (cookieSid) {
    const existing = findSessionById(cookieSid);
    if (existing) return existing;
  }

  const headerSid = verifySignedSessionId(
    req.headers["x-preview-session"] as string | undefined
  );
  if (headerSid) {
    const existing = findSessionById(headerSid);
    if (existing) return existing;
  }

  const newSid = crypto.randomBytes(24).toString("hex");
  const sess: SessionData = {
    id: newSid,
    csrfToken: crypto.randomBytes(24).toString("base64url"),
  };
  saveSession(sess);
  setSessionCookie(req, res, newSid);
  return sess;
}

function sanitizeFarmer(f: FarmerRecord) {
  return {
    id: f.id,
    name: f.name,
    email: f.email,
    phone: f.phone,
    farm_location: f.farm_location,
    farm_size: f.farm_size,
    soil_type: f.soil_type,
    created_at: f.created_at,
  };
}

function requireCsrf(req: Request, res: Response, next: NextFunction): void {
  const sess = getOrCreateSession(req, res);
  const provided =
    (req.headers["x-csrf-token"] as string | undefined) ||
    (typeof req.body?.csrf_token === "string" ? req.body.csrf_token : undefined);

  if (!provided || provided.length !== sess.csrfToken.length) {
    res.status(403).json({
      success: false,
      error: "Invalid or missing CSRF token. Please refresh and try again.",
    });
    return;
  }
  const ok = crypto.timingSafeEqual(Buffer.from(sess.csrfToken), Buffer.from(provided));
  if (!ok) {
    res.status(403).json({
      success: false,
      error: "Invalid or missing CSRF token. Please refresh and try again.",
    });
    return;
  }
  next();
}

function requireAuth(req: Request, res: Response): FarmerRecord | null {
  const sess = getOrCreateSession(req, res);
  if (!sess.farmerId) {
    res.status(401).json({
      success: false,
      error: "Authentication required. Please log in to continue.",
      login_required: true,
    });
    return null;
  }
  const farmer = getFarmerById(sess.farmerId);
  if (!farmer) {
    sess.farmerId = undefined;
    saveSession(sess);
    res.status(401).json({
      success: false,
      error: "Session expired. Please log in again.",
      login_required: true,
    });
    return null;
  }
  return farmer;
}

function renderHtmlPage(initialSection: string, req: Request, res: Response): void {
  const sess = getOrCreateSession(req, res);
  let html = fs.readFileSync(TEMPLATE_PATH, "utf-8");
  html = html
    .replace(
      '<meta name="csrf-token" content="{{ csrf_token | default(\'\') }}">',
      `<meta name="csrf-token" content="${sess.csrfToken}">\n<meta name="preview-session" content="${signSessionId(sess.id)}">`
    )
    .replace("{{ initial_section | default('home') }}", initialSection);
  res.setHeader("Cache-Control", "no-store");
  res.status(200).type("html").send(html);
}

// ─── EXPRESS APP SETUP ────────────────────────────────────────────────────────
const app = express();
app.set("trust proxy", 1);
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: false, limit: "2mb" }));
app.use("/static", express.static(STATIC_DIR));

// Page routes
const PAGE_SECTIONS: Record<string, string> = {
  "/": "home",
  "/login": "login",
  "/register": "register",
  "/dashboard": "dashboard",
  "/disease": "disease",
  "/market-prices": "market",
  "/weather": "weather",
  "/logout": "logout",
};

for (const [routePath, sec] of Object.entries(PAGE_SECTIONS)) {
  app.get(routePath, (req, res) => renderHtmlPage(sec, req, res));
}

// CSRF & Health
app.get("/api/csrf-token", (req, res) => {
  const sess = getOrCreateSession(req, res);
  res.setHeader("Cache-Control", "no-store");
  res.json({
    success: true,
    csrf_token: sess.csrfToken,
    preview_session: signSessionId(sess.id),
  });
});

app.get("/api/health", (_req, res) => {
  const hasCropPkl = fs.existsSync(path.join(SMART_AGRI_DIR, "crop_model.pkl"));
  const hasDiseaseH5 = fs.existsSync(path.join(SMART_AGRI_DIR, "disease_model.h5"));
  const hasGeminiVision = Boolean(getGeminiVisionClient());
  res.json({
    success: true,
    database: true,
    models: {
      crop_model: hasCropPkl || Boolean(cropClassifier),
      disease_model: hasDiseaseH5 || hasGeminiVision,
      crop_error: hasCropPkl
        ? null
        : cropClassifier
          ? null
          : "Model file not found: crop_model.pkl (run smart_agri_ai/app.py locally with trained .pkl artifacts)",
      disease_error: hasDiseaseH5 || hasGeminiVision
        ? null
        : "Plant disease vision unavailable: set GEMINI_API_KEY in AI Studio Secrets or run smart_agri_ai/app.py locally with disease_model.h5",
    },
  });
});

// Authentication
const authFormUpload = multer({
  limits: { fields: 20, fieldSize: 32 * 1024, files: 0 },
});

function parseAuthFormData(req: Request, res: Response, next: NextFunction): void {
  const ct = String(req.headers["content-type"] ?? "").toLowerCase();
  if (!ct.includes("multipart/form-data")) {
    next();
    return;
  }
  authFormUpload.none()(req, res, (err: unknown) => {
    if (err) {
      console.error(
        "[SmartAgri Auth] Multipart FormData parse failed:",
        err instanceof Error ? err.message : String(err)
      );
      res.status(400).json({
        success: false,
        error: "Invalid form submission payload. Please check your entries and try again.",
      });
      return;
    }
    next();
  });
}

app.post("/api/auth/register", parseAuthFormData, requireCsrf, (req, res) => {
  const sess = getOrCreateSession(req, res);
  const body = req.body ?? {};
  const name = String(body.name ?? "").trim();
  const email = String(body.email ?? "").trim().toLowerCase();
  const phoneRaw = String(body.phone ?? "").trim();
  const phone = phoneRaw.replace(/[\s-]+/g, "");
  const phoneDigits = phone.replace(/\D/g, "");
  const farm_location = String(body.farm_location ?? "").trim();
  const soil_type = String(body.soil_type ?? "Alluvial Soil").trim() || "Alluvial Soil";
  const password = String(body.password ?? "");
  const farm_size = Number.parseFloat(String(body.farm_size ?? "0"));

  if (name.length < 2 || name.length > 120) {
    res.status(400).json({ success: false, error: "Full name must be between 2 and 120 characters." });
    return;
  }
  if (email.length > 160 || !EMAIL_RE.test(email)) {
    res.status(400).json({ success: false, error: "Please enter a valid email address (max 160 characters)." });
    return;
  }
  if (!PHONE_RE.test(phoneRaw) || phone.length > 24 || phoneDigits.length < 10 || phoneDigits.length > 15) {
    res.status(400).json({ success: false, error: "Please enter a valid 10 to 15 digit phone number." });
    return;
  }
  if (!farm_location || farm_location.length > 100) {
    res.status(400).json({
      success: false,
      error: "Please select a valid farm location / district (max 100 characters).",
    });
    return;
  }
  if (!Number.isFinite(farm_size) || farm_size < 0.1 || farm_size > 10000) {
    res.status(400).json({ success: false, error: "Farm size must be between 0.1 and 10,000 acres." });
    return;
  }
  if (soil_type.length > 80) {
    res.status(400).json({ success: false, error: "Soil type must be 80 characters or fewer." });
    return;
  }
  if (!isPasswordComplex(password)) {
    res.status(400).json({
      success: false,
      error:
        "Password must be 8–128 characters and include at least one uppercase letter, one lowercase letter, one number, and one special character.",
    });
    return;
  }

  if (getFarmerByEmail(email)) {
    res.status(409).json({ success: false, error: "An account with this email already exists." });
    return;
  }
  const existingPhone = db
    .prepare("SELECT id FROM farmers WHERE phone = ?")
    .get(phone) as { id: number } | undefined;
  if (existingPhone) {
    res.status(409).json({ success: false, error: "An account with this phone number already exists." });
    return;
  }

  const createdAt = new Date().toISOString();
  const roundedSize = Math.round(farm_size * 100) / 100;
  const passwordHash = hashPassword(password);

  let insertInfo: { lastInsertRowid: number | bigint };
  try {
    insertInfo = db
      .prepare(
        "INSERT INTO farmers (name, email, phone, farm_location, farm_size, soil_type, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
      )
      .run(name, email, phone, farm_location, roundedSize, soil_type, passwordHash, createdAt);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error("[SmartAgri Register] SQLite INSERT INTO farmers failed:", msg);
    if (msg.includes("UNIQUE constraint failed")) {
      const isPhone = msg.includes("farmers.phone");
      res.status(409).json({
        success: false,
        error: isPhone
          ? "An account with this phone number already exists."
          : "An account with this email already exists.",
      });
      return;
    }
    res.status(400).json({
      success: false,
      error: "Registration could not be saved due to database field constraints.",
    });
    return;
  }

  const record: FarmerRecord = {
    id: Number(insertInfo.lastInsertRowid),
    name,
    email,
    phone,
    farm_location,
    farm_size: roundedSize,
    soil_type,
    passwordHash,
    created_at: createdAt,
  };

  sess.farmerId = record.id;
  sess.csrfToken = crypto.randomBytes(24).toString("base64url");
  saveSession(sess);
  setSessionCookie(req, res, sess.id);

  res.status(201).json({
    success: true,
    message: "Registration successful.",
    csrf_token: sess.csrfToken,
    preview_session: signSessionId(sess.id),
    farmer: sanitizeFarmer(record),
  });
});

app.post("/api/auth/login", parseAuthFormData, requireCsrf, (req, res) => {
  const sess = getOrCreateSession(req, res);
  const body = req.body ?? {};
  const email = String(body.email ?? "").trim().toLowerCase();
  const password = String(body.password ?? "");

  if (email.length > 160 || !EMAIL_RE.test(email) || !password) {
    res.status(400).json({ success: false, error: "Valid email and password are required." });
    return;
  }

  const farmer = getFarmerByEmail(email);
  if (!farmer || !verifyPassword(password, farmer.passwordHash)) {
    res.status(401).json({ success: false, error: "Invalid email or password." });
    return;
  }

  sess.farmerId = farmer.id;
  sess.csrfToken = crypto.randomBytes(24).toString("base64url");
  saveSession(sess);
  setSessionCookie(req, res, sess.id);
  res.json({
    success: true,
    message: "Login successful.",
    csrf_token: sess.csrfToken,
    preview_session: signSessionId(sess.id),
    farmer: sanitizeFarmer(farmer),
  });
});

app.post("/api/auth/logout", requireCsrf, (req, res) => {
  const sess = getOrCreateSession(req, res);
  sess.farmerId = undefined;
  sess.csrfToken = crypto.randomBytes(24).toString("base64url");
  saveSession(sess);
  setSessionCookie(req, res, sess.id);
  res.json({
    success: true,
    message: "Logged out successfully.",
    csrf_token: sess.csrfToken,
    preview_session: signSessionId(sess.id),
  });
});

app.get("/api/auth/me", (req, res) => {
  const sess = getOrCreateSession(req, res);
  if (!sess.farmerId) {
    res.status(401).json({ success: false, authenticated: false, farmer: null });
    return;
  }
  const farmer = getFarmerById(sess.farmerId);
  if (!farmer) {
    sess.farmerId = undefined;
    saveSession(sess);
    res.status(401).json({ success: false, authenticated: false, farmer: null });
    return;
  }
  res.json({
    success: true,
    authenticated: true,
    csrf_token: sess.csrfToken,
    preview_session: signSessionId(sess.id),
    farmer: sanitizeFarmer(farmer),
  });
});

// Protected Dashboard & History
app.get("/api/dashboard", async (req, res) => {
  const farmer = requireAuth(req, res);
  if (!farmer) return;

  const farmerTests = db
    .prepare(
      "SELECT id, farmer_id, nitrogen, phosphorus, potassium, ph, district, temperature, humidity, rainfall, confidence, recommendation, recommendation_ta, icon, date FROM soil_test WHERE farmer_id = ? ORDER BY date DESC, id DESC"
    )
    .all(farmer.id) as unknown as SoilTestRecord[];

  const latestSoil = farmerTests[0] ?? null;
  const latestRec = latestSoil
    ? {
        crop_name: latestSoil.recommendation,
        crop_name_ta: latestSoil.recommendation_ta,
        confidence: latestSoil.confidence,
        nitrogen: latestSoil.nitrogen,
        phosphorus: latestSoil.phosphorus,
        potassium: latestSoil.potassium,
        date: latestSoil.date,
      }
    : null;

  const farmerDiseases = db
    .prepare(
      "SELECT id, farmer_id, crop_type, disease_name, confidence, severity, image_filename, treatment, date FROM disease_history WHERE farmer_id = ? ORDER BY date DESC, id DESC"
    )
    .all(farmer.id) as unknown as DiseaseRecord[];

  const recentActivity = [
    ...farmerTests.slice(0, 5).map((s) => ({
      type: "soil_test",
      icon: s.icon,
      title_en: `Crop Recommendation — ${s.recommendation}`,
      title_ta: `பயிர் பரிந்துரை — ${s.recommendation_ta}`,
      sub_en: `N:${s.nitrogen.toFixed(0)} P:${s.phosphorus.toFixed(0)} K:${s.potassium.toFixed(0)} • Confidence ${s.confidence.toFixed(1)}%`,
      sub_ta: `N:${s.nitrogen.toFixed(0)} P:${s.phosphorus.toFixed(0)} K:${s.potassium.toFixed(0)} • நம்பகத்தன்மை ${s.confidence.toFixed(1)}%`,
      date: s.date,
    })),
    ...farmerDiseases.slice(0, 5).map((d) => ({
      type: "disease_scan",
      icon: "🔬",
      title_en: `Disease Scan — ${d.disease_name} (${d.crop_type})`,
      title_ta: `நோய் ஸ்கேன் — ${d.disease_name} (${d.crop_type})`,
      sub_en: `Confidence ${d.confidence.toFixed(1)}% • Severity: ${d.severity.charAt(0).toUpperCase() + d.severity.slice(1)}`,
      sub_ta: `நம்பகத்தன்மை ${d.confidence.toFixed(1)}% • தீவிரம்: ${d.severity.charAt(0).toUpperCase() + d.severity.slice(1)}`,
      date: d.date,
    })),
  ]
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 8);

  let weatherInfo: WeatherRow | null = null;
  if (DISTRICT_COORDS[farmer.farm_location]) {
    const live = await getLiveWeather([farmer.farm_location]);
    weatherInfo = live.records[0] ?? null;
  }
  if (!weatherInfo) {
    weatherInfo =
      historicalWeather.find((w) => w.district.toLowerCase() === farmer.farm_location.toLowerCase()) ??
      null;
  }

  res.json({
    success: true,
    data: {
      farmer: sanitizeFarmer(farmer),
      total_soil_tests: farmerTests.length,
      total_disease_detections: farmerDiseases.length,
      latest_recommendation: latestRec,
      recent_activity: recentActivity,
      weather: weatherInfo,
    },
  });
});

app.get("/api/soil-tests", (req, res) => {
  const farmer = requireAuth(req, res);
  if (!farmer) return;
  const rows = db
    .prepare(
      "SELECT id, farmer_id, nitrogen, phosphorus, potassium, ph, district, temperature, humidity, rainfall, confidence, recommendation, recommendation_ta, icon, date FROM soil_test WHERE farmer_id = ? ORDER BY date DESC, id DESC LIMIT 25"
    )
    .all(farmer.id) as unknown as SoilTestRecord[];
  res.json({ success: true, data: rows });
});

app.get("/api/disease-history", (req, res) => {
  const farmer = requireAuth(req, res);
  if (!farmer) return;
  const rows = (
    db
      .prepare(
        "SELECT id, crop_type, disease_name, confidence, severity, image_filename, treatment, date FROM disease_history WHERE farmer_id = ? ORDER BY date DESC, id DESC LIMIT 25"
      )
      .all(farmer.id) as unknown as DiseaseRecord[]
  ).map((d) => ({
    id: d.id,
    crop_type: d.crop_type,
    disease_name: d.disease_name,
    confidence: d.confidence,
    severity: d.severity,
    image_url: `/uploads/${d.image_filename}`,
    treatment: d.treatment,
    date: d.date,
  }));
  res.json({ success: true, data: rows });
});

async function resolveDistrictClimate(district: string): Promise<[number, number, number]> {
  if (DISTRICT_COORDS[district]) {
    const live = await getLiveWeather([district]);
    if (live.records[0]) {
      const w = live.records[0];
      return [w.temp, w.humidity, Math.max(w.rainfall * 25.0, 60.0)];
    }
  }
  const hist = historicalWeather.find(
    (w) => w.district.toLowerCase() === district.toLowerCase()
  );
  if (hist) {
    return [hist.temp, hist.humidity, Math.max(hist.rainfall * 25.0, 60.0)];
  }
  return [27.0, 72.0, 120.0];
}

// Crop Recommendation (dataset-driven standardized k-NN over crop_data.csv when .pkl runtime is absent)
app.post("/api/crop/predict", requireCsrf, async (req, res) => {
  const farmer = requireAuth(req, res);
  if (!farmer) return;
  const body = req.body ?? {};
  const n = Number(body.nitrogen);
  const p = Number(body.phosphorus);
  const k = Number(body.potassium);
  const ph = Number(body.ph ?? 6.5);
  const district = String(body.district ?? farmer.farm_location ?? "").trim();

  if (
    body.nitrogen === undefined ||
    body.phosphorus === undefined ||
    body.potassium === undefined ||
    [n, p, k].some((v) => Number.isNaN(v)) ||
    n < 0 ||
    n > 300 ||
    p < 0 ||
    p > 300 ||
    k < 0 ||
    k > 300
  ) {
    res.status(400).json({ success: false, error: "NPK values must be between 0 and 300 kg/ha." });
    return;
  }
  if (Number.isNaN(ph) || ph < 3 || ph > 10) {
    res.status(400).json({ success: false, error: "Soil pH must be between 3.0 and 10.0." });
    return;
  }
  if (!district) {
    res.status(400).json({ success: false, error: "Please select a district." });
    return;
  }

  const [defTemp, defHum, defRain] = await resolveDistrictClimate(district);
  const temperature =
    body.temperature !== null && body.temperature !== undefined && body.temperature !== ""
      ? Number(body.temperature)
      : defTemp;
  const humidity =
    body.humidity !== null && body.humidity !== undefined && body.humidity !== ""
      ? Number(body.humidity)
      : defHum;
  const rainfall =
    body.rainfall !== null && body.rainfall !== undefined && body.rainfall !== ""
      ? Number(body.rainfall)
      : defRain;

  if ([temperature, humidity, rainfall].some((v) => Number.isNaN(v))) {
    res.status(400).json({ success: false, error: "Climate parameters must be numeric." });
    return;
  }

  const pred = predictCropFromDataset([n, p, k, temperature, humidity, ph, rainfall]);
  if (!pred) {
    res.status(422).json({
      success: false,
      error: "Crop dataset or model is unavailable on this server.",
    });
    return;
  }

  const meta = CROP_DETAILS_CATALOG[pred.cropKey];
  const cropNameEn = meta?.name_en ?? pred.cropKey.charAt(0).toUpperCase() + pred.cropKey.slice(1);
  const cropNameTa = meta?.name_ta ?? cropNameEn;
  const descEn =
    meta?.desc_en ??
    `Based on your soil NPK (${n.toFixed(0)}/${p.toFixed(0)}/${k.toFixed(0)}) and pH ${ph.toFixed(1)}, ${cropNameEn} is recommended.`;
  const descTa =
    meta?.desc_ta ??
    `உங்கள் மண் NPK (${n.toFixed(0)}/${p.toFixed(0)}/${k.toFixed(0)}) மற்றும் pH ${ph.toFixed(1)} அடிப்படையில் ${cropNameTa} பரிந்துரைக்கப்படுகிறது.`;
  const icon = meta?.icon ?? "🌱";
  const nowIso = new Date().toISOString().slice(0, 19);

  const rN = Math.round(n * 100) / 100;
  const rP = Math.round(p * 100) / 100;
  const rK = Math.round(k * 100) / 100;
  const rPh = Math.round(ph * 100) / 100;
  const rTemp = Math.round(temperature * 100) / 100;
  const rHum = Math.round(humidity * 100) / 100;
  const rRain = Math.round(rainfall * 100) / 100;

  const insertSoil = db
    .prepare(
      "INSERT INTO soil_test (farmer_id, nitrogen, phosphorus, potassium, ph, district, temperature, humidity, rainfall, confidence, recommendation, recommendation_ta, icon, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    .run(
      farmer.id,
      rN,
      rP,
      rK,
      rPh,
      district,
      rTemp,
      rHum,
      rRain,
      pred.confidence,
      cropNameEn,
      cropNameTa,
      icon,
      nowIso
    );

  const savedRow: SoilTestRecord = {
    id: Number(insertSoil.lastInsertRowid),
    farmer_id: farmer.id,
    nitrogen: rN,
    phosphorus: rP,
    potassium: rK,
    ph: rPh,
    district,
    temperature: rTemp,
    humidity: rHum,
    rainfall: rRain,
    confidence: pred.confidence,
    recommendation: cropNameEn,
    recommendation_ta: cropNameTa,
    icon,
    date: nowIso,
  };

  res.json({
    success: true,
    data: {
      id: savedRow.id,
      crop_name: cropNameEn,
      crop_name_ta: cropNameTa,
      confidence: pred.confidence,
      description_en: descEn,
      description_ta: descTa,
      icon,
      npk_summary: {
        nitrogen: savedRow.nitrogen,
        phosphorus: savedRow.phosphorus,
        potassium: savedRow.potassium,
        ph: savedRow.ph,
        district,
        temperature: Math.round(temperature * 10) / 10,
        humidity: Math.round(humidity * 10) / 10,
        rainfall: Math.round(rainfall * 10) / 10,
      },
      date: nowIso,
    },
  });
});

const ALLOWED_IMAGE_EXTS = new Set(["png", "jpg", "jpeg", "webp", "gif", "bmp"]);
const SAFE_FILENAME_RE = /^[A-Za-z0-9_.-]+$/;

const uploadMulter = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024, files: 1 },
});

function detectImageFormat(buf: Buffer): { mimeType: string; ext: string } | null {
  if (
    buf.length >= 8 &&
    buf[0] === 0x89 &&
    buf[1] === 0x50 &&
    buf[2] === 0x4e &&
    buf[3] === 0x47 &&
    buf[4] === 0x0d &&
    buf[5] === 0x0a &&
    buf[6] === 0x1a &&
    buf[7] === 0x0a
  ) {
    return { mimeType: "image/png", ext: "png" };
  }
  if (buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) {
    return { mimeType: "image/jpeg", ext: "jpg" };
  }
  if (
    buf.length >= 12 &&
    buf.subarray(0, 4).toString("ascii") === "RIFF" &&
    buf.subarray(8, 12).toString("ascii") === "WEBP"
  ) {
    return { mimeType: "image/webp", ext: "webp" };
  }
  if (
    buf.length >= 6 &&
    (buf.subarray(0, 6).toString("ascii") === "GIF87a" ||
      buf.subarray(0, 6).toString("ascii") === "GIF89a")
  ) {
    return { mimeType: "image/gif", ext: "gif" };
  }
  if (buf.length >= 2 && buf.subarray(0, 2).toString("ascii") === "BM") {
    return { mimeType: "image/bmp", ext: "bmp" };
  }
  return null;
}

function getGeminiVisionClient(): GoogleGenAI | null {
  const apiKey = process.env.GEMINI_API_KEY?.trim();
  if (!apiKey || apiKey === "MY_GEMINI_API_KEY") {
    return null;
  }
  return new GoogleGenAI({
    apiKey,
    httpOptions: {
      timeout: 45000,
      headers: { "User-Agent": "aistudio-build" },
    },
  });
}

interface VisionDiseaseResult {
  is_plant_leaf: boolean;
  matched_class_key: string;
  crop_name_en: string;
  crop_name_ta: string;
  disease_name_en: string;
  disease_name_ta: string;
  severity: "low" | "medium" | "high";
  confidence: number;
  description_en?: string;
  description_ta?: string;
  treatment_en?: string;
  treatment_ta?: string;
}

const VISION_MODEL_CANDIDATES = [
  "gemini-3.1-flash-lite",
  "gemini-4-hydrogen",
  "gemini-3.1-flash-lite",
] as const;

function isTransientVisionError(err: unknown): boolean {
  const msg = err instanceof Error ? err.message : String(err ?? "");
  return (
    msg.includes("503") ||
    msg.includes("429") ||
    msg.includes("UNAVAILABLE") ||
    msg.includes("RESOURCE_EXHAUSTED") ||
    msg.includes("high demand") ||
    msg.includes("ETIMEDOUT") ||
    msg.includes("timeout")
  );
}

function formatVisionErrorMessage(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err ?? "Leaf image analysis failed.");
  if (
    msg.includes("503") ||
    msg.includes("UNAVAILABLE") ||
    msg.includes("high demand") ||
    msg.includes("RESOURCE_EXHAUSTED") ||
    msg.includes("429")
  ) {
    return "Plant disease AI vision service is temporarily experiencing high demand. Please click Detect Disease again in a few seconds.";
  }
  return `Could not analyze leaf image: ${msg}`;
}

async function analyzeLeafWithGemini(
  ai: GoogleGenAI,
  imgBuffer: Buffer,
  mimeType: string
): Promise<VisionDiseaseResult> {
  const classListText = DISEASE_CLASS_KEYS.join(", ");
  const prompt = [
    "You are an expert agricultural plant pathologist diagnosing a crop leaf photo for Smart Agri AI.",
    "1. If the image is NOT a plant leaf/foliage crop (e.g., person, car, document, blank graphic), set `is_plant_leaf: false`, `matched_class_key: ''`, and leave text fields empty.",
    `2. If it IS a plant leaf, match it to one of these canonical classes if applicable: [${classListText}].`,
    "   - If matched (including healthy classes), set `matched_class_key` to that EXACT key, provide `confidence` as a percentage number between 50 and 99.9 (e.g. 92.5, never a 0-1 decimal) and `severity` ('low'|'medium'|'high'), and set `description_en`, `description_ta`, `treatment_en`, `treatment_ta` to empty strings '' (our catalog supplies them).",
    '   - Only if the leaf is a crop/disease NOT in that list, set `matched_class_key` to "OTHER" and provide concise English & Tamil crop/disease names, description, and 4 numbered treatment steps.',
  ].join("\n");

  let lastErr: unknown = null;
  for (let i = 0; i < VISION_MODEL_CANDIDATES.length; i++) {
    const model = VISION_MODEL_CANDIDATES[i];
    try {
      const response = await ai.models.generateContent({
        model,
        contents: [
          {
            inlineData: {
              mimeType,
              data: imgBuffer.toString("base64"),
            },
          },
          { text: prompt },
        ],
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              is_plant_leaf: { type: Type.BOOLEAN },
              matched_class_key: { type: Type.STRING },
              crop_name_en: { type: Type.STRING },
              crop_name_ta: { type: Type.STRING },
              disease_name_en: { type: Type.STRING },
              disease_name_ta: { type: Type.STRING },
              severity: { type: Type.STRING, enum: ["low", "medium", "high"] },
              confidence: { type: Type.NUMBER },
              description_en: { type: Type.STRING },
              description_ta: { type: Type.STRING },
              treatment_en: { type: Type.STRING },
              treatment_ta: { type: Type.STRING },
            },
            required: [
              "is_plant_leaf",
              "matched_class_key",
              "crop_name_en",
              "crop_name_ta",
              "disease_name_en",
              "disease_name_ta",
              "severity",
              "confidence",
            ],
          },
        },
      });

      const rawText = response.text;
      if (!rawText) {
        throw new Error("Vision model returned an empty response.");
      }
      return JSON.parse(rawText) as VisionDiseaseResult;
    } catch (err) {
      lastErr = err;
      if (!isTransientVisionError(err) || i === VISION_MODEL_CANDIDATES.length - 1) {
        throw err;
      }
      await new Promise((resolve) => setTimeout(resolve, 700));
    }
  }

  throw lastErr ?? new Error("Leaf image analysis failed.");
}

function attachAuthenticatedFarmer(req: Request, res: Response, next: NextFunction): void {
  const farmer = requireAuth(req, res);
  if (!farmer) return;
  (req as AuthenticatedRequest).farmer = farmer;
  next();
}

function handleDiseaseUpload(req: Request, res: Response, next: NextFunction): void {
  uploadMulter.single("image")(req, res, (err: unknown) => {
    if (err instanceof multer.MulterError) {
      if (err.code === "LIMIT_FILE_SIZE") {
        res.status(413).json({ success: false, error: "Image exceeds 10 MB size limit." });
        return;
      }
      res.status(400).json({ success: false, error: `Upload error: ${err.message}` });
      return;
    }
    if (err) {
      res.status(400).json({ success: false, error: "Failed to read uploaded image." });
      return;
    }
    next();
  });
}

// Plant Disease Detection (Gemini Vision multimodal analysis in preview; Keras disease_model.h5 in local app.py)
// Note: Return 422 (never 502/503/504) on unavailable config so reverse-proxy passes JSON cleanly.
app.post(
  "/api/disease/detect",
  requireCsrf,
  attachAuthenticatedFarmer,
  handleDiseaseUpload,
  async (req, res) => {
    const farmer = (req as AuthenticatedRequest).farmer!;
    const file = req.file;
    if (!file || !file.originalname) {
      res.status(400).json({ success: false, error: "No image file provided." });
      return;
    }

    const ext = file.originalname.includes(".")
      ? file.originalname.split(".").pop()!.toLowerCase()
      : "";
    if (!ALLOWED_IMAGE_EXTS.has(ext)) {
      res.status(400).json({
        success: false,
        error: "Invalid file type. Allowed formats: PNG, JPG, JPEG, WEBP.",
      });
      return;
    }

    if (!file.buffer || file.buffer.length === 0) {
      res.status(400).json({ success: false, error: "Uploaded file is empty." });
      return;
    }

    const imgFmt = detectImageFormat(file.buffer);
    if (!imgFmt) {
      res.status(400).json({
        success: false,
        error: "Uploaded file is not a valid readable image.",
      });
      return;
    }

    const ai = getGeminiVisionClient();
    if (!ai) {
      res.status(422).json({
        success: false,
        error:
          "Plant disease vision model is not configured in this preview environment (GEMINI_API_KEY missing, and TensorFlow disease_model.h5 requires local Python). Add GEMINI_API_KEY in AI Studio Secrets or run smart_agri_ai/app.py locally with disease_model.h5.",
      });
      return;
    }

    let diagnosis: VisionDiseaseResult;
    try {
      diagnosis = await analyzeLeafWithGemini(ai, file.buffer, imgFmt.mimeType);
    } catch (err) {
      res.status(422).json({
        success: false,
        error: formatVisionErrorMessage(err),
      });
      return;
    }

    if (!diagnosis.is_plant_leaf) {
      res.status(400).json({
        success: false,
        error:
          "The uploaded image does not appear to be a plant or crop leaf. Please upload a clear photo of an affected leaf.",
      });
      return;
    }

    let matchedKey = (diagnosis.matched_class_key || "").trim();
    let catalogInfo: DiseaseCatalogEntry | undefined = DISEASE_CATALOG[matchedKey];
    if (!catalogInfo && matchedKey && matchedKey.toUpperCase() !== "OTHER") {
      const norm = matchedKey.toLowerCase().replace(/\s+/g, "");
      const foundKey = DISEASE_CLASS_KEYS.find(
        (k) => k.toLowerCase().replace(/\s+/g, "") === norm
      );
      if (foundKey) {
        matchedKey = foundKey;
        catalogInfo = DISEASE_CATALOG[foundKey];
      }
    }

    const sevRaw = String(diagnosis.severity || "medium").toLowerCase();
    const fallbackSev: "low" | "medium" | "high" =
      sevRaw === "low" || sevRaw === "high" ? sevRaw : "medium";

    const info: DiseaseCatalogEntry = catalogInfo ?? {
      disease_name: diagnosis.disease_name_en || DEFAULT_DISEASE_ENTRY.disease_name,
      disease_name_ta:
        diagnosis.disease_name_ta ||
        diagnosis.disease_name_en ||
        DEFAULT_DISEASE_ENTRY.disease_name_ta,
      severity: fallbackSev,
      crop_name: diagnosis.crop_name_en || DEFAULT_DISEASE_ENTRY.crop_name,
      crop_name_ta:
        diagnosis.crop_name_ta || diagnosis.crop_name_en || DEFAULT_DISEASE_ENTRY.crop_name_ta,
      description_en: diagnosis.description_en || DEFAULT_DISEASE_ENTRY.description_en,
      description_ta:
        diagnosis.description_ta ||
        diagnosis.description_en ||
        DEFAULT_DISEASE_ENTRY.description_ta,
      treatment_en: diagnosis.treatment_en || DEFAULT_DISEASE_ENTRY.treatment_en,
      treatment_ta:
        diagnosis.treatment_ta ||
        diagnosis.treatment_en ||
        DEFAULT_DISEASE_ENTRY.treatment_ta,
    };

    const rawConf = Number(diagnosis.confidence);
    const pctConf = Number.isFinite(rawConf)
      ? rawConf > 0 && rawConf <= 1
        ? rawConf * 100
        : rawConf
      : 85.0;
    const confidence = Math.round(Math.min(100, Math.max(1, pctConf)) * 10) / 10;

    const uniqueName = `farmer_${farmer.id}_${crypto.randomBytes(6).toString("hex")}.${imgFmt.ext}`;
    const targetPath = path.resolve(UPLOAD_DIR, uniqueName);
    if (!targetPath.startsWith(UPLOAD_DIR + path.sep)) {
      res.status(400).json({ success: false, error: "Invalid upload filename." });
      return;
    }
    fs.writeFileSync(targetPath, file.buffer);

    const nowIso = new Date().toISOString().slice(0, 19);
    const insertDisease = db
      .prepare(
        "INSERT INTO disease_history (farmer_id, crop_type, disease_name, confidence, severity, image_filename, mime_type, treatment, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
      )
      .run(
        farmer.id,
        info.crop_name,
        info.disease_name,
        confidence,
        info.severity,
        uniqueName,
        imgFmt.mimeType,
        info.treatment_en,
        nowIso
      );

    const savedId = Number(insertDisease.lastInsertRowid);

    res.json({
      success: true,
      data: {
        id: savedId,
        disease_name: info.disease_name,
        disease_name_ta: info.disease_name_ta,
        severity: info.severity,
        confidence,
        crop_name: info.crop_name,
        crop_name_ta: info.crop_name_ta,
        description_en: info.description_en,
        description_ta: info.description_ta,
        treatment_en: info.treatment_en,
        treatment_ta: info.treatment_ta,
        class_key: catalogInfo ? matchedKey : "OTHER",
        image_url: `/uploads/${uniqueName}`,
        date: nowIso,
      },
    });
  }
);

app.get("/uploads/:filename", (req, res) => {
  const farmer = requireAuth(req, res);
  if (!farmer) return;

  const cleanName = path.basename(String(req.params.filename || ""));
  if (!cleanName || !SAFE_FILENAME_RE.test(cleanName)) {
    res.status(400).json({ success: false, error: "Invalid file path." });
    return;
  }

  const row = db
    .prepare("SELECT farmer_id, mime_type FROM disease_history WHERE image_filename = ?")
    .get(cleanName) as { farmer_id: number; mime_type: string } | undefined;

  if (!row) {
    res.status(404).json({ success: false, error: "Image not found." });
    return;
  }
  if (Number(row.farmer_id) !== farmer.id) {
    res.status(403).json({ success: false, error: "Access denied." });
    return;
  }

  const targetPath = path.resolve(UPLOAD_DIR, cleanName);
  if (!targetPath.startsWith(UPLOAD_DIR + path.sep) || !fs.existsSync(targetPath)) {
    res.status(404).json({ success: false, error: "Image not found." });
    return;
  }

  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("Content-Type", row.mime_type || "image/jpeg");
  res.send(fs.readFileSync(targetPath));
});

// Market Prices (CSV/APMC dataset)
app.get(["/api/market-prices", "/api/market/prices"], (req, res) => {
  const district = String(req.query.district ?? "All").trim();
  const search = String(req.query.search ?? "").trim().toLowerCase();
  const sort = String(req.query.sort ?? "date_desc").trim().toLowerCase();

  let filtered = marketRows.slice();
  if (district && district.toLowerCase() !== "all") {
    filtered = filtered.filter((r) => r.district.toLowerCase() === district.toLowerCase());
  }
  if (search) {
    filtered = filtered.filter(
      (r) =>
        r.crop.toLowerCase().includes(search) ||
        r.district.toLowerCase().includes(search)
    );
  }

  filtered.sort((a, b) => {
    if (sort === "price_asc") return a.price - b.price || a.crop.localeCompare(b.crop);
    if (sort === "price_desc") return b.price - a.price || a.crop.localeCompare(b.crop);
    if (sort === "crop_asc") return a.crop.localeCompare(b.crop) || a.district.localeCompare(b.district);
    return b.date.localeCompare(a.date) || a.crop.localeCompare(b.crop) || a.district.localeCompare(b.district);
  });

  const districts = Array.from(new Set(marketRows.map((r) => r.district))).sort();
  res.json({
    success: true,
    data: filtered.slice(0, 250),
    districts,
    total: filtered.length,
  });
});

// Real-time Crop Details Search (Dataset stats + bilingual catalog + APMC market summary)
app.get("/api/crops/search", (req, res) => {
  const queryText = String(req.query.q ?? "").trim().toLowerCase();
  const results = Object.entries(CROP_DETAILS_CATALOG)
    .filter(([key, meta]) => {
      if (!queryText) return true;
      const haystack = `${key} ${meta.name_en} ${meta.name_ta} ${meta.desc_en} ${meta.desc_ta}`.toLowerCase();
      return haystack.includes(queryText);
    })
    .map(([key, meta]) => {
      const stats = cropDatasetStats[key] ?? null;
      return {
        key,
        name_en: meta.name_en,
        name_ta: meta.name_ta,
        icon: meta.icon,
        desc_en: meta.desc_en,
        desc_ta: meta.desc_ta,
        is_ml_crop: stats !== null,
        stats,
        market: marketSummaryByCrop[key] ?? marketSummaryByCrop[meta.name_en.toLowerCase()] ?? null,
      };
    })
    .sort((a, b) => {
      const aStarts = queryText && a.name_en.toLowerCase().startsWith(queryText) ? 0 : 1;
      const bStarts = queryText && b.name_en.toLowerCase().startsWith(queryText) ? 0 : 1;
      if (aStarts !== bStarts) return aStarts - bStarts;
      if (a.is_ml_crop !== b.is_ml_crop) return a.is_ml_crop ? -1 : 1;
      return a.name_en.localeCompare(b.name_en);
    });

  res.json({ success: true, data: results, total: results.length });
});

// Live + Historical Weather
app.get(["/api/weather", "/api/weather/data"], async (req, res) => {
  const district = String(req.query.district ?? "").trim();
  const mode = String(req.query.mode ?? "all").trim().toLowerCase();

  let targetDistricts = Object.keys(DISTRICT_COORDS);
  let filterName = "";

  if (district && district.toLowerCase() !== "all") {
    const matched = targetDistricts.find((d) => d.toLowerCase() === district.toLowerCase());
    if (!matched) {
      res.status(400).json({
        success: false,
        error: `Unknown district '${district}'. Choose a valid Tamil Nadu district.`,
      });
      return;
    }
    targetDistricts = [matched];
    filterName = matched;
  }

  let liveList: WeatherRow[] = [];
  let liveError: string | null = null;
  if (mode === "all" || mode === "live") {
    const live = await getLiveWeather(targetDistricts);
    liveList = live.records;
    liveError = live.error;
  }

  let histList: WeatherRow[] = [];
  if (mode === "all" || mode === "historical" || (mode === "live" && liveList.length === 0)) {
    histList = filterName
      ? historicalWeather.filter((w) => w.district.toLowerCase() === filterName.toLowerCase())
      : historicalWeather;
  }

  res.json({
    success: true,
    data: liveList.length > 0 ? liveList : histList,
    live_data: liveList,
    historical_data: histList,
    live_available: liveList.length > 0,
    live_error: liveError,
    districts: Object.keys(DISTRICT_COORDS).sort(),
  });
});

app.use((req, res) => {
  if (req.path.startsWith("/api/")) {
    res.status(404).json({ success: false, error: "API endpoint not found" });
    return;
  }
  renderHtmlPage("home", req, res);
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Smart Agri AI server listening on http://0.0.0.0:${PORT}`);
});
