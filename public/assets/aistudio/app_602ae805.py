"""
Smart Agri AI — Flask Backend
Complete integration with PlantVillage disease model
"""

import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import traceback

app = Flask(__name__)
CORS(app)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─── FULL PLANTVILLAGE DISEASE DATABASE ───────────────────────────────────────
DISEASE_DB = {
    "Apple___Apple_scab": {
        "disease_name": "Apple Scab",
        "disease_name_ta": "ஆப்பிள் ஸ்கேப்",
        "severity": "medium",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "treatment_en": (
            "1. Apply fungicides containing Myclobutanil or Captan at bud break.\n"
            "2. Remove and destroy all infected leaves and fallen fruit.\n"
            "3. Prune trees to improve air circulation and reduce humidity.\n"
            "4. Apply lime sulfur sprays during dormant season.\n"
            "5. Avoid overhead irrigation; use drip irrigation instead.\n"
            "6. Repeat fungicide application every 7–10 days during wet periods."
        ),
        "treatment_ta": (
            "1. மொட்டு விரியும் போது Myclobutanil அல்லது Captan கொண்ட பூஞ்சை மருந்தை தெளிக்கவும்.\n"
            "2. பாதிக்கப்பட்ட இலைகள் மற்றும் விழுந்த பழங்களை அகற்றி அழிக்கவும்.\n"
            "3. காற்று சுழற்சியை மேம்படுத்த மரங்களை கத்தரிக்கவும்.\n"
            "4. உறக்க காலத்தில் சுண்ணாம்பு கந்தக தெளிப்பு பயன்படுத்தவும்.\n"
            "5. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்; சொட்டு நீர்ப்பாசனம் பயன்படுத்தவும்.\n"
            "6. ஈர காலங்களில் ஒவ்வொரு 7–10 நாட்களுக்கு பூஞ்சை மருந்து தெளிக்கவும்."
        )
    },
    "Apple___Black_rot": {
        "disease_name": "Apple Black Rot",
        "disease_name_ta": "ஆப்பிள் கருப்பு அழுகல்",
        "severity": "high",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "treatment_en": (
            "1. Remove and destroy mummified fruit and cankers immediately.\n"
            "2. Apply Captan or Thiophanate-methyl fungicide every 10–14 days.\n"
            "3. Prune out all dead and diseased wood back to healthy tissue.\n"
            "4. Disinfect pruning tools with 70% isopropyl alcohol between cuts.\n"
            "5. Avoid wounding trees during wet weather.\n"
            "6. Apply protective fungicide sprays from pink stage through harvest."
        ),
        "treatment_ta": (
            "1. உலர்ந்த பழங்கள் மற்றும் புண்களை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "2. ஒவ்வொரு 10–14 நாட்களுக்கு Captan அல்லது Thiophanate-methyl தெளிக்கவும்.\n"
            "3. இறந்த மற்றும் நோய்வாய்ப்பட்ட மரக்கிளைகளை ஆரோக்கியமான திசு வரை கத்தரிக்கவும்.\n"
            "4. ஒவ்வொரு வெட்டுக்கும் இடையில் 70% ஐசோப்ரோப்பில் ஆல்கஹால் கொண்டு கருவிகளை கிருமி நீக்கம் செய்யவும்.\n"
            "5. ஈர வானிலையில் மரங்களை காயப்படுத்துவதை தவிர்க்கவும்.\n"
            "6. இளஞ்சிவப்பு நிலையிலிருந்து அறுவடை வரை பாதுகாப்பு பூஞ்சை மருந்து தெளிக்கவும்."
        )
    },
    "Apple___Cedar_apple_rust": {
        "disease_name": "Cedar Apple Rust",
        "disease_name_ta": "சீடர் ஆப்பிள் துரு",
        "severity": "medium",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "treatment_en": (
            "1. Apply Myclobutanil fungicide from pink bud stage through petal fall.\n"
            "2. Remove nearby juniper/cedar trees that host the alternate stage.\n"
            "3. Apply fungicide every 7–10 days during infection periods (wet spring).\n"
            "4. Plant rust-resistant apple varieties when possible.\n"
            "5. Remove and destroy infected leaves immediately."
        ),
        "treatment_ta": (
            "1. இளஞ்சிவப்பு மொட்டு நிலையிலிருந்து இதழ் உதிர்வு வரை Myclobutanil தெளிக்கவும்.\n"
            "2. மாற்று நிலையை தாங்கும் அருகிலுள்ள ஜுனிபர்/சீடர் மரங்களை அகற்றவும்.\n"
            "3. நோய் தாக்கும் காலத்தில் (ஈர வசந்தம்) ஒவ்வொரு 7–10 நாட்களுக்கு பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "4. சாத்தியமான போது துரு-எதிர்ப்பு ஆப்பிள் வகைகளை நடவு செய்யவும்.\n"
            "5. பாதிக்கப்பட்ட இலைகளை உடனடியாக அகற்றி அழிக்கவும்."
        )
    },
    "Apple___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "treatment_en": "✅ Your apple plant looks healthy! Continue regular monitoring, proper irrigation, and seasonal fertilization. Maintain good orchard hygiene.",
        "treatment_ta": "✅ உங்கள் ஆப்பிள் செடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு, சரியான நீர்ப்பாசனம் மற்றும் பருவகால உரமிடுதல் தொடருங்கள்."
    },
    "Blueberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Blueberry",
        "crop_name_ta": "ப்ளூபெர்ரி",
        "treatment_en": "✅ Your blueberry plant looks healthy! Maintain acidic soil (pH 4.5–5.5), proper mulching, and regular monitoring.",
        "treatment_ta": "✅ உங்கள் ப்ளூபெர்ரி செடி ஆரோக்கியமாக உள்ளது! அமில மண் (pH 4.5–5.5), சரியான மல்ச்சிங் மற்றும் தொடர்ந்து கண்காணிப்பு பராமரிக்கவும்."
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "disease_name_ta": "தூள் பூஞ்சை",
        "severity": "medium",
        "crop_name": "Cherry",
        "crop_name_ta": "செர்ரி",
        "treatment_en": (
            "1. Apply sulfur-based fungicide or potassium bicarbonate sprays.\n"
            "2. Prune and destroy infected shoots immediately.\n"
            "3. Avoid excessive nitrogen fertilization.\n"
            "4. Improve air circulation by proper pruning.\n"
            "5. Apply Myclobutanil or Trifloxystrobin at first sign of infection.\n"
            "6. Avoid wetting foliage during irrigation."
        ),
        "treatment_ta": (
            "1. கந்தக அடிப்படையிலான பூஞ்சை மருந்து அல்லது பொட்டாசியம் பைகார்பனேட் தெளிப்பு பயன்படுத்தவும்.\n"
            "2. பாதிக்கப்பட்ட தளிர்களை உடனடியாக கத்தரித்து அழிக்கவும்.\n"
            "3. அதிகப்படியான நைட்ரஜன் உரமிடுதலை தவிர்க்கவும்.\n"
            "4. சரியான கத்தரிப்பு மூலம் காற்று சுழற்சியை மேம்படுத்தவும்.\n"
            "5. நோய் தொற்றின் முதல் அறிகுறியில் Myclobutanil அல்லது Trifloxystrobin பயன்படுத்தவும்.\n"
            "6. நீர்ப்பாசனத்தின் போது இலைகளை நனைப்பதை தவிர்க்கவும்."
        )
    },
    "Cherry_(including_sour)___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Cherry",
        "crop_name_ta": "செர்ரி",
        "treatment_en": "✅ Your cherry plant looks healthy! Continue proper care with balanced fertilization and regular monitoring.",
        "treatment_ta": "✅ உங்கள் செர்ரி செடி ஆரோக்கியமாக உள்ளது! சமநிலையான உரமிடுதல் மற்றும் தொடர்ந்து கண்காணிப்புடன் சரியான பராமரிப்பை தொடருங்கள்."
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "disease_name": "Gray Leaf Spot",
        "disease_name_ta": "சாம்பல் இலை புள்ளி",
        "severity": "medium",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "treatment_en": (
            "1. Apply Azoxystrobin or Propiconazole fungicide at first sign of disease.\n"
            "2. Plant resistant hybrid varieties in future seasons.\n"
            "3. Rotate crops — avoid consecutive corn plantings.\n"
            "4. Till infected residue into soil after harvest.\n"
            "5. Ensure proper plant spacing for air circulation.\n"
            "6. Monitor fields regularly from tasseling stage onwards."
        ),
        "treatment_ta": (
            "1. நோயின் முதல் அறிகுறியில் Azoxystrobin அல்லது Propiconazole பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. எதிர்கால பருவங்களில் எதிர்ப்பு சக்தி கொண்ட கலப்பின வகைகளை நடவு செய்யவும்.\n"
            "3. பயிர் சுழற்சி பின்பற்றவும் — தொடர்ச்சியான சோள நடவுகளை தவிர்க்கவும்.\n"
            "4. அறுவடைக்கு பின் பாதிக்கப்பட்ட எச்சங்களை மண்ணில் கலக்கவும்.\n"
            "5. காற்று சுழற்சிக்கு சரியான தாவர இடைவெளி உறுதி செய்யவும்.\n"
            "6. தாசல் நிலையிலிருந்து தொடர்ந்து வயல்களை கண்காணிக்கவும்."
        )
    },
    "Corn_(maize)___Common_rust_": {
        "disease_name": "Common Rust",
        "disease_name_ta": "பொதுவான துரு நோய்",
        "severity": "medium",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "treatment_en": (
            "1. Apply Mancozeb (2.5 g/L) or Propiconazole fungicide spray.\n"
            "2. Use resistant varieties — rust-resistant hybrids are available.\n"
            "3. Plant early to avoid peak rust infection periods.\n"
            "4. Apply fungicide at silking stage if rust is observed.\n"
            "5. Avoid excessive nitrogen fertilization.\n"
            "6. Repeat spraying every 10–14 days if infection persists."
        ),
        "treatment_ta": (
            "1. Mancozeb (2.5 g/L) அல்லது Propiconazole பூஞ்சை மருந்து தெளிப்பு பயன்படுத்தவும்.\n"
            "2. எதிர்ப்பு சக்தி கொண்ட வகைகளை பயன்படுத்தவும் — துரு-எதிர்ப்பு கலப்பினங்கள் கிடைக்கின்றன.\n"
            "3. உச்ச துரு தொற்று காலங்களை தவிர்க்க ஆரம்பத்தில் நடவு செய்யவும்.\n"
            "4. துரு கண்டறியப்பட்டால் பட்டு நிலையில் பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "5. அதிகப்படியான நைட்ரஜன் உரமிடுதலை தவிர்க்கவும்.\n"
            "6. நோய் தொடர்ந்தால் ஒவ்வொரு 10–14 நாட்களுக்கு மீண்டும் தெளிக்கவும்."
        )
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "disease_name": "Northern Leaf Blight",
        "disease_name_ta": "வடக்கு இலை கருகல்",
        "severity": "high",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "treatment_en": (
            "1. Apply Azoxystrobin + Propiconazole fungicide at early infection stage.\n"
            "2. Plant resistant or tolerant hybrids in future seasons.\n"
            "3. Crop rotation — plant non-host crops for 1–2 seasons.\n"
            "4. Deep plow infected residues after harvest.\n"
            "5. Apply fungicide at VT (tasseling) to R1 (silking) growth stage.\n"
            "6. Avoid water stress during critical growth periods."
        ),
        "treatment_ta": (
            "1. ஆரம்ப தொற்று நிலையில் Azoxystrobin + Propiconazole பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. எதிர்கால பருவங்களில் எதிர்ப்பு சக்தி கொண்ட அல்லது சகிப்புத்தன்மை கொண்ட கலப்பினங்களை நடவு செய்யவும்.\n"
            "3. பயிர் சுழற்சி — 1–2 பருவங்களுக்கு புரவலனல்லாத பயிர்களை நடவு செய்யவும்.\n"
            "4. அறுவடைக்கு பின் பாதிக்கப்பட்ட எச்சங்களை ஆழமாக உழவு செய்யவும்.\n"
            "5. VT (தாசல்) முதல் R1 (பட்டு) வளர்ச்சி நிலையில் பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "6. முக்கிய வளர்ச்சி காலங்களில் நீர் அழுத்தத்தை தவிர்க்கவும்."
        )
    },
    "Corn_(maize)___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "treatment_en": "✅ Your corn plant looks healthy! Continue balanced NPK fertilization, proper irrigation, and regular field monitoring.",
        "treatment_ta": "✅ உங்கள் சோள செடி ஆரோக்கியமாக உள்ளது! சமநிலையான NPK உரமிடுதல், சரியான நீர்ப்பாசனம் மற்றும் தொடர்ந்து வயல் கண்காணிப்பை தொடருங்கள்."
    },
    "Grape___Black_rot": {
        "disease_name": "Grape Black Rot",
        "disease_name_ta": "திராட்சை கருப்பு அழுகல்",
        "severity": "high",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "treatment_en": (
            "1. Apply Myclobutanil or Mancozeb from budbreak through berry set.\n"
            "2. Remove and destroy mummified berries and infected canes.\n"
            "3. Prune vines to improve air circulation and reduce canopy density.\n"
            "4. Apply fungicide every 10–14 days during wet weather.\n"
            "5. Avoid overhead irrigation; use drip system.\n"
            "6. Train vines on trellises to keep fruit off the ground."
        ),
        "treatment_ta": (
            "1. மொட்டு விரிதலிலிருந்து காய் பிடித்தல் வரை Myclobutanil அல்லது Mancozeb தெளிக்கவும்.\n"
            "2. உலர்ந்த திராட்சைகள் மற்றும் பாதிக்கப்பட்ட கொடிகளை அகற்றி அழிக்கவும்.\n"
            "3. காற்று சுழற்சியை மேம்படுத்த கொடியை கத்தரிக்கவும்.\n"
            "4. ஈர வானிலையில் ஒவ்வொரு 10–14 நாட்களுக்கு பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "5. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்; சொட்டு முறை பயன்படுத்தவும்.\n"
            "6. பழங்கள் தரையில் படாமல் இருக்க கம்பிகளில் கொடியை பயிற்சி செய்யவும்."
        )
    },
    "Grape___Esca_(Black_Measles)": {
        "disease_name": "Esca (Black Measles)",
        "disease_name_ta": "எஸ்கா (கருப்பு தட்டம்மை)",
        "severity": "high",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "treatment_en": (
            "1. No complete cure — focus on management and prevention.\n"
            "2. Remove and destroy severely infected vines.\n"
            "3. Protect pruning wounds with fungicidal paste (Trichoderma-based).\n"
            "4. Prune during dry weather; avoid rainy seasons.\n"
            "5. Disinfect pruning tools between plants.\n"
            "6. Apply sodium arsenite (where legally permitted) as trunk injection."
        ),
        "treatment_ta": (
            "1. முழுமையான சிகிச்சை இல்லை — மேலாண்மை மற்றும் தடுப்பில் கவனம் செலுத்தவும்.\n"
            "2. கடுமையாக பாதிக்கப்பட்ட கொடிகளை அகற்றி அழிக்கவும்.\n"
            "3. கத்தரிப்பு புண்களை பூஞ்சை மருந்து பேஸ்ட் (Trichoderma-அடிப்படையிலான) கொண்டு பாதுகாக்கவும்.\n"
            "4. வறண்ட வானிலையில் கத்தரிக்கவும்; மழை பருவங்களை தவிர்க்கவும்.\n"
            "5. செடிகளுக்கு இடையில் கத்தரிப்பு கருவிகளை கிருமி நீக்கம் செய்யவும்.\n"
            "6. சட்டப்படி அனுமதிக்கப்பட்ட இடங்களில் தண்டு ஊசி மூலம் சோடியம் ஆர்சனைட் பயன்படுத்தவும்."
        )
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "disease_name": "Leaf Blight",
        "disease_name_ta": "இலை கருகல்",
        "severity": "medium",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "treatment_en": (
            "1. Apply copper-based fungicide (Bordeaux mixture 1%) at first sign.\n"
            "2. Remove and destroy infected leaves.\n"
            "3. Improve air circulation by thinning the canopy.\n"
            "4. Apply Mancozeb or Zineb fungicide every 10–14 days.\n"
            "5. Avoid wetting foliage; use drip irrigation.\n"
            "6. Maintain proper vine spacing."
        ),
        "treatment_ta": (
            "1. முதல் அறிகுறியில் தாமிர-அடிப்படையிலான பூஞ்சை மருந்து (போர்டோ கலவை 1%) தெளிக்கவும்.\n"
            "2. பாதிக்கப்பட்ட இலைகளை அகற்றி அழிக்கவும்.\n"
            "3. கொடியை மெலிக்க வேண்டும் — காற்று சுழற்சியை மேம்படுத்தவும்.\n"
            "4. ஒவ்வொரு 10–14 நாட்களுக்கு Mancozeb அல்லது Zineb தெளிக்கவும்.\n"
            "5. இலைகளை நனைப்பதை தவிர்க்கவும்; சொட்டு நீர்ப்பாசனம் பயன்படுத்தவும்.\n"
            "6. சரியான கொடி இடைவெளி பராமரிக்கவும்."
        )
    },
    "Grape___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "treatment_en": "✅ Your grape vine looks healthy! Continue regular monitoring, proper pruning, and balanced fertilization.",
        "treatment_ta": "✅ உங்கள் திராட்சை கொடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு, சரியான கத்தரிப்பு மற்றும் சமநிலையான உரமிடுதலை தொடருங்கள்."
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "disease_name": "Citrus Greening (HLB)",
        "disease_name_ta": "சிட்ரஸ் பச்சையாதல் (HLB)",
        "severity": "high",
        "crop_name": "Orange",
        "crop_name_ta": "ஆரஞ்சு",
        "treatment_en": (
            "1. No cure exists — infected trees must be removed and destroyed.\n"
            "2. Control Asian citrus psyllid (vector) with insecticides (Imidacloprid).\n"
            "3. Use certified disease-free planting material only.\n"
            "4. Apply reflective mulches to deter psyllid movement.\n"
            "5. Regularly inspect trees for symptoms.\n"
            "6. Notify local agricultural authorities if HLB is suspected."
        ),
        "treatment_ta": (
            "1. சிகிச்சை இல்லை — பாதிக்கப்பட்ட மரங்களை அகற்றி அழிக்க வேண்டும்.\n"
            "2. ஆசிய சிட்ரஸ் சிட்லை (வாகனம்) பூச்சி மருந்துகளால் (Imidacloprid) கட்டுப்படுத்தவும்.\n"
            "3. சான்றளிக்கப்பட்ட நோயற்ற நடவு பொருட்களை மட்டுமே பயன்படுத்தவும்.\n"
            "4. சிட்லை இயக்கத்தை தடுக்க பிரதிபலிப்பு மல்ச்களை பயன்படுத்தவும்.\n"
            "5. அறிகுறிகளுக்கு மரங்களை தொடர்ந்து ஆய்வு செய்யவும்.\n"
            "6. HLB சந்தேகப்பட்டால் உள்ளூர் விவசாய அதிகாரிகளுக்கு தெரியப்படுத்தவும்."
        )
    },
    "Peach___Bacterial_spot": {
        "disease_name": "Peach Bacterial Spot",
        "disease_name_ta": "பீச் பாக்டீரியல் புள்ளி",
        "severity": "medium",
        "crop_name": "Peach",
        "crop_name_ta": "பீச்",
        "treatment_en": (
            "1. Apply copper-based bactericide sprays (Bordeaux mixture) from pre-bloom.\n"
            "2. Apply Oxytetracycline antibiotic during bloom period.\n"
            "3. Plant resistant peach varieties where available.\n"
            "4. Prune infected branches; destroy infected material.\n"
            "5. Avoid overhead irrigation.\n"
            "6. Apply zinc sulfate during dormant season."
        ),
        "treatment_ta": (
            "1. மலர் முன் நிலையிலிருந்து தாமிர-அடிப்படையிலான பாக்டீரியா மருந்து (போர்டோ கலவை) தெளிக்கவும்.\n"
            "2. மலர்ச்சி காலத்தில் Oxytetracycline நுண்ணுயிர் எதிர்ப்பி தெளிக்கவும்.\n"
            "3. கிடைக்கக்கூடிய இடங்களில் எதிர்ப்பு சக்தி கொண்ட பீச் வகைகளை நடவு செய்யவும்.\n"
            "4. பாதிக்கப்பட்ட கிளைகளை கத்தரிக்கவும்; பாதிக்கப்பட்ட பொருட்களை அழிக்கவும்.\n"
            "5. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்.\n"
            "6. உறக்க பருவத்தில் ஜிங்க் சல்பேட் தெளிக்கவும்."
        )
    },
    "Peach___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Peach",
        "crop_name_ta": "பீச்",
        "treatment_en": "✅ Your peach plant looks healthy! Maintain proper nutrition, irrigation, and regular monitoring.",
        "treatment_ta": "✅ உங்கள் பீச் செடி ஆரோக்கியமாக உள்ளது! சரியான ஊட்டச்சத்து, நீர்ப்பாசனம் மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்."
    },
    "Pepper,_bell___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "disease_name_ta": "பாக்டீரியல் புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Bell Pepper",
        "crop_name_ta": "குடை மிளகாய்",
        "treatment_en": (
            "1. Apply copper hydroxide (0.1%) spray every 7–10 days.\n"
            "2. Use certified disease-free seeds and transplants.\n"
            "3. Avoid overhead irrigation; use drip system.\n"
            "4. Remove and destroy infected plant material immediately.\n"
            "5. Rotate crops — avoid peppers/tomatoes in same field for 2+ seasons.\n"
            "6. Disinfect tools and equipment regularly."
        ),
        "treatment_ta": (
            "1. ஒவ்வொரு 7–10 நாட்களுக்கு தாமிர ஹைட்ராக்சைடு (0.1%) தெளிக்கவும்.\n"
            "2. சான்றளிக்கப்பட்ட நோயற்ற விதைகள் மற்றும் நாற்றுகளை பயன்படுத்தவும்.\n"
            "3. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்; சொட்டு முறை பயன்படுத்தவும்.\n"
            "4. பாதிக்கப்பட்ட தாவர பொருட்களை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "5. பயிர் சுழற்சி — 2+ பருவங்களுக்கு அதே வயலில் மிளகாய்/தக்காளி தவிர்க்கவும்.\n"
            "6. கருவிகள் மற்றும் உபகரணங்களை தொடர்ந்து கிருமி நீக்கம் செய்யவும்."
        )
    },
    "Pepper,_bell___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Bell Pepper",
        "crop_name_ta": "குடை மிளகாய்",
        "treatment_en": "✅ Your pepper plant looks healthy! Continue regular monitoring and balanced fertilization.",
        "treatment_ta": "✅ உங்கள் மிளகாய் செடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு மற்றும் சமநிலையான உரமிடுதலை தொடருங்கள்."
    },
    "Potato___Early_blight": {
        "disease_name": "Early Blight",
        "disease_name_ta": "ஆரம்ப கருகல் நோய்",
        "severity": "medium",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "treatment_en": (
            "1. Apply Mancozeb (2.5 g/L) or Chlorothalonil fungicide spray.\n"
            "2. Spray every 7–10 days starting from disease appearance.\n"
            "3. Remove and destroy infected lower leaves.\n"
            "4. Avoid excessive nitrogen fertilization.\n"
            "5. Maintain proper soil moisture — avoid waterlogging.\n"
            "6. Use certified disease-free seed tubers.\n"
            "7. Practice crop rotation — avoid solanaceous crops."
        ),
        "treatment_ta": (
            "1. Mancozeb (2.5 g/L) அல்லது Chlorothalonil பூஞ்சை மருந்து தெளிப்பு தெளிக்கவும்.\n"
            "2. நோய் தோன்றிய நாளிலிருந்து ஒவ்வொரு 7–10 நாட்களுக்கு தெளிக்கவும்.\n"
            "3. பாதிக்கப்பட்ட கீழ் இலைகளை அகற்றி அழிக்கவும்.\n"
            "4. அதிகப்படியான நைட்ரஜன் உரமிடுதலை தவிர்க்கவும்.\n"
            "5. சரியான மண் ஈரப்பதம் பராமரிக்கவும் — நீர் தேங்குவதை தவிர்க்கவும்.\n"
            "6. சான்றளிக்கப்பட்ட நோயற்ற விதை கிழங்குகளை பயன்படுத்தவும்.\n"
            "7. பயிர் சுழற்சி பின்பற்றவும் — சோலனேசியஸ் பயிர்களை தவிர்க்கவும்."
        )
    },
    "Potato___Late_blight": {
        "disease_name": "Late Blight",
        "disease_name_ta": "தாமத கருகல் நோய்",
        "severity": "high",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "treatment_en": (
            "1. Apply Metalaxyl + Mancozeb (Ridomil Gold) immediately at first sign.\n"
            "2. Spray every 5–7 days during wet, cool weather.\n"
            "3. Destroy all infected plant material — do NOT compost.\n"
            "4. Hill up soil around plants to protect tubers.\n"
            "5. Harvest tubers in dry conditions; allow to dry before storage.\n"
            "6. Plant resistant varieties (e.g., Kufri Jyoti, Kufri Bahar).\n"
            "7. Avoid overhead irrigation."
        ),
        "treatment_ta": (
            "1. முதல் அறிகுறியில் உடனடியாக Metalaxyl + Mancozeb (Ridomil Gold) தெளிக்கவும்.\n"
            "2. ஈர, குளிர் வானிலையில் ஒவ்வொரு 5–7 நாட்களுக்கு தெளிக்கவும்.\n"
            "3. அனைத்து பாதிக்கப்பட்ட தாவர பொருட்களை அழிக்கவும் — உரமாக்கல் கூடாது.\n"
            "4. கிழங்குகளை பாதுகாக்க செடிகளை சுற்றி மண் திரட்டவும்.\n"
            "5. வறண்ட நிலையில் கிழங்குகளை அறுவடை செய்யவும்; சேமிக்கும் முன் காய வைக்கவும்.\n"
            "6. எதிர்ப்பு சக்தி கொண்ட வகைகளை நடவு செய்யவும் (உ.கா., Kufri Jyoti, Kufri Bahar).\n"
            "7. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்."
        )
    },
    "Potato___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "treatment_en": "✅ Your potato plant looks healthy! Maintain proper hilling, balanced NPK fertilization, and regular monitoring.",
        "treatment_ta": "✅ உங்கள் உருளைக்கிழங்கு செடி ஆரோக்கியமாக உள்ளது! சரியான மண் திரட்டல், சமநிலையான NPK உரமிடுதல் மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்."
    },
    "Raspberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Raspberry",
        "crop_name_ta": "ராஸ்பெர்ரி",
        "treatment_en": "✅ Your raspberry plant looks healthy! Continue proper pruning, mulching, and regular monitoring for pests.",
        "treatment_ta": "✅ உங்கள் ராஸ்பெர்ரி செடி ஆரோக்கியமாக உள்ளது! சரியான கத்தரிப்பு, மல்ச்சிங் மற்றும் பூச்சிகளுக்கான தொடர்ந்து கண்காணிப்பை தொடருங்கள்."
    },
    "Rice___Brown_Spot": {
        "disease_name": "Brown Spot",
        "disease_name_ta": "பழுப்பு புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "treatment_en": (
            "1. Apply Mancozeb (2.5 g/L) or Edifenphos (1 ml/L) fungicide.\n"
            "2. Treat seeds with Thiram or Captan before sowing (2.5 g/kg seed).\n"
            "3. Use balanced NPK fertilization — correct potassium deficiency.\n"
            "4. Avoid waterlogging; maintain proper water level.\n"
            "5. Spray Propiconazole (0.1%) at booting stage.\n"
            "6. Use resistant varieties recommended by state agriculture dept."
        ),
        "treatment_ta": (
            "1. Mancozeb (2.5 g/L) அல்லது Edifenphos (1 ml/L) பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. விதைப்பதற்கு முன் விதைகளை Thiram அல்லது Captan கொண்டு சிகிச்சை செய்யவும் (2.5 g/kg விதை).\n"
            "3. சமநிலையான NPK உரமிடுதல் பயன்படுத்தவும் — பொட்டாசியம் குறைபாட்டை சரிசெய்யவும்.\n"
            "4. நீர் தேங்குவதை தவிர்க்கவும்; சரியான நீர் மட்டம் பராமரிக்கவும்.\n"
            "5. பூட்டிங் நிலையில் Propiconazole (0.1%) தெளிக்கவும்.\n"
            "6. மாநில விவசாய துறை பரிந்துரைத்த எதிர்ப்பு வகைகளை பயன்படுத்தவும்."
        )
    },
    "Rice___Hispa": {
        "disease_name": "Rice Hispa",
        "disease_name_ta": "நெல் ஹிஸ்பா",
        "severity": "medium",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "treatment_en": (
            "1. Apply Chlorpyrifos (2 ml/L) or Malathion (1.5 ml/L) spray.\n"
            "2. Clip and destroy infested leaf tips to remove eggs and grubs.\n"
            "3. Avoid close planting — maintain proper spacing.\n"
            "4. Keep field bunds weed-free to eliminate alternate hosts.\n"
            "5. Apply Carbofuran (3G) at 1 kg a.i./ha in standing water.\n"
            "6. Release natural predators if available."
        ),
        "treatment_ta": (
            "1. Chlorpyrifos (2 ml/L) அல்லது Malathion (1.5 ml/L) தெளிப்பு தெளிக்கவும்.\n"
            "2. முட்டைகள் மற்றும் புழுக்களை அகற்ற பாதிக்கப்பட்ட இலை நுனிகளை ஒடித்து அழிக்கவும்.\n"
            "3. நெருக்கமாக நடவு செய்வதை தவிர்க்கவும் — சரியான இடைவெளி பராமரிக்கவும்.\n"
            "4. மாற்று புரவலர்களை ஒழிக்க வயல் வரம்புகளை களை நீக்கம் செய்யவும்.\n"
            "5. நிற்கும் நீரில் Carbofuran (3G) 1 kg a.i./ha தெளிக்கவும்.\n"
            "6. கிடைத்தால் இயற்கை வேட்டையாடிகளை விடவும்."
        )
    },
    "Rice___Leaf_Blast": {
        "disease_name": "Leaf Blast",
        "disease_name_ta": "இலை வெடிப்பு நோய்",
        "severity": "high",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "treatment_en": (
            "1. Apply Tricyclazole (0.6 g/L) or Isoprothiolane (1.5 ml/L) immediately.\n"
            "2. Spray at tillering and booting stages preventively.\n"
            "3. Avoid excessive nitrogen fertilization — split application recommended.\n"
            "4. Drain water from fields during blast-prone periods.\n"
            "5. Plant blast-resistant varieties (IR64, Swarna Sub1).\n"
            "6. Treat seeds with Carbendazim (2g/kg) before sowing."
        ),
        "treatment_ta": (
            "1. உடனடியாக Tricyclazole (0.6 g/L) அல்லது Isoprothiolane (1.5 ml/L) தெளிக்கவும்.\n"
            "2. தளிர் மற்றும் பூட்டிங் நிலைகளில் தடுப்பு முறையில் தெளிக்கவும்.\n"
            "3. அதிகப்படியான நைட்ரஜன் உரமிடுதலை தவிர்க்கவும் — பகுதி பயன்பாடு பரிந்துரைக்கப்படுகிறது.\n"
            "4. வெடிப்பு-ஆபத்தான காலங்களில் வயல்களிலிருந்து நீரை வடிக்கட்டவும்.\n"
            "5. வெடிப்பு-எதிர்ப்பு வகைகளை நடவு செய்யவும் (IR64, Swarna Sub1).\n"
            "6. விதைப்பதற்கு முன் Carbendazim (2g/kg) கொண்டு விதை சிகிச்சை செய்யவும்."
        )
    },
    "Rice___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "treatment_en": "✅ Your rice plant looks healthy! Maintain proper water management, balanced NPK fertilization, and regular field monitoring.",
        "treatment_ta": "✅ உங்கள் நெல் செடி ஆரோக்கியமாக உள்ளது! சரியான நீர் மேலாண்மை, சமநிலையான NPK உரமிடுதல் மற்றும் தொடர்ந்து வயல் கண்காணிப்பை பராமரிக்கவும்."
    },
    "Soybean___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Soybean",
        "crop_name_ta": "சோயாபீன்",
        "treatment_en": "✅ Your soybean plant looks healthy! Maintain balanced fertilization and proper weed management.",
        "treatment_ta": "✅ உங்கள் சோயாபீன் செடி ஆரோக்கியமாக உள்ளது! சமநிலையான உரமிடுதல் மற்றும் சரியான களை மேலாண்மையை பராமரிக்கவும்."
    },
    "Squash___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "disease_name_ta": "தூள் பூஞ்சை நோய்",
        "severity": "medium",
        "crop_name": "Squash",
        "crop_name_ta": "சுரைக்காய்",
        "treatment_en": (
            "1. Apply potassium bicarbonate (1 tbsp/gallon water) spray.\n"
            "2. Use neem oil (2%) spray as organic option.\n"
            "3. Apply Myclobutanil or Trifloxystrobin fungicide.\n"
            "4. Remove and destroy severely infected plant parts.\n"
            "5. Ensure proper plant spacing for air circulation.\n"
            "6. Avoid late-evening irrigation."
        ),
        "treatment_ta": (
            "1. பொட்டாசியம் பைகார்பனேட் (1 டேபிள்ஸ்பூன்/கேலன் தண்ணீர்) தெளிக்கவும்.\n"
            "2. கரிம விருப்பமாக வேப்ப எண்ணெய் (2%) தெளிப்பு பயன்படுத்தவும்.\n"
            "3. Myclobutanil அல்லது Trifloxystrobin பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "4. கடுமையாக பாதிக்கப்பட்ட தாவர பகுதிகளை அகற்றி அழிக்கவும்.\n"
            "5. காற்று சுழற்சிக்கு சரியான தாவர இடைவெளி உறுதி செய்யவும்.\n"
            "6. மாலை நேர நீர்ப்பாசனம் தவிர்க்கவும்."
        )
    },
    "Strawberry___Leaf_scorch": {
        "disease_name": "Leaf Scorch",
        "disease_name_ta": "இலை எரிவு நோய்",
        "severity": "medium",
        "crop_name": "Strawberry",
        "crop_name_ta": "ஸ்ட்ராபெர்ரி",
        "treatment_en": (
            "1. Apply Captan or Thiram fungicide at 7–10 day intervals.\n"
            "2. Remove and destroy infected leaves immediately.\n"
            "3. Avoid overhead irrigation — use drip irrigation.\n"
            "4. Plant resistant varieties where available.\n"
            "5. Improve air circulation by proper plant spacing.\n"
            "6. Apply copper-based fungicide as preventive measure."
        ),
        "treatment_ta": (
            "1. 7–10 நாள் இடைவெளியில் Captan அல்லது Thiram பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. பாதிக்கப்பட்ட இலைகளை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "3. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும் — சொட்டு நீர்ப்பாசனம் பயன்படுத்தவும்.\n"
            "4. கிடைக்கக்கூடிய இடங்களில் எதிர்ப்பு சக்தி கொண்ட வகைகளை நடவு செய்யவும்.\n"
            "5. சரியான தாவர இடைவெளி மூலம் காற்று சுழற்சியை மேம்படுத்தவும்.\n"
            "6. தடுப்பு நடவடிக்கையாக தாமிர-அடிப்படையிலான பூஞ்சை மருந்து தெளிக்கவும்."
        )
    },
    "Strawberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Strawberry",
        "crop_name_ta": "ஸ்ட்ராபெர்ரி",
        "treatment_en": "✅ Your strawberry plant looks healthy! Maintain proper mulching, balanced nutrition, and regular monitoring.",
        "treatment_ta": "✅ உங்கள் ஸ்ட்ராபெர்ரி செடி ஆரோக்கியமாக உள்ளது! சரியான மல்ச்சிங், சமநிலையான ஊட்டச்சத்து மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்."
    },
    "Tomato___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "disease_name_ta": "பாக்டீரியல் புள்ளி நோய்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply copper hydroxide (0.1%) or copper oxychloride (0.25%) spray.\n"
            "2. Spray every 5–7 days during wet, warm conditions.\n"
            "3. Remove and destroy severely infected plants.\n"
            "4. Avoid overhead irrigation — use drip system.\n"
            "5. Use certified disease-free seeds and transplants.\n"
            "6. Rotate crops for 2–3 seasons; avoid peppers in rotation.\n"
            "7. Disinfect tools with bleach solution (10%) regularly."
        ),
        "treatment_ta": (
            "1. தாமிர ஹைட்ராக்சைடு (0.1%) அல்லது தாமிர ஆக்சிகுளோரைடு (0.25%) தெளிக்கவும்.\n"
            "2. ஈர, வெப்பமான நிலைகளில் ஒவ்வொரு 5–7 நாட்களுக்கு தெளிக்கவும்.\n"
            "3. கடுமையாக பாதிக்கப்பட்ட செடிகளை அகற்றி அழிக்கவும்.\n"
            "4. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும் — சொட்டு முறை பயன்படுத்தவும்.\n"
            "5. சான்றளிக்கப்பட்ட நோயற்ற விதைகள் மற்றும் நாற்றுகளை பயன்படுத்தவும்.\n"
            "6. 2–3 பருவங்களுக்கு பயிர் சுழற்சி; சுழற்சியில் மிளகாய் தவிர்க்கவும்.\n"
            "7. கருவிகளை ப்ளீச் கரைசல் (10%) கொண்டு தொடர்ந்து கிருமி நீக்கம் செய்யவும்."
        )
    },
    "Tomato___Early_blight": {
        "disease_name": "Early Blight",
        "disease_name_ta": "ஆரம்ப கருகல் நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Mancozeb (2.5 g/L) or Chlorothalonil (2 g/L) fungicide.\n"
            "2. Spray every 7–10 days from disease appearance.\n"
            "3. Remove infected lower leaves immediately.\n"
            "4. Avoid working in fields when plants are wet.\n"
            "5. Mulch around plants to prevent soil splash.\n"
            "6. Ensure adequate potassium fertilization.\n"
            "7. Stake plants to improve air circulation."
        ),
        "treatment_ta": (
            "1. Mancozeb (2.5 g/L) அல்லது Chlorothalonil (2 g/L) பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. நோய் தோன்றிய நாளிலிருந்து ஒவ்வொரு 7–10 நாட்களுக்கு தெளிக்கவும்.\n"
            "3. பாதிக்கப்பட்ட கீழ் இலைகளை உடனடியாக அகற்றவும்.\n"
            "4. செடிகள் ஈரமாக இருக்கும் போது வயல்களில் வேலை செய்வதை தவிர்க்கவும்.\n"
            "5. மண் தெறிப்பை தடுக்க செடிகளை சுற்றி மல்ச் இடவும்.\n"
            "6. போதுமான பொட்டாசியம் உரமிடுதல் உறுதி செய்யவும்.\n"
            "7. காற்று சுழற்சியை மேம்படுத்த செடிகளை கட்டவும்."
        )
    },
    "Tomato___Late_blight": {
        "disease_name": "Late Blight",
        "disease_name_ta": "தாமத கருகல் நோய்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Metalaxyl + Mancozeb (Ridomil Gold MZ) immediately.\n"
            "2. Spray every 5–7 days during cool, wet weather.\n"
            "3. Remove and destroy infected plants immediately.\n"
            "4. Avoid planting near potatoes (shared pathogen).\n"
            "5. Do NOT compost infected material.\n"
            "6. Apply preventive copper spray before disease appears.\n"
            "7. Plant resistant varieties when available."
        ),
        "treatment_ta": (
            "1. உடனடியாக Metalaxyl + Mancozeb (Ridomil Gold MZ) தெளிக்கவும்.\n"
            "2. குளிர், ஈர வானிலையில் ஒவ்வொரு 5–7 நாட்களுக்கு தெளிக்கவும்.\n"
            "3. பாதிக்கப்பட்ட செடிகளை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "4. உருளைக்கிழங்கு அருகில் நடவு செய்வதை தவிர்க்கவும் (பகிரப்பட்ட நோய்க்கிருமி).\n"
            "5. பாதிக்கப்பட்ட பொருட்களை உரமாக்கல் செய்யாதீர்கள்.\n"
            "6. நோய் தோன்றுவதற்கு முன் தடுப்பு தாமிர தெளிப்பு தெளிக்கவும்.\n"
            "7. கிடைத்தால் எதிர்ப்பு சக்தி கொண்ட வகைகளை நடவு செய்யவும்."
        )
    },
    "Tomato___Leaf_Mold": {
        "disease_name": "Leaf Mold",
        "disease_name_ta": "இலை பூஞ்சை நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Mancozeb or Chlorothalonil fungicide every 7–10 days.\n"
            "2. Reduce greenhouse/field humidity by improving ventilation.\n"
            "3. Remove and destroy infected leaves.\n"
            "4. Avoid overhead irrigation.\n"
            "5. Space plants adequately for air movement.\n"
            "6. Plant resistant varieties if available."
        ),
        "treatment_ta": (
            "1. ஒவ்வொரு 7–10 நாட்களுக்கு Mancozeb அல்லது Chlorothalonil பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. காற்றோட்டத்தை மேம்படுத்துவதன் மூலம் கிரீன்ஹவுஸ்/வயல் ஈரப்பதத்தை குறைக்கவும்.\n"
            "3. பாதிக்கப்பட்ட இலைகளை அகற்றி அழிக்கவும்.\n"
            "4. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும்.\n"
            "5. காற்று இயக்கத்திற்கு செடிகளை சரியான இடைவெளியில் வைக்கவும்.\n"
            "6. கிடைத்தால் எதிர்ப்பு சக்தி கொண்ட வகைகளை நடவு செய்யவும்."
        )
    },
    "Tomato___Septoria_leaf_spot": {
        "disease_name": "Septoria Leaf Spot",
        "disease_name_ta": "செப்டோரியா இலை புள்ளி",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Chlorothalonil (2 g/L) or Mancozeb (2.5 g/L) fungicide.\n"
            "2. Remove infected lower leaves at first sign.\n"
            "3. Spray every 7–10 days during wet weather.\n"
            "4. Mulch around base of plants to prevent soil splash.\n"
            "5. Avoid working in fields when foliage is wet.\n"
            "6. Rotate crops for 2 years — avoid tomato family."
        ),
        "treatment_ta": (
            "1. Chlorothalonil (2 g/L) அல்லது Mancozeb (2.5 g/L) பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. முதல் அறிகுறியில் பாதிக்கப்பட்ட கீழ் இலைகளை அகற்றவும்.\n"
            "3. ஈர வானிலையில் ஒவ்வொரு 7–10 நாட்களுக்கு தெளிக்கவும்.\n"
            "4. மண் தெறிப்பை தடுக்க செடிகளின் அடிப்பகுதியை சுற்றி மல்ச் இடவும்.\n"
            "5. இலைகள் ஈரமாக இருக்கும் போது வயல்களில் வேலை செய்வதை தவிர்க்கவும்.\n"
            "6. 2 ஆண்டுகளுக்கு பயிர் சுழற்சி — தக்காளி குடும்பத்தை தவிர்க்கவும்."
        )
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "disease_name": "Spider Mites (Two-spotted)",
        "disease_name_ta": "சிலந்தி பூச்சிகள் (இரு புள்ளி)",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Abamectin (0.5 ml/L) or Spiromesifen miticide spray.\n"
            "2. Use neem oil (2%) as organic alternative.\n"
            "3. Spray forcefully on undersides of leaves where mites feed.\n"
            "4. Remove heavily infested leaves.\n"
            "5. Avoid using broad-spectrum insecticides (kills natural predators).\n"
            "6. Maintain adequate soil moisture — mites thrive in dry conditions.\n"
            "7. Repeat treatment every 5–7 days for 3 cycles."
        ),
        "treatment_ta": (
            "1. Abamectin (0.5 ml/L) அல்லது Spiromesifen பூச்சி மருந்து தெளிப்பு தெளிக்கவும்.\n"
            "2. கரிம மாற்றாக வேப்ப எண்ணெய் (2%) பயன்படுத்தவும்.\n"
            "3. பூச்சிகள் உண்ணும் இலைகளின் அடிப்பகுதியில் சக்தியாக தெளிக்கவும்.\n"
            "4. கடுமையாக பாதிக்கப்பட்ட இலைகளை அகற்றவும்.\n"
            "5. பரந்த-நோக்கு பூச்சி மருந்துகளை தவிர்க்கவும் (இயற்கை வேட்டையாடிகளை கொல்லும்).\n"
            "6. போதுமான மண் ஈரப்பதம் பராமரிக்கவும் — வறண்ட நிலைகளில் பூச்சிகள் தழைக்கும்.\n"
            "7. 3 சுழற்சிகளுக்கு ஒவ்வொரு 5–7 நாட்களுக்கு சிகிச்சை திரும்பவும்."
        )
    },
    "Tomato___Target_Spot": {
        "disease_name": "Target Spot",
        "disease_name_ta": "இலக்கு புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. Apply Azoxystrobin or Pyraclostrobin fungicide every 10–14 days.\n"
            "2. Remove infected lower leaves promptly.\n"
            "3. Avoid overhead irrigation — use drip system.\n"
            "4. Improve field ventilation and plant spacing.\n"
            "5. Apply preventive fungicide during high humidity periods.\n"
            "6. Crop rotation to reduce soil inoculum."
        ),
        "treatment_ta": (
            "1. ஒவ்வொரு 10–14 நாட்களுக்கு Azoxystrobin அல்லது Pyraclostrobin பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "2. பாதிக்கப்பட்ட கீழ் இலைகளை உடனடியாக அகற்றவும்.\n"
            "3. மேல்நிலை நீர்ப்பாசனம் தவிர்க்கவும் — சொட்டு முறை பயன்படுத்தவும்.\n"
            "4. வயல் காற்றோட்டம் மற்றும் தாவர இடைவெளியை மேம்படுத்தவும்.\n"
            "5. அதிக ஈரப்பதம் காலங்களில் தடுப்பு பூஞ்சை மருந்து தெளிக்கவும்.\n"
            "6. மண் நோய்க்கிருமியை குறைக்க பயிர் சுழற்சி பின்பற்றவும்."
        )
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "disease_name": "Yellow Leaf Curl Virus (TYLCV)",
        "disease_name_ta": "மஞ்சள் இலை சுருட்டை வைரஸ்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. No cure — remove and destroy infected plants immediately.\n"
            "2. Control whitefly vector with Imidacloprid (0.3 ml/L) spray.\n"
            "3. Use yellow sticky traps to monitor and reduce whitefly population.\n"
            "4. Install 40-mesh insect-proof nets in nurseries.\n"
            "5. Plant resistant/tolerant varieties (e.g., TY varieties).\n"
            "6. Apply reflective mulch to deter whitefly landing.\n"
            "7. Remove alternative host weeds around the field."
        ),
        "treatment_ta": (
            "1. சிகிச்சை இல்லை — பாதிக்கப்பட்ட செடிகளை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "2. வெள்ளை ஈ வாகனத்தை Imidacloprid (0.3 ml/L) தெளிப்பு கொண்டு கட்டுப்படுத்தவும்.\n"
            "3. வெள்ளை ஈ மக்களை கண்காணிக்க மற்றும் குறைக்க மஞ்சள் பசை பொறிகளை பயன்படுத்தவும்.\n"
            "4. நாற்றுப்பண்ணைகளில் 40-மெஷ் பூச்சி-தடுப்பு வலைகளை நிறுவுங்கள்.\n"
            "5. எதிர்ப்பு/சகிப்புத்தன்மை வகைகளை நடவு செய்யவும் (உ.கா., TY வகைகள்).\n"
            "6. வெள்ளை ஈ தரையிறங்குவதை தடுக்க பிரதிபலிப்பு மல்ச் பயன்படுத்தவும்.\n"
            "7. வயலைச் சுற்றியுள்ள மாற்று புரவலர் களைகளை அகற்றவும்."
        )
    },
    "Tomato___Tomato_mosaic_virus": {
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "disease_name_ta": "தக்காளி மொசைக் வைரஸ்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": (
            "1. No cure — remove and destroy infected plants immediately.\n"
            "2. Disinfect tools with 10% bleach or 70% alcohol between plants.\n"
            "3. Wash hands thoroughly before handling plants.\n"
            "4. Control aphid vectors with Imidacloprid or Acetamiprid.\n"
            "5. Use virus-free certified seeds.\n"
            "6. Plant resistant varieties (ToMV-resistant hybrids).\n"
            "7. Remove tobacco products before entering field (tobacco carries TMV)."
        ),
        "treatment_ta": (
            "1. சிகிச்சை இல்லை — பாதிக்கப்பட்ட செடிகளை உடனடியாக அகற்றி அழிக்கவும்.\n"
            "2. செடிகளுக்கு இடையில் கருவிகளை 10% ப்ளீச் அல்லது 70% ஆல்கஹால் கொண்டு கிருமி நீக்கம் செய்யவும்.\n"
            "3. செடிகளை கையாளுவதற்கு முன் கைகளை நன்றாக கழுவுங்கள்.\n"
            "4. Imidacloprid அல்லது Acetamiprid கொண்டு அசை பூச்சி வாகனங்களை கட்டுப்படுத்தவும்.\n"
            "5. வைரஸ் இல்லாத சான்றளிக்கப்பட்ட விதைகளை பயன்படுத்தவும்.\n"
            "6. எதிர்ப்பு சக்தி கொண்ட வகைகளை நடவு செய்யவும் (ToMV-எதிர்ப்பு கலப்பினங்கள்).\n"
            "7. வயலில் நுழைவதற்கு முன் புகையிலை பொருட்களை அகற்றுங்கள் (புகையிலை TMV தாங்கும்)."
        )
    },
    "Tomato___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "treatment_en": "✅ Your tomato plant looks healthy! Maintain balanced NPK, proper staking, regular monitoring, and adequate watering.",
        "treatment_ta": "✅ உங்கள் தக்காளி செடி ஆரோக்கியமாக உள்ளது! சமநிலையான NPK, சரியான கட்டுதல், தொடர்ந்து கண்காணிப்பு மற்றும் போதுமான நீர்ப்பாசனம் பராமரிக்கவும்."
    },
}

DEFAULT_DISEASE = {
    "disease_name": "Unknown Disease",
    "disease_name_ta": "தெரியாத நோய்",
    "severity": "medium",
    "crop_name": "Unknown Crop",
    "crop_name_ta": "தெரியாத பயிர்",
    "treatment_en": "Please consult your local agricultural extension officer for proper diagnosis and treatment recommendations.",
    "treatment_ta": "சரியான நோயறிதல் மற்றும் சிகிச்சை பரிந்துரைகளுக்கு உங்கள் உள்ளூர் விவசாய விரிவாக்க அதிகாரியை அணுகவும்."
}

# ─── MODEL LOADING ────────────────────────────────────────────────────────────
disease_model = None
class_indices = None
crop_model = None
crop_scaler = None
crop_encoder = None
market_df = None

IMG_SIZE = (224, 224)

def load_models():
    global disease_model, class_indices, crop_model, crop_scaler, crop_encoder, market_df
    try:
        import tensorflow as tf
        disease_model = tf.keras.models.load_model('disease_model.h5')
        print("✅ Disease model loaded")
    except Exception as e:
        print(f"⚠️  Disease model load failed: {e}")
    try:
        with open('class_indices.pkl', 'rb') as f:
            raw = pickle.load(f)
        if isinstance(raw, dict):
            first_val = next(iter(raw.values()))
            if isinstance(first_val, int):
                class_indices = {v: k for k, v in raw.items()}
            else:
                class_indices = raw
        print(f"✅ Class indices loaded ({len(class_indices)} classes)")
    except Exception as e:
        print(f"⚠️  Class indices load failed: {e}")
    try:
        with open('crop_model.pkl', 'rb') as f:
            crop_model = pickle.load(f)
        with open('crop_scaler.pkl', 'rb') as f:
            crop_scaler = pickle.load(f)
        with open('crop_encoder.pkl', 'rb') as f:
            crop_encoder = pickle.load(f)
        print("✅ Crop model loaded")
    except Exception as e:
        print(f"⚠️  Crop model load failed: {e}")
    try:
        market_df = pd.read_csv('market_data.csv')
        print(f"✅ Market data loaded ({len(market_df)} rows)")
    except Exception as e:
        print(f"⚠️  Market data load failed: {e}")


def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    arr = arr / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def class_key_to_display(class_key: str):
    parts = class_key.split('___')
    plant = parts[0].replace('_', ' ').strip() if len(parts) > 0 else 'Unknown'
    disease = parts[1].replace('_', ' ').strip() if len(parts) > 1 else 'Unknown'
    return plant, disease


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/disease/detect', methods=['POST'])
def detect_disease():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Use PNG, JPG, or JPEG.'}), 400
        img_bytes = file.read()
        if disease_model is None or class_indices is None:
            return jsonify({'success': False, 'error': 'Disease detection model is not loaded.'}), 503
        img_array = preprocess_image(img_bytes)
        predictions = disease_model.predict(img_array, verbose=0)
        pred_idx = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0])) * 100
        class_key = class_indices.get(pred_idx, '')
        if not class_key:
            return jsonify({'success': False, 'error': f'Unknown class index: {pred_idx}'}), 500
        info = DISEASE_DB.get(class_key)
        if info is None:
            for db_key, db_val in DISEASE_DB.items():
                if db_key.lower().replace(' ', '') == class_key.lower().replace(' ', ''):
                    info = db_val
                    break
        if info is None:
            plant, disease = class_key_to_display(class_key)
            info = dict(DEFAULT_DISEASE)
            info['disease_name'] = disease
            info['crop_name'] = plant
            info['disease_name_ta'] = disease
            info['crop_name_ta'] = plant
        filename = secure_filename(file.filename) if file.filename else 'upload.jpg'
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(save_path, 'wb') as f:
            f.write(img_bytes)
        return jsonify({
            'success': True,
            'data': {
                'disease_name':    info['disease_name'],
                'disease_name_ta': info['disease_name_ta'],
                'severity':        info['severity'],
                'confidence':      round(confidence, 1),
                'crop_name':       info['crop_name'],
                'crop_name_ta':    info['crop_name_ta'],
                'treatment_en':    info['treatment_en'],
                'treatment_ta':    info['treatment_ta'],
                'class_key':       class_key
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/crop/predict', methods=['POST'])
def predict_crop():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        nitrogen   = float(data.get('nitrogen', 0))
        phosphorus = float(data.get('phosphorus', 0))
        potassium  = float(data.get('potassium', 0))
        ph         = float(data.get('ph', 7.0))
        district   = str(data.get('district', ''))
        temperature = float(data.get('temperature', 25.0))
        humidity    = float(data.get('humidity', 70.0))
        rainfall    = float(data.get('rainfall', 200.0))

        if crop_model is None:
            return jsonify({'success': False, 'error': 'Crop model not loaded'}), 503

        # Build features in correct order from crop_features.pkl
        try:
            with open('crop_features.pkl', 'rb') as f:
                feature_names = pickle.load(f)
            feat_map = {
                'N': nitrogen, 'P': phosphorus, 'K': potassium,
                'temperature': temperature, 'humidity': humidity,
                'ph': ph, 'rainfall': rainfall
            }
            features = np.array([[feat_map.get(name, 0) for name in feature_names]])
        except:
            features = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])

        if crop_scaler:
            features = crop_scaler.transform(features)

        prediction = crop_model.predict(features)
        proba = crop_model.predict_proba(features) if hasattr(crop_model, 'predict_proba') else None
        confidence = float(np.max(proba)) * 100 if proba is not None else 95.0

        crop_name = str(prediction[0])
        if crop_encoder:
            try:
                crop_name = str(crop_encoder.inverse_transform(prediction)[0])
            except Exception:
                pass

        CROP_TA = {
            'rice': 'நெல்', 'wheat': 'கோதுமை', 'maize': 'சோளம்',
            'sugarcane': 'கரும்பு', 'cotton': 'பருத்தி', 'groundnut': 'நிலக்கடலை',
            'banana': 'வாழை', 'turmeric': 'மஞ்சள்', 'onion': 'வெங்காயம்',
            'potato': 'உருளைக்கிழங்கு', 'tomato': 'தக்காளி', 'mango': 'மாம்பழம்',
            'coconut': 'தேங்காய்', 'chickpea': 'கொண்டைக்கடலை', 'lentil': 'பருப்பு',
            'mungbean': 'பாசிப்பயறு', 'blackgram': 'உளுந்து', 'kidneybeans': 'ராஜ்மா',
            'pigeonpeas': 'தூவரை', 'mothbeans': 'மொத்து பயறு', 'muskmelon': 'மஸ்க்மெலான்',
            'watermelon': 'தர்பூசணி', 'grapes': 'திராட்சை', 'apple': 'ஆப்பிள்',
            'orange': 'ஆரஞ்சு', 'papaya': 'பப்பாளி', 'pomegranate': 'மாதுளை',
            'jute': 'சணல்', 'coffee': 'காபி'
        }
        crop_name_ta = CROP_TA.get(crop_name.lower(), crop_name)

        CROP_DESC = {
            'rice': ('Ideal for your soil composition. Best sown June-July.',
                     'உங்கள் மண் கலவைக்கு சிறந்தது. ஜூன்-ஜூலையில் விதைக்க சிறந்தது.'),
        }
        desc_en, desc_ta = CROP_DESC.get(crop_name.lower(),
            ('Your soil conditions are suitable for this crop.',
             'உங்கள் மண் நிலைமைகள் இந்த பயிருக்கு ஏற்றவை.'))

        CROP_ICONS = {
            'rice': '🌾', 'wheat': '🌾', 'maize': '🌽', 'sugarcane': '🎋',
            'cotton': '🌸', 'groundnut': '🥜', 'banana': '🍌', 'turmeric': '🟡',
            'tomato': '🍅', 'potato': '🥔', 'onion': '🧅', 'mango': '🥭',
            'coconut': '🥥', 'grapes': '🍇', 'apple': '🍎', 'orange': '🍊',
            'watermelon': '🍉', 'papaya': '🍈', 'pomegranate': '❤️', 'coffee': '☕'
        }
        icon = CROP_ICONS.get(crop_name.lower(), '🌱')

        return jsonify({
            'success': True,
            'data': {
                'crop_name':       crop_name.title(),
                'crop_name_ta':    crop_name_ta,
                'confidence':      round(confidence, 1),
                'description_en':  desc_en,
                'description_ta':  desc_ta,
                'icon':            icon,
                'yield_estimate':  f'{round(confidence * 0.45, 1)} tons/ha'
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/market/prices', methods=['GET'])
def get_market_prices():
    try:
        district = request.args.get('district', 'All')
        if market_df is not None:
            df = market_df.copy()
            if district and district.lower() not in ('all', ''):
                df = df[df['district'].str.lower() == district.lower()]
            records = []
            for _, row in df.iterrows():
                change_val = float(row.get('change', 0))
                records.append({
                    'crop':     str(row.get('crop', '')),
                    'crop_ta':  str(row.get('crop_ta', row.get('crop', ''))),
                    'price':    float(row.get('price', 0)),
                    'district': str(row.get('district', '')),
                    'change':   f"{'+' if change_val >= 0 else ''}{change_val:.1f}%",
                    'up':       change_val >= 0,
                    'date':     str(row.get('date', 'Today'))
                })
            return jsonify({'success': True, 'data': records})
        data = [
            {'crop': 'Rice', 'crop_ta': 'நெல்', 'price': 2150, 'district': 'Thanjavur', 'change': '+2.4%', 'up': True, 'date': 'Today'},
            {'crop': 'Wheat', 'crop_ta': 'கோதுமை', 'price': 1820, 'district': 'Coimbatore', 'change': '-1.1%', 'up': False, 'date': 'Today'},
            {'crop': 'Sugarcane', 'crop_ta': 'கரும்பு', 'price': 3600, 'district': 'Erode', 'change': '+0.8%', 'up': True, 'date': 'Today'},
            {'crop': 'Cotton', 'crop_ta': 'பருத்தி', 'price': 5900, 'district': 'Salem', 'change': '+3.2%', 'up': True, 'date': 'Today'},
            {'crop': 'Groundnut', 'crop_ta': 'நிலக்கடலை', 'price': 5200, 'district': 'Vellore', 'change': '-0.5%', 'up': False, 'date': 'Yesterday'},
            {'crop': 'Turmeric', 'crop_ta': 'மஞ்சள்', 'price': 8500, 'district': 'Erode', 'change': '+5.1%', 'up': True, 'date': 'Yesterday'},
            {'crop': 'Banana', 'crop_ta': 'வாழை', 'price': 1200, 'district': 'Thanjavur', 'change': '+0.3%', 'up': True, 'date': 'Yesterday'},
            {'crop': 'Tomato', 'crop_ta': 'தக்காளி', 'price': 2800, 'district': 'Coimbatore', 'change': '-4.2%', 'up': False, 'date': '2 days ago'},
            {'crop': 'Onion', 'crop_ta': 'வெங்காயம்', 'price': 1600, 'district': 'Madurai', 'change': '+2.8%', 'up': True, 'date': '2 days ago'},
            {'crop': 'Maize', 'crop_ta': 'சோளம்', 'price': 1450, 'district': 'Salem', 'change': '-1.3%', 'up': False, 'date': '2 days ago'},
            {'crop': 'Soybean', 'crop_ta': 'சோயாபீன்', 'price': 3900, 'district': 'Trichy', 'change': '+1.6%', 'up': True, 'date': '3 days ago'},
            {'crop': 'Coconut', 'crop_ta': 'தேங்காய்', 'price': 2200, 'district': 'Coimbatore', 'change': '+0.9%', 'up': True, 'date': '3 days ago'},
        ]
        if district and district.lower() not in ('all', ''):
            data = [d for d in data if d['district'].lower() == district.lower()]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/weather/data', methods=['GET'])
def get_weather():
    try:
        data = [
            {'district': 'Thanjavur', 'condition': '⛅', 'condition_name': 'Partly Cloudy', 'condition_ta': 'பகுதியளவு மேகமூட்டம்', 'temp': 34, 'feels': 37, 'humidity': 78, 'rainfall': 12, 'wind': 18, 'advisory_en': 'Moderate rainfall expected. Good conditions for paddy transplanting.', 'advisory_ta': 'மிதமான மழை எதிர்பார்க்கப்படுகிறது. நெல் நடவுக்கு நல்ல நிலைமைகள்.'},
            {'district': 'Coimbatore', 'condition': '🌤️', 'condition_name': 'Mostly Sunny', 'condition_ta': 'பெரும்பாலும் வெயில்', 'temp': 29, 'feels': 31, 'humidity': 62, 'rainfall': 3, 'wind': 12, 'advisory_en': 'Clear skies. Ideal for harvesting operations.', 'advisory_ta': 'தெளிந்த வானம். அறுவடை நடவடிக்கைகளுக்கு சிறந்தது.'},
            {'district': 'Madurai', 'condition': '☀️', 'condition_name': 'Hot & Dry', 'condition_ta': 'வெப்பமும் வறட்சியும்', 'temp': 38, 'feels': 42, 'humidity': 45, 'rainfall': 0, 'wind': 8, 'advisory_en': 'High heat stress. Irrigate crops in early morning or evening.', 'advisory_ta': 'அதிக வெப்ப அழுத்தம். அதிகாலை அல்லது மாலையில் பயிர்களுக்கு நீர்ப்பாசனம் செய்யவும்.'},
            {'district': 'Salem', 'condition': '🌦️', 'condition_name': 'Light Rain', 'condition_ta': 'லேசான மழை', 'temp': 31, 'feels': 33, 'humidity': 70, 'rainfall': 8, 'wind': 15, 'advisory_en': 'Light showers expected. Delay pesticide application.', 'advisory_ta': 'லேசான மழை எதிர்பார்க்கப்படுகிறது. பூச்சி மருந்து தெளிப்பதை தாமதப்படுத்தவும்.'},
            {'district': 'Trichy', 'condition': '⛅', 'condition_name': 'Partly Cloudy', 'condition_ta': 'பகுதியளவு மேகமூட்டம்', 'temp': 35, 'feels': 38, 'humidity': 72, 'rainfall': 5, 'wind': 14, 'advisory_en': 'Pleasant conditions for field operations.', 'advisory_ta': 'வயல் நடவடிக்கைகளுக்கு இனிமையான நிலைமைகள்.'},
            {'district': 'Vellore', 'condition': '🌤️', 'condition_name': 'Clear', 'condition_ta': 'தெளிவான', 'temp': 33, 'feels': 35, 'humidity': 58, 'rainfall': 1, 'wind': 10, 'advisory_en': 'Good conditions. Suitable for fertilizer application.', 'advisory_ta': 'நல்ல நிலைமைகள். உரமிடுதலுக்கு ஏற்றது.'},
            {'district': 'Tirunelveli', 'condition': '☀️', 'condition_name': 'Sunny', 'condition_ta': 'வெயிலான', 'temp': 36, 'feels': 40, 'humidity': 65, 'rainfall': 0, 'wind': 11, 'advisory_en': 'Dry conditions. Ensure adequate irrigation for crops.', 'advisory_ta': 'வறண்ட நிலைமைகள். பயிர்களுக்கு போதுமான நீர்ப்பாசனம் உறுதி செய்யவும்.'},
            {'district': 'Erode', 'condition': '🌦️', 'condition_name': 'Drizzle', 'condition_ta': 'தூறல்', 'temp': 30, 'feels': 32, 'humidity': 67, 'rainfall': 7, 'wind': 16, 'advisory_en': 'Drizzle expected. Monitor for fungal disease risk.', 'advisory_ta': 'தூறல் எதிர்பார்க்கப்படுகிறது. பூஞ்சை நோய் அபாயத்தை கண்காணிக்கவும்.'},
        ]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ─── STARTUP ──────────────────────────────────────────────────────────────────
load_models()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)