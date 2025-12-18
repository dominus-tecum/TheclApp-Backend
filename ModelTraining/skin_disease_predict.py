# app.py
from fastapi import FastAPI, File, UploadFile, HTTPException
import tensorflow as tf
from PIL import Image
import numpy as np
import io

app = FastAPI(title="Skin Disease Prediction API")

# ==========================
# 1️⃣ Load Trained Model
# ==========================
MODEL_PATH = r"backend/ModelTraining/SkinAnalysis/SkinDisease/skin_disease_mobilenetv2_tf.keras"
model = tf.keras.models.load_model(MODEL_PATH)

# Replace with your actual class names
class_names = [
    'Melanoma', 'Basal Cell Carcinoma', 'Benign Keratosis', 'Dermatofibroma',
    'Vascular Lesion', 'Nevus', 'Actinic Keratosis', 'Squamous Cell Carcinoma',
    'Seborrheic Keratosis', 'Lentigo', 'Acne', 'Psoriasis', 'Eczema',
    'Rosacea', 'Vitiligo', 'Cellulitis', 'Impetigo', 'Tinea', 'Scabies', 'Urticaria',
    'Lichen Planus', 'Other'
]

# Optional: Descriptions for each class
class_descriptions = {
    'Melanoma': "A serious form of skin cancer that develops in melanocytes.",
    'Basal Cell Carcinoma': "A common skin cancer that arises from basal cells.",
    'Benign Keratosis': "Non-cancerous skin growths often caused by sun exposure.",
    'Dermatofibroma': "A benign skin nodule, usually firm and small.",
    'Vascular Lesion': "An abnormality of blood vessels in the skin.",
    'Nevus': "A mole or birthmark, usually harmless.",
    'Actinic Keratosis': "A rough, scaly patch caused by years of sun exposure.",
    'Squamous Cell Carcinoma': "A common skin cancer originating in squamous cells.",
    'Seborrheic Keratosis': "Non-cancerous, wart-like growths on the skin.",
    'Lentigo': "A small pigmented spot on the skin, often due to sun exposure.",
    'Acne': "A skin condition that occurs when hair follicles become clogged.",
    'Psoriasis': "A chronic disease causing red, scaly skin patches.",
    'Eczema': "An inflammatory skin condition causing itchy, red skin.",
    'Rosacea': "A chronic skin condition causing redness and visible blood vessels.",
    'Vitiligo': "Loss of skin color in patches due to lack of melanin.",
    'Cellulitis': "A bacterial infection of the skin and tissues beneath.",
    'Impetigo': "A contagious bacterial skin infection, common in children.",
    'Tinea': "A fungal infection of the skin (ringworm).",
    'Scabies': "A skin infestation by the mite Sarcoptes scabiei.",
    'Urticaria': "Also known as hives, a skin rash triggered by allergies.",
    'Lichen Planus': "An inflammatory condition causing purplish, itchy bumps.",
    'Other': "Other or unclassified skin condition."
}

# ==========================
# 2️⃣ Image Preprocessing
# ==========================
def preprocess_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))  # model input size
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # batch dimension
        return img_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {e}")

# ==========================
# 3️⃣ Prediction Endpoint
# ==========================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img_array = preprocess_image(image_bytes)
        preds = model.predict(img_array)
        idx = int(np.argmax(preds))
        predicted_class = class_names[idx]
        confidence = float(np.max(preds))
        description = class_descriptions.get(predicted_class, "No description available.")
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

# ==========================
# 4️⃣ Health Check
# ==========================
@app.get("/health")
async def health():
    return {"status": "ok"}
