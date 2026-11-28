"""
Smart Agri AI — Agronomic Knowledge Catalog
Preserves the full PlantVillage + Rice disease database, bilingual crop metadata
for all 22 ML crop classes + 15 market crops, and Tamil Nadu district coordinates
for Open-Meteo live weather integration.
"""

# ─── FULL PLANTVILLAGE + RICE DISEASE DATABASE ────────────────────────────────
DISEASE_DB = {
    "Apple___Apple_scab": {
        "disease_name": "Apple Scab",
        "disease_name_ta": "ஆப்பிள் ஸ்கேப்",
        "severity": "medium",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "description_en": "Fungal infection causing olive-green to black velvety spots on leaves and fruit.",
        "description_ta": "இலைகள் மற்றும் பழங்களில் ஆலிவ்-பச்சை முதல் கருப்பு நிற புள்ளிகளை ஏற்படுத்தும் பூஞ்சை தொற்று.",
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
        ),
    },
    "Apple___Black_rot": {
        "disease_name": "Apple Black Rot",
        "disease_name_ta": "ஆப்பிள் கருப்பு அழுகல்",
        "severity": "high",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "description_en": "Fungal disease causing frog-eye leaf spots, fruit rot, and branch cankers.",
        "description_ta": "இலைகளில் புள்ளிகள், பழ அழுகல் மற்றும் கிளைப் புண்களை ஏற்படுத்தும் பூஞ்சை நோய்.",
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
        ),
    },
    "Apple___Cedar_apple_rust": {
        "disease_name": "Cedar Apple Rust",
        "disease_name_ta": "சீடர் ஆப்பிள் துரு",
        "severity": "medium",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "description_en": "Bright orange-yellow spots on apple leaves spread from nearby cedar/juniper hosts.",
        "description_ta": "ஆப்பிள் இலைகளில் பிரகாசமான ஆரஞ்சு-மஞ்சள் நிற புள்ளிகளை ஏற்படுத்தும் துரு நோய்.",
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
        ),
    },
    "Apple___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Apple",
        "crop_name_ta": "ஆப்பிள்",
        "description_en": "No visible signs of fungal, bacterial, or viral leaf disease detected.",
        "description_ta": "இலைகளில் பூஞ்சை, பாக்டீரியா அல்லது வைரஸ் நோய் அறிகுறிகள் எதுவும் இல்லை.",
        "treatment_en": "Your apple plant looks healthy! Continue regular monitoring, proper irrigation, and seasonal fertilization. Maintain good orchard hygiene.",
        "treatment_ta": "உங்கள் ஆப்பிள் செடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு, சரியான நீர்ப்பாசனம் மற்றும் பருவகால உரமிடுதல் தொடருங்கள்.",
    },
    "Blueberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Blueberry",
        "crop_name_ta": "ப்ளூபெர்ரி",
        "description_en": "Foliage appears vibrant and free from disease lesions.",
        "description_ta": "இலைகள் ஆரோக்கியமாகவும் நோய்க் கறைகள் இன்றியும் உள்ளன.",
        "treatment_en": "Your blueberry plant looks healthy! Maintain acidic soil (pH 4.5–5.5), proper mulching, and regular monitoring.",
        "treatment_ta": "உங்கள் ப்ளூபெர்ரி செடி ஆரோக்கியமாக உள்ளது! அமில மண் (pH 4.5–5.5), சரியான மல்ச்சிங் மற்றும் தொடர்ந்து கண்காணிப்பு பராமரிக்கவும்.",
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "disease_name_ta": "தூள் பூஞ்சை",
        "severity": "medium",
        "crop_name": "Cherry",
        "crop_name_ta": "செர்ரி",
        "description_en": "White powdery fungal growth on young leaves and shoots causing leaf curling.",
        "description_ta": "இளம் இலைகள் மற்றும் தளிர்களில் வெள்ளை தூள் போன்ற பூஞ்சை வளர்ச்சியை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Cherry_(including_sour)___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Cherry",
        "crop_name_ta": "செர்ரி",
        "description_en": "Cherry leaf is healthy with normal chlorophyll pigmentation.",
        "description_ta": "செர்ரி இலை ஆரோக்கியமாகவும் இயல்பான பச்சை நிறத்துடனும் உள்ளது.",
        "treatment_en": "Your cherry plant looks healthy! Continue proper care with balanced fertilization and regular monitoring.",
        "treatment_ta": "உங்கள் செர்ரி செடி ஆரோக்கியமாக உள்ளது! சமநிலையான உரமிடுதல் மற்றும் தொடர்ந்து கண்காணிப்புடன் சரியான பராமரிப்பை தொடருங்கள்.",
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "disease_name": "Gray Leaf Spot",
        "disease_name_ta": "சாம்பல் இலை புள்ளி",
        "severity": "medium",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "description_en": "Rectangular tan-to-gray lesions restricted by leaf veins, reducing photosynthesis.",
        "description_ta": "இலை நரம்புகளுக்கு இடையே செவ்வக சாம்பல் நிற புள்ளிகளை ஏற்படுத்தி ஒளிச்சேர்க்கையைக் குறைக்கும் நோய்.",
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
        ),
    },
    "Corn_(maize)___Common_rust_": {
        "disease_name": "Common Rust",
        "disease_name_ta": "பொதுவான துரு நோய்",
        "severity": "medium",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "description_en": "Cinnamon-brown pustules scattered across upper and lower leaf surfaces.",
        "description_ta": "இலைகளின் மேல் மற்றும் கீழ் பரப்புகளில் பழுப்பு நிற துரு கொப்புளங்களை ஏற்படுத்தும் பூஞ்சை நோய்.",
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
        ),
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "disease_name": "Northern Leaf Blight",
        "disease_name_ta": "வடக்கு இலை கருகல்",
        "severity": "high",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "description_en": "Long cigar-shaped grayish-green necrotic lesions that can cause severe yield loss.",
        "description_ta": "இலைகளில் நீளமான சாம்பல்-பச்சை கருகல் புள்ளிகளை ஏற்படுத்தி மகசூலைக் குறைக்கும் நோய்.",
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
        ),
    },
    "Corn_(maize)___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Corn (Maize)",
        "crop_name_ta": "சோளம்",
        "description_en": "Maize leaf shows healthy green color with no blight or rust spots.",
        "description_ta": "சோள இலை கருகல் அல்லது துரு புள்ளிகள் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your corn plant looks healthy! Continue balanced NPK fertilization, proper irrigation, and regular field monitoring.",
        "treatment_ta": "உங்கள் சோள செடி ஆரோக்கியமாக உள்ளது! சமநிலையான NPK உரமிடுதல், சரியான நீர்ப்பாசனம் மற்றும் தொடர்ந்து வயல் கண்காணிப்பை தொடருங்கள்.",
    },
    "Grape___Black_rot": {
        "disease_name": "Grape Black Rot",
        "disease_name_ta": "திராட்சை கருப்பு அழுகல்",
        "severity": "high",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "description_en": "Reddish-brown leaf lesions with black pycnidia and shriveled mummified berries.",
        "description_ta": "இலைகளில் சிவப்பு-பழுப்பு புள்ளிகள் மற்றும் திராட்சை பழங்களில் சுருக்கமான கருப்பு அழுகலை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Grape___Esca_(Black_Measles)": {
        "disease_name": "Esca (Black Measles)",
        "disease_name_ta": "எஸ்கா (கருப்பு தட்டம்மை)",
        "severity": "high",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "description_en": "Tiger-stripe interveinal chlorosis and necrosis on leaves caused by wood-decay fungi.",
        "description_ta": "இலைகளில் புலி-வரி போன்ற மஞ்சள் மற்றும் காய்ந்த கோடுகளை ஏற்படுத்தும் பூஞ்சை நோய்.",
        "treatment_en": (
            "1. No complete cure — focus on management and prevention.\n"
            "2. Remove and destroy severely infected vines.\n"
            "3. Protect pruning wounds with fungicidal paste (Trichoderma-based).\n"
            "4. Prune during dry weather; avoid rainy seasons.\n"
            "5. Disinfect pruning tools between plants.\n"
            "6. Apply trunk protection treatments where recommended by extension officers."
        ),
        "treatment_ta": (
            "1. முழுமையான சிகிச்சை இல்லை — மேலாண்மை மற்றும் தடுப்பில் கவனம் செலுத்தவும்.\n"
            "2. கடுமையாக பாதிக்கப்பட்ட கொடிகளை அகற்றி அழிக்கவும்.\n"
            "3. கத்தரிப்பு புண்களை பூஞ்சை மருந்து பேஸ்ட் (Trichoderma-அடிப்படையிலான) கொண்டு பாதுகாக்கவும்.\n"
            "4. வறண்ட வானிலையில் கத்தரிக்கவும்; மழை பருவங்களை தவிர்க்கவும்.\n"
            "5. செடிகளுக்கு இடையில் கத்தரிப்பு கருவிகளை கிருமி நீக்கம் செய்யவும்.\n"
            "6. வேளாண் அதிகாரிகளின் ஆலோசனைப்படி தண்டு பாதுகாப்பு சிகிச்சைகளை மேற்கொள்ளவும்."
        ),
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "disease_name": "Leaf Blight",
        "disease_name_ta": "இலை கருகல்",
        "severity": "medium",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "description_en": "Irregular dark brown blotches on leaves leading to premature defoliation.",
        "description_ta": "இலைகளில் அடர் பழுப்பு நிற திட்டுகளை ஏற்படுத்தி முன்கூட்டியே இலை உதிர்வை உண்டாக்கும் நோய்.",
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
        ),
    },
    "Grape___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Grape",
        "crop_name_ta": "திராட்சை",
        "description_en": "Grapevine leaf is healthy with no fungal spots or scorching.",
        "description_ta": "திராட்சை இலை பூஞ்சை புள்ளிகள் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your grape vine looks healthy! Continue regular monitoring, proper pruning, and balanced fertilization.",
        "treatment_ta": "உங்கள் திராட்சை கொடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு, சரியான கத்தரிப்பு மற்றும் சமநிலையான உரமிடுதலை தொடருங்கள்.",
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "disease_name": "Citrus Greening (HLB)",
        "disease_name_ta": "சிட்ரஸ் பச்சையாதல் (HLB)",
        "severity": "high",
        "crop_name": "Orange",
        "crop_name_ta": "ஆரஞ்சு",
        "description_en": "Asymmetrical blotchy yellowing of citrus leaves transmitted by Asian citrus psyllid.",
        "description_ta": "இலைகளில் சமச்சீரற்ற மஞ்சள் திட்டுகளை ஏற்படுத்தும் கடுமையான பாக்டீரியா நோய்.",
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
            "2. ஆசிய சிட்ரஸ் பூச்சியை (Imidacloprid) மருந்துகளால் கட்டுப்படுத்தவும்.\n"
            "3. சான்றளிக்கப்பட்ட நோயற்ற நடவு பொருட்களை மட்டுமே பயன்படுத்தவும்.\n"
            "4. பூச்சி இயக்கத்தை தடுக்க பிரதிபலிப்பு மல்ச்களை பயன்படுத்தவும்.\n"
            "5. அறிகுறிகளுக்கு மரங்களை தொடர்ந்து ஆய்வு செய்யவும்.\n"
            "6. HLB சந்தேகப்பட்டால் உள்ளூர் விவசாய அதிகாரிகளுக்கு தெரியப்படுத்தவும்."
        ),
    },
    "Peach___Bacterial_spot": {
        "disease_name": "Peach Bacterial Spot",
        "disease_name_ta": "பீச் பாக்டீரியல் புள்ளி",
        "severity": "medium",
        "crop_name": "Peach",
        "crop_name_ta": "பீச்",
        "description_en": "Water-soaked angular spots on leaves that drop out leaving shot-hole appearances.",
        "description_ta": "இலைகளில் நீர் ஊறிய கோணப் புள்ளிகளை ஏற்படுத்தி துளைகள் போல மாற்றும் பாக்டீரியா நோய்.",
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
        ),
    },
    "Peach___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Peach",
        "crop_name_ta": "பீச்",
        "description_en": "Peach foliage is healthy and free from bacterial or fungal spotting.",
        "description_ta": "பீச் இலைகள் பாக்டீரியா அல்லது பூஞ்சை புள்ளிகள் இன்றி ஆரோக்கியமாக உள்ளன.",
        "treatment_en": "Your peach plant looks healthy! Maintain proper nutrition, irrigation, and regular monitoring.",
        "treatment_ta": "உங்கள் பீச் செடி ஆரோக்கியமாக உள்ளது! சரியான ஊட்டச்சத்து, நீர்ப்பாசனம் மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்.",
    },
    "Pepper,_bell___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "disease_name_ta": "பாக்டீரியல் புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Bell Pepper",
        "crop_name_ta": "குடை மிளகாய்",
        "description_en": "Small dark water-soaked spots on pepper leaves turning brown with yellow halos.",
        "description_ta": "மிளகாய் இலைகளில் மஞ்சள் வளையத்துடன் கூடிய பழுப்பு நிற பாக்டீரியா புள்ளிகளை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Pepper,_bell___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Bell Pepper",
        "crop_name_ta": "குடை மிளகாய்",
        "description_en": "Bell pepper leaf is healthy with uniform green coloration.",
        "description_ta": "குடை மிளகாய் இலை சீரான பச்சை நிறத்துடன் ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your pepper plant looks healthy! Continue regular monitoring and balanced fertilization.",
        "treatment_ta": "உங்கள் மிளகாய் செடி ஆரோக்கியமாக உள்ளது! தொடர்ந்து கண்காணிப்பு மற்றும் சமநிலையான உரமிடுதலை தொடருங்கள்.",
    },
    "Potato___Early_blight": {
        "disease_name": "Early Blight",
        "disease_name_ta": "ஆரம்ப கருகல் நோய்",
        "severity": "medium",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "description_en": "Concentric bullseye-ring brown spots caused by Alternaria solani.",
        "description_ta": "இலைகளில் வட்ட வளைய பழுப்பு நிற கருகல் புள்ளிகளை ஏற்படுத்தும் பூஞ்சை நோய்.",
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
        ),
    },
    "Potato___Late_blight": {
        "disease_name": "Late Blight",
        "disease_name_ta": "தாமத கருகல் நோய்",
        "severity": "high",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "description_en": "Rapidly expanding dark water-soaked lesions with white mold under humid conditions.",
        "description_ta": "ஈரமான சூழலில் வேகமாகப் பரவும் அடர் கருகல் மற்றும் வெள்ளை பூஞ்சையை ஏற்படுத்தும் தீவிர நோய்.",
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
        ),
    },
    "Potato___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Potato",
        "crop_name_ta": "உருளைக்கிழங்கு",
        "description_en": "Potato foliage is healthy with no blight lesions.",
        "description_ta": "உருளைக்கிழங்கு இலை கருகல் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your potato plant looks healthy! Maintain proper hilling, balanced NPK fertilization, and regular monitoring.",
        "treatment_ta": "உங்கள் உருளைக்கிழங்கு செடி ஆரோக்கியமாக உள்ளது! சரியான மண் திரட்டல், சமநிலையான NPK உரமிடுதல் மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்.",
    },
    "Raspberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Raspberry",
        "crop_name_ta": "ராஸ்பெர்ரி",
        "description_en": "Raspberry leaf is healthy and free of visible pests or fungal spots.",
        "description_ta": "ராஸ்பெர்ரி இலை பூச்சி அல்லது பூஞ்சை புள்ளிகள் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your raspberry plant looks healthy! Continue proper pruning, mulching, and regular monitoring for pests.",
        "treatment_ta": "உங்கள் ராஸ்பெர்ரி செடி ஆரோக்கியமாக உள்ளது! சரியான கத்தரிப்பு, மல்ச்சிங் மற்றும் பூச்சிகளுக்கான தொடர்ந்து கண்காணிப்பை தொடருங்கள்.",
    },
    "Rice___Brown_Spot": {
        "disease_name": "Brown Spot",
        "disease_name_ta": "பழுப்பு புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "description_en": "Oval brown lesions with gray centers and yellow halos, often linked to nutrient deficiency.",
        "description_ta": "நெல் இலைகளில் மஞ்சள் ஓரங்களுடன் கூடிய நீள்வட்ட பழுப்பு புள்ளிகளை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Rice___Hispa": {
        "disease_name": "Rice Hispa",
        "disease_name_ta": "நெல் ஹிஸ்பா",
        "severity": "medium",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "description_en": "White parallel streaks on rice leaves caused by scraping beetles and mining grubs.",
        "description_ta": "வண்டுகள் மற்றும் புழுக்களால் நெல் இலைகளில் வெள்ளை கோடுகள் ஏற்படும் பூச்சி சேதம்.",
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
        ),
    },
    "Rice___Leaf_Blast": {
        "disease_name": "Leaf Blast",
        "disease_name_ta": "இலை வெடிப்பு நோய்",
        "severity": "high",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "description_en": "Diamond or spindle-shaped gray-centered lesions with brown margins caused by Magnaporthe oryzae.",
        "description_ta": "நெல் இலைகளில் கண் வடிவ சாம்பல் மையப் புள்ளிகளை ஏற்படுத்தும் கடுமையான பூஞ்சை நோய்.",
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
        ),
    },
    "Rice___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Rice (Paddy)",
        "crop_name_ta": "நெல் (பயிர்)",
        "description_en": "Paddy leaf appears healthy with no blast or brown spot lesions.",
        "description_ta": "நெல் இலை வெடிப்பு அல்லது பழுப்பு புள்ளி இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your rice plant looks healthy! Maintain proper water management, balanced NPK fertilization, and regular field monitoring.",
        "treatment_ta": "உங்கள் நெல் செடி ஆரோக்கியமாக உள்ளது! சரியான நீர் மேலாண்மை, சமநிலையான NPK உரமிடுதல் மற்றும் தொடர்ந்து வயல் கண்காணிப்பை பராமரிக்கவும்.",
    },
    "Soybean___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Soybean",
        "crop_name_ta": "சோயாபீன்",
        "description_en": "Soybean foliage is vigorous and disease-free.",
        "description_ta": "சோயாபீன் இலை நோயின்றி செழிப்பாக உள்ளது.",
        "treatment_en": "Your soybean plant looks healthy! Maintain balanced fertilization and proper weed management.",
        "treatment_ta": "உங்கள் சோயாபீன் செடி ஆரோக்கியமாக உள்ளது! சமநிலையான உரமிடுதல் மற்றும் சரியான களை மேலாண்மையை பராமரிக்கவும்.",
    },
    "Squash___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "disease_name_ta": "தூள் பூஞ்சை நோய்",
        "severity": "medium",
        "crop_name": "Squash",
        "crop_name_ta": "சுரைக்காய்",
        "description_en": "White talcum-like powdery spots covering upper leaf surfaces.",
        "description_ta": "இலைகளின் மேற்பரப்பில் வெள்ளை மாவு போன்ற பூஞ்சை படிவுகளை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Strawberry___Leaf_scorch": {
        "disease_name": "Leaf Scorch",
        "disease_name_ta": "இலை எரிவு நோய்",
        "severity": "medium",
        "crop_name": "Strawberry",
        "crop_name_ta": "ஸ்ட்ராபெர்ரி",
        "description_en": "Dark purple blotches coalescing until leaves dry and appear scorched.",
        "description_ta": "இலைகளில் அடர் ஊதா நிற திட்டுகள் ஏற்பட்டு இலைகள் எரிந்தது போல காய்ந்து போகும் நோய்.",
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
        ),
    },
    "Strawberry___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Strawberry",
        "crop_name_ta": "ஸ்ட்ராபெர்ரி",
        "description_en": "Strawberry leaf is healthy and free from scorch or fungal spotting.",
        "description_ta": "ஸ்ட்ராபெர்ரி இலை எரிவு அல்லது பூஞ்சை புள்ளிகள் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your strawberry plant looks healthy! Maintain proper mulching, balanced nutrition, and regular monitoring.",
        "treatment_ta": "உங்கள் ஸ்ட்ராபெர்ரி செடி ஆரோக்கியமாக உள்ளது! சரியான மல்ச்சிங், சமநிலையான ஊட்டச்சத்து மற்றும் தொடர்ந்து கண்காணிப்பை பராமரிக்கவும்.",
    },
    "Tomato___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "disease_name_ta": "பாக்டீரியல் புள்ளி நோய்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Dark greasy spots on leaves and raised scabby spots on fruits.",
        "description_ta": "இலைகளில் கருப்பு நிற புள்ளிகள் மற்றும் பழங்களில் சொறி போன்ற புள்ளிகளை ஏற்படுத்தும் பாக்டீரியா நோய்.",
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
        ),
    },
    "Tomato___Early_blight": {
        "disease_name": "Early Blight",
        "disease_name_ta": "ஆரம்ப கருகல் நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Dark brown spots with concentric rings on older lower leaves.",
        "description_ta": "முதிர்ந்த கீழ் இலைகளில் வட்ட வளையங்களுடன் கூடிய அடர் பழுப்பு நிற புள்ளிகள்.",
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
        ),
    },
    "Tomato___Late_blight": {
        "disease_name": "Late Blight",
        "disease_name_ta": "தாமத கருகல் நோய்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Rapidly spreading greenish-black water-soaked patches caused by Phytophthora infestans.",
        "description_ta": "குளிர் மற்றும் ஈரமான சூழலில் வேகமாகப் பரவும் பச்சை-கருப்பு நிற அழுகல் நோய்.",
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
        ),
    },
    "Tomato___Leaf_Mold": {
        "disease_name": "Leaf Mold",
        "disease_name_ta": "இலை பூஞ்சை நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Pale green/yellow patches on upper leaf surface with olive-gray mold beneath.",
        "description_ta": "இலையின் மேல் மஞ்சள் திட்டுகளும் கீழே ஆலிவ்-சாம்பல் பூஞ்சை வளர்ச்சியும் ஏற்படும் நோய்.",
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
        ),
    },
    "Tomato___Septoria_leaf_spot": {
        "disease_name": "Septoria Leaf Spot",
        "disease_name_ta": "செப்டோரியா இலை புள்ளி",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Numerous small circular spots with dark borders and tan centers.",
        "description_ta": "கருமையான ஓரமும் வெளிர் மையமும் கொண்ட சிறிய வட்டப் புள்ளிகளை ஏற்படுத்தும் நோய்.",
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
        ),
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "disease_name": "Spider Mites (Two-spotted)",
        "disease_name_ta": "சிலந்தி பூச்சிகள் (இரு புள்ளி)",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Fine yellow stippling and webbing on leaves caused by sap-sucking spider mites.",
        "description_ta": "சிலந்தி பூச்சிகள் சாறு உறிஞ்சுவதால் இலைகளில் மஞ்சள் புள்ளிகள் மற்றும் வலை ஏற்படும்.",
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
        ),
    },
    "Tomato___Target_Spot": {
        "disease_name": "Target Spot",
        "disease_name_ta": "இலக்கு புள்ளி நோய்",
        "severity": "medium",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Target-like concentric necrotic spots expanding across leaves and stems.",
        "description_ta": "இலைகள் மற்றும் தண்டுகளில் இலக்கு போன்ற வட்டப் புள்ளிகளை ஏற்படுத்தும் பூஞ்சை நோய்.",
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
        ),
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "disease_name": "Yellow Leaf Curl Virus (TYLCV)",
        "disease_name_ta": "மஞ்சள் இலை சுருட்டை வைரஸ்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Upward curling, yellowing leaf margins, and stunted plant growth spread by whiteflies.",
        "description_ta": "வெள்ளை ஈ மூலம் பரவும் இலை சுருட்டல், மஞ்சள் நிறம் மற்றும் வளர்ச்சி குன்றிய வைரஸ் நோய்.",
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
        ),
    },
    "Tomato___Tomato_mosaic_virus": {
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "disease_name_ta": "தக்காளி மொசைக் வைரஸ்",
        "severity": "high",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Light and dark green mottled leaf patterns with distorted fern-like foliage.",
        "description_ta": "இலைகளில் வெளிர் மற்றும் அடர் பச்சை நிற மொசைக் வடிவங்களை ஏற்படுத்தும் வைரஸ் நோய்.",
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
            "7. வயலில் நுழைவதற்கு முன் புகையிலை பொருட்களை அகற்றுங்கள்."
        ),
    },
    "Tomato___healthy": {
        "disease_name": "Healthy",
        "disease_name_ta": "ஆரோக்கியமான",
        "severity": "low",
        "crop_name": "Tomato",
        "crop_name_ta": "தக்காளி",
        "description_en": "Tomato foliage is healthy with no fungal, bacterial, or viral symptoms.",
        "description_ta": "தக்காளி இலை பூஞ்சை, பாக்டீரியா அல்லது வைரஸ் அறிகுறிகள் இன்றி ஆரோக்கியமாக உள்ளது.",
        "treatment_en": "Your tomato plant looks healthy! Maintain balanced NPK, proper staking, regular monitoring, and adequate watering.",
        "treatment_ta": "உங்கள் தக்காளி செடி ஆரோக்கியமாக உள்ளது! சமநிலையான NPK, சரியான கட்டுதல், தொடர்ந்து கண்காணிப்பு மற்றும் போதுமான நீர்ப்பாசனம் பராமரிக்கவும்.",
    },
}

DEFAULT_DISEASE = {
    "disease_name": "Unknown Disease",
    "disease_name_ta": "தெரியாத நோய்",
    "severity": "medium",
    "crop_name": "Unknown Crop",
    "crop_name_ta": "தெரியாத பயிர்",
    "description_en": "Detected class is not in the detailed advisory table; consult a local agricultural specialist.",
    "description_ta": "கண்டறியப்பட்ட வகுப்பு விரிவான ஆலோசனை அட்டவணையில் இல்லை; உள்ளூர் வேளாண் அதிகாரியை அணுகவும்.",
    "treatment_en": "Please consult your local agricultural extension officer for proper diagnosis and treatment recommendations.",
    "treatment_ta": "சரியான நோயறிதல் மற்றும் சிகிச்சை பரிந்துரைகளுக்கு உங்கள் உள்ளூர் விவசாய விரிவாக்க அதிகாரியை அணுகவும்.",
}

# ─── CROP METADATA (ALL 22 ML CLASSES + MARKET CROPS) ────────────────────────
CROP_CATALOG = {
    "rice": {
        "name_en": "Rice",
        "name_ta": "நெல்",
        "icon": "🌾",
        "desc_en": "Ideal for alluvial and clay-loam soils with high water retention and warm humid conditions.",
        "desc_ta": "அதிக நீர் தேக்கம் கொண்ட வண்டல் மற்றும் களிமண் நிலங்களுக்கு ஏற்றது. வெப்ப ஈரப்பதமான சூழலில் சிறப்பாக வளரும்.",
    },
    "maize": {
        "name_en": "Maize",
        "name_ta": "மக்காச்சோளம்",
        "icon": "🌽",
        "desc_en": "Well-suited for fertile, well-drained loamy soils with balanced nitrogen and potassium.",
        "desc_ta": "சமநிலையான நைட்ரஜன் மற்றும் பொட்டாசியம் கொண்ட வளமான, வடிகால் வசதியுள்ள மண்ணிற்கு சிறந்தது.",
    },
    "chickpea": {
        "name_en": "Chickpea",
        "name_ta": "கொண்டைக்கடலை",
        "icon": "🫘",
        "desc_en": "Thrives in cooler semi-arid conditions with moderate phosphorus and low rainfall.",
        "desc_ta": "மிதமான பாஸ்பரஸ் மற்றும் குறைந்த மழைப்பொழிவு உள்ள குளிர்ந்த வறண்ட பகுதிகளில் சிறப்பாக வளரும்.",
    },
    "kidneybeans": {
        "name_en": "Kidney Beans",
        "name_ta": "ராஜ்மா",
        "icon": "🫘",
        "desc_en": "Prefers well-drained neutral-to-slightly-acidic soil with cool to moderate temperatures.",
        "desc_ta": "நல்ல வடிகால் வசதியுள்ள நடுநிலை முதல் சற்று அமில மண் மற்றும் மிதமான வெப்பநிலையில் நன்கு வளரும்.",
    },
    "pigeonpeas": {
        "name_en": "Pigeon Peas",
        "name_ta": "துவரை",
        "icon": "🌿",
        "desc_en": "Drought-tolerant pulse crop suited for red and black soils with moderate rainfall.",
        "desc_ta": "வறட்சியைத் தாங்கும் பருப்பு வகைப் பயிர்; சிவப்பு மற்றும் கரிசல் மண்ணில் சிறப்பாக வளரும்.",
    },
    "mothbeans": {
        "name_en": "Moth Beans",
        "name_ta": "மொத்து பயறு",
        "icon": "🌱",
        "desc_en": "Highly drought-resistant legume ideal for arid sandy soils and warm climates.",
        "desc_ta": "வறண்ட மணல் மண் மற்றும் வெப்பமான காலநிலைக்கு ஏற்ற வறட்சி தாங்கும் பயறு வகை.",
    },
    "mungbean": {
        "name_en": "Mung Bean",
        "name_ta": "பாசிப்பயறு",
        "icon": "🫛",
        "desc_en": "Short-duration pulse crop suited for warm humid weather and well-drained loamy soils.",
        "desc_ta": "வெப்ப ஈரப்பதமான காலநிலை மற்றும் வடிகால் வசதியுள்ள மண்ணிற்கு ஏற்ற குறுகிய கால பயறு பயிர்.",
    },
    "blackgram": {
        "name_en": "Black Gram",
        "name_ta": "உளுந்து",
        "icon": "🫘",
        "desc_en": "Performs well in warm regions and rice-fallow delta soils with balanced NPK.",
        "desc_ta": "நெல் தரிசு நிலங்கள் மற்றும் வெப்ப பகுதிகளில் சமநிலையான NPK உடன் நன்கு விளையும்.",
    },
    "lentil": {
        "name_en": "Lentil",
        "name_ta": "மைசூர் பருப்பு",
        "icon": "🫘",
        "desc_en": "Suited for cool, dry conditions and well-drained soils with moderate phosphorus.",
        "desc_ta": "குளிர்ந்த வறண்ட காலநிலை மற்றும் மிதமான பாஸ்பரஸ் உள்ள மண்ணிற்கு ஏற்றது.",
    },
    "pomegranate": {
        "name_en": "Pomegranate",
        "name_ta": "மாதுளை",
        "icon": "🍎",
        "desc_en": "Thrives in semi-arid climates with hot summers and well-drained loamy soils.",
        "desc_ta": "வறண்ட வெப்பமான காலநிலை மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் சிறப்பாக விளையும்.",
    },
    "banana": {
        "name_en": "Banana",
        "name_ta": "வாழை",
        "icon": "🍌",
        "desc_en": "Requires potassium-rich fertile soil, steady moisture, and warm tropical weather.",
        "desc_ta": "பொட்டாசியம் நிறைந்த வளமான மண், நிலையான ஈரப்பதம் மற்றும் வெப்பமண்டல காலநிலை தேவை.",
    },
    "mango": {
        "name_en": "Mango",
        "name_ta": "மாம்பழம்",
        "icon": "🥭",
        "desc_en": "Performs best in deep well-drained alluvial or red loamy soils with warm dry flowering weather.",
        "desc_ta": "ஆழமான வடிகால் வசதியுள்ள வண்டல் அல்லது செம்மண்ணில் பூக்கும் கால வறண்ட வானிலையில் சிறப்பாக வளரும்.",
    },
    "grapes": {
        "name_en": "Grapes",
        "name_ta": "திராட்சை",
        "icon": "🍇",
        "desc_en": "Requires potassium-rich sandy loam soil and dry sunny weather for sweet fruit development.",
        "desc_ta": "பொட்டாசியம் செறிந்த மணல் கலந்த மண் மற்றும் இனிமையான பழ வளர்ச்சிக்கு வெயிலான வானிலை தேவை.",
    },
    "watermelon": {
        "name_en": "Watermelon",
        "name_ta": "தர்பூசணி",
        "icon": "🍉",
        "desc_en": "Ideal for warm sunny conditions and well-drained sandy loam soils.",
        "desc_ta": "வெப்பமான வெயில் சூழல் மற்றும் வடிகால் வசதியுள்ள மணல் கலந்த மண்ணிற்கு சிறந்தது.",
    },
    "muskmelon": {
        "name_en": "Muskmelon",
        "name_ta": "முலாம்பழம்",
        "icon": "🍈",
        "desc_en": "Grows rapidly in warm dry climates with sandy loam soil and good drainage.",
        "desc_ta": "வெப்ப வறண்ட காலநிலை மற்றும் மணல் கலந்த மண்ணில் விரைவாக வளரும்.",
    },
    "apple": {
        "name_en": "Apple",
        "name_ta": "ஆப்பிள்",
        "icon": "🍏",
        "desc_en": "Requires cool temperate highland climate and well-drained loamy soil rich in potassium.",
        "desc_ta": "குளிர்ந்த மலைப்பகுதி காலநிலை மற்றும் பொட்டாசியம் நிறைந்த வண்டல் மண் தேவை.",
    },
    "orange": {
        "name_en": "Orange",
        "name_ta": "ஆரஞ்சு",
        "icon": "🍊",
        "desc_en": "Suitable for subtropical climates with slightly acidic to neutral well-drained soils.",
        "desc_ta": "மிதவெப்பமண்டல காலநிலை மற்றும் சற்று அமில முதல் நடுநிலை மண்ணிற்கு ஏற்றது.",
    },
    "papaya": {
        "name_en": "Papaya",
        "name_ta": "பப்பாளி",
        "icon": "🍈",
        "desc_en": "Fast-growing tropical fruit thriving in warm humid conditions and fertile drained soil.",
        "desc_ta": "வெப்ப ஈரப்பதமான சூழல் மற்றும் வளமான வடிகால் வசதியுள்ள மண்ணில் விரைவாக வளரும்.",
    },
    "coconut": {
        "name_en": "Coconut",
        "name_ta": "தேங்காய்",
        "icon": "🥥",
        "desc_en": "Ideal for coastal and tropical humid districts with high rainfall and sandy loam soils.",
        "desc_ta": "கடற்கரை மற்றும் அதிக மழைப்பொழிவு உள்ள ஈரப்பதமான மாவட்டங்களுக்கு மிகவும் ஏற்றது.",
    },
    "cotton": {
        "name_en": "Cotton",
        "name_ta": "பருத்தி",
        "icon": "🌸",
        "desc_en": "Thrives in black cotton and deep loamy soils with high nitrogen and warm sunny weather.",
        "desc_ta": "கரிசல் மண் மற்றும் ஆழமான மண்ணில் அதிக நைட்ரஜன் மற்றும் வெயிலான வானிலையில் சிறப்பாக வளரும்.",
    },
    "jute": {
        "name_en": "Jute",
        "name_ta": "சணல்",
        "icon": "🌾",
        "desc_en": "Best suited for warm, very humid alluvial plains with abundant rainfall.",
        "desc_ta": "அதிக மழைப்பொழிவு மற்றும் ஈரப்பதம் கொண்ட வெப்பமான வண்டல் சமவெளிகளுக்கு ஏற்றது.",
    },
    "coffee": {
        "name_en": "Coffee",
        "name_ta": "காபி",
        "icon": "☕",
        "desc_en": "Suited for cool humid hill tracts with rich organic acidic soils and high rainfall.",
        "desc_ta": "குளிர்ந்த ஈரப்பதமான மலைப்பகுதிகள் மற்றும் கரிம அமில மண்ணிற்கு ஏற்றது.",
    },
    "sugarcane": {
        "name_en": "Sugarcane",
        "name_ta": "கரும்பு",
        "icon": "🎋",
        "desc_en": "Long-duration cash crop thriving in fertile alluvial soil with reliable irrigation.",
        "desc_ta": "வளமான வண்டல் மண் மற்றும் நிலையான நீர்ப்பாசனத்துடன் சிறப்பாக விளையும் பணப்பயிர்.",
    },
    "groundnut": {
        "name_en": "Groundnut",
        "name_ta": "நிலக்கடலை",
        "icon": "🥜",
        "desc_en": "Oilseed crop well-suited for friable red sandy loam soils.",
        "desc_ta": "செம்மண் மற்றும் மணல் கலந்த மண்ணிற்கு ஏற்ற எண்ணெய் வித்துப் பயிர்.",
    },
    "turmeric": {
        "name_en": "Turmeric",
        "name_ta": "மஞ்சள்",
        "icon": "🌿",
        "desc_en": "High-value rhizome crop well-adapted to Erode, Salem, and Coimbatore regions.",
        "desc_ta": "ஈரோடு, சேலம் மற்றும் கோயம்புத்தூர் பகுதிகளுக்கு ஏற்ற அதிக மதிப்புள்ள கிழங்கு பயிர்.",
    },
    "onion": {
        "name_en": "Onion",
        "name_ta": "வெங்காயம்",
        "icon": "🧅",
        "desc_en": "Prefers well-drained friable loamy soil with mild dry harvest conditions.",
        "desc_ta": "நல்ல வடிகால் வசதியுள்ள மண் மற்றும் மிதமான வறண்ட அறுவடை காலநிலைக்கு ஏற்றது.",
    },
    "potato": {
        "name_en": "Potato",
        "name_ta": "உருளைக்கிழங்கு",
        "icon": "🥔",
        "desc_en": "Cool-season tuber crop suited for well-drained sandy loam soils.",
        "desc_ta": "குளிர்ந்த பருவம் மற்றும் வடிகால் வசதியுள்ள மணல் கலந்த மண்ணிற்கு ஏற்ற கிழங்கு பயிர்.",
    },
    "tomato": {
        "name_en": "Tomato",
        "name_ta": "தக்காளி",
        "icon": "🍅",
        "desc_en": "Versatile vegetable crop growing well in fertile neutral soils.",
        "desc_ta": "வளமான நடுநிலை மண்ணில் நன்கு விளையும் காய்கறி பயிர்.",
    },
    "wheat": {
        "name_en": "Wheat",
        "name_ta": "கோதுமை",
        "icon": "🌾",
        "desc_en": "Cool-season cereal crop adapted to well-drained loamy soils.",
        "desc_ta": "வடிகால் வசதியுள்ள வண்டல் மண்ணிற்கு ஏற்ற குளிர் பருவ தானியப் பயிர்.",
    },
    "chilli": {
        "name_en": "Chilli",
        "name_ta": "மிளகாய்",
        "icon": "🌶️",
        "desc_en": "Warm-season spice crop thriving in well-drained black and loamy soils.",
        "desc_ta": "நல்ல வடிகால் வசதியுள்ள கரிசல் மற்றும் வண்டல் மண்ணில் விளையும் நறுமணப் பயிர்.",
    },
    "soybean": {
        "name_en": "Soybean",
        "name_ta": "சோயாபீன்",
        "icon": "🫘",
        "desc_en": "Protein-rich oilseed legume suited for well-drained fertile loams.",
        "desc_ta": "வளமான மண்ணிற்கு ஏற்ற புரதம் நிறைந்த எண்ணெய் வித்துப் பயிர்.",
    },
    "sunflower": {
        "name_en": "Sunflower",
        "name_ta": "சூரியகாந்தி",
        "icon": "🌻",
        "desc_en": "Hardy oilseed crop adaptable to moderate rainfall and sunny conditions.",
        "desc_ta": "மிதமான மழை மற்றும் வெயிலான சூழலுக்கு ஏற்ற எண்ணெய் வித்துப் பயிர்.",
    },
}

# ─── TAMIL NADU DISTRICTS (COORDINATES FOR OPEN-METEO) ────────────────────────
DISTRICT_COORDS = {
    "Thanjavur": (10.7870, 79.1378),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Trichy": (10.7905, 78.7047),
    "Vellore": (12.9165, 79.1325),
    "Tirunelveli": (8.7139, 77.7567),
    "Erode": (11.3410, 77.7172),
    "Dindigul": (10.3673, 77.9803),
    "Chennai": (13.0827, 80.2707),
    "Cuddalore": (11.7480, 79.7714),
    "Kancheepuram": (12.8342, 79.7036),
    "Karur": (10.9601, 78.0766),
    "Krishnagiri": (12.5186, 78.2137),
    "Virudhunagar": (9.5680, 77.9624),
    "Nagapattinam": (10.7672, 79.8449),
    "Tiruvarur": (10.7661, 79.6344),
    "Pudukkottai": (10.3833, 78.8001),
}

WMO_WEATHER_MAP = {
    0: ("☀️", "Clear Sky", "தெளிவான வானம்"),
    1: ("🌤️", "Mostly Clear", "பெரும்பாலும் தெளிவானது"),
    2: ("⛅", "Partly Cloudy", "பகுதியளவு மேகமூட்டம்"),
    3: ("☁️", "Overcast", "மேகமூட்டம்"),
    45: ("🌫️", "Foggy", "மூடுபனி"),
    48: ("🌫️", "Rime Fog", "உறைபனி"),
    51: ("🌦️", "Light Drizzle", "லேசான தூறல்"),
    53: ("🌦️", "Moderate Drizzle", "மிதமான தூறல்"),
    55: ("🌧️", "Dense Drizzle", "அடர்ந்த தூறல்"),
    61: ("🌦️", "Light Rain", "லேசான மழை"),
    63: ("🌧️", "Moderate Rain", "மிதமான மழை"),
    65: ("🌧️", "Heavy Rain", "கனமழை"),
    80: ("🌦️", "Rain Showers", "மழைத்தூறல்"),
    81: ("🌧️", "Moderate Showers", "மிதமான மழைத்தூறல்"),
    82: ("⛈️", "Heavy Showers", "கனமழைத்தூறல்"),
    95: ("⛈️", "Thunderstorm", "இடியுடன் மழை"),
}


def build_weather_advisory(temp: float, humidity: float, rainfall: float):
    """Return practical farming advisory (EN, TA) derived from weather conditions."""
    if rainfall >= 5.0:
        return (
            "Rain expected — postpone pesticide spraying and inspect field drainage.",
            "மழை எதிர்பார்க்கப்படுகிறது — பூச்சி மருந்து தெளிப்பதை ஒத்திவைத்து வடிகாலை சரிபார்க்கவும்.",
        )
    if temp >= 35.0:
        return (
            "High temperature — irrigate early morning or late evening to reduce evaporation loss.",
            "அதிக வெப்பம் — ஆவியாதல் இழப்பைக் குறைக்க அதிகாலை அல்லது மாலையில் நீர்ப்பாசனம் செய்யவும்.",
        )
    if humidity >= 80.0:
        return (
            "High humidity — monitor crops closely for fungal leaf spots and blight.",
            "அதிக ஈரப்பதம் — இலைப் புள்ளி மற்றும் கருகல் பூஞ்சை நோய்களைக் கவனமாகக் கண்காணிக்கவும்.",
        )
    return (
        "Favorable weather for routine field operations, fertilization, and crop monitoring.",
        "வழக்கமான வயல் பணிகள், உரமிடுதல் மற்றும் பயிர் கண்காணிப்புக்கு உகந்த வானிலை.",
    )
