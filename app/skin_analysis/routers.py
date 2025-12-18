from fastapi import APIRouter, File, UploadFile, HTTPException
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import json
import os
from pathlib import Path
import logging


# Add this after imports
logger = logging.getLogger(__name__)

# ✅ REMOVED prefix from router - it will be added in main.py
router = APIRouter(tags=["Skin Analysis"])

# Use your existing SkinDiseasePredictor class
class SkinDiseasePredictor:
    def __init__(self, model_path, class_json_path):
        self.model = tf.keras.models.load_model(model_path)
        with open(class_json_path, 'r') as f:
            self.class_indices = json.load(f)
        self.class_names = {v: k for k, v in self.class_indices.items()}
        
    def predict_image_bytes(self, image_bytes, top_k=3):
        """Predict skin disease from image bytes (for FastAPI)"""
        # Convert bytes to image and preprocess
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Use the same preprocessing as your test script
        from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
        img_array = preprocess_input(img_array)
        
        # Make prediction
        predictions = self.model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        # Get top K predictions
        top_k_indices = np.argsort(predictions[0])[-top_k:][::-1]
        top_k_predictions = []
        
        for idx in top_k_indices:
            top_k_predictions.append({
                'class_name': self.class_names[idx],
                'confidence': float(predictions[0][idx])
            })
        
        return {
            'primary_prediction': {
                'class_name': self.class_names[predicted_class_idx],
                'confidence': float(confidence)
            },
            'top_predictions': top_k_predictions
        }

# Initialize predictor with your paths
MODEL_PATH = r"D:\TheclApp\BACKEND\app\skin_analysis\skin_model_finetuned_20251023-225002.keras"
CLASS_JSON_PATH = r"D:\TheclApp\BACKEND\app\skin_analysis\class_indices.json"

try:
    predictor = SkinDiseasePredictor(MODEL_PATH, CLASS_JSON_PATH)
    print("✅ Skin disease model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load skin model: {e}")
    predictor = None

@router.post("/predict-from-upload")
async def predict_from_upload(file: UploadFile = File(...)):
    """Predict from uploaded image (gallery)"""
    return await predict_skin_disease(file)

@router.post("/predict-from-camera") 
async def predict_from_camera(file: UploadFile = File(...)):
    """Predict from camera capture"""
    return await predict_skin_disease(file)

async def predict_skin_disease(file: UploadFile):
    """Shared prediction logic"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Skin model not available")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_bytes = await file.read()
        result = predictor.predict_image_bytes(image_bytes, top_k=3)
        
        return {
            'success': True,
            **result,
            'message': 'Always consult a healthcare professional for proper diagnosis!'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/classes")
async def get_available_classes():
    if predictor is None:
        raise HTTPException(status_code=503, detail="Skin analysis service is not available")
    
    try:
        # Use the original class_indices for the correct mapping
        classes = [
            {
                'class_id': class_id,
                'class_name': class_name
            }
            for class_name, class_id in predictor.class_indices.items()
        ]
        
        return {
            'total_classes': len(classes),
            'available_classes': list(predictor.class_indices.keys()),  # Just the names
            'classes': sorted(classes, key=lambda x: x['class_name'])
        }
        
    except Exception as e:
        print(f"❌ Classes endpoint error: {e}")  # ✅ Use print instead of logger
        raise HTTPException(status_code=500, detail=f"Error retrieving classes: {str(e)}")










@router.get("/health")
async def skin_model_health():
    """Check if skin model is loaded and ready"""
    return {
        'model_loaded': predictor is not None,
        'classes_loaded': predictor.class_indices is not None if predictor else False,
        'total_classes': len(predictor.class_indices) if predictor else 0
    }