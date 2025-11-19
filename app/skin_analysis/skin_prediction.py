from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
import json
import os
from pathlib import Path
import uuid
from datetime import datetime
import io
import logging
import tempfile
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Skin Analysis"])  # Remove the prefix

class SkinDiseasePredictor:
    def __init__(self, model_path: str, class_json_path: str):
        try:
            self.model = tf.keras.models.load_model(model_path)
            with open(class_json_path, 'r') as f:
                self.class_indices = json.load(f)
            self.class_names = {v: k for k, v in self.class_indices.items()}
            logger.info(f"✅ Model loaded successfully. Classes: {len(self.class_names)}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def predict_image(self, img_array: np.ndarray, top_k: int = 3) -> Dict:
        """Predict skin disease from image array"""
        try:
            # Preprocess image
            img_array = preprocess_input(img_array)
            
            # Make prediction
            predictions = self.model.predict(img_array, verbose=0)
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
                'top_predictions': top_k_predictions,
                'all_predictions': {self.class_names[i]: float(pred) for i, pred in enumerate(predictions[0])}
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
current_dir = os.path.dirname(os.path.abspath(__file__))           

# Initialize the predictor
MODEL_PATH = os.path.join(current_dir, "skin_model_finetuned_20251023-225002.keras")
CLASS_JSON_PATH = os.path.join(current_dir, "class_indices.json")

try:
    predictor = SkinDiseasePredictor(MODEL_PATH, CLASS_JSON_PATH)
    logger.info("🚀 Skin Disease Predictor initialized successfully!")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    predictor = None

# In-memory storage for analysis results
analysis_storage = {}

def validate_and_process_image(file_contents: bytes, filename: str) -> np.ndarray:
    """Validate and process uploaded image file for model prediction"""
    try:
        # Validate file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        file_ext = Path(filename).suffix.lower()
        if file_ext not in valid_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Supported types: {', '.join(valid_extensions)}")
        
        # Try to open and process the image
        try:
            img = image.load_img(io.BytesIO(file_contents), target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as img_error:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(img_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")




# CHANGE ONLY THESE ENDPOINT NAMES:

@router.post("/predict-from-upload")
async def predict_from_upload(file: UploadFile = File(...)):
    """
    Predict from uploaded image (gallery)
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Skin analysis service is not available")
    
    print(f"🔍 DEBUG: File received - name: {file.filename}, type: {file.content_type}")
    
    try:
        # Read file contents
        contents = await file.read()
        print(f"🔍 DEBUG: File size: {len(contents)} bytes")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Debug: Check first few bytes
        print(f"🔍 DEBUG: First 10 bytes: {contents[:10]}")
        
        # Validate and process image
        img_array = validate_and_process_image(contents, file.filename)
        print(f"🔍 DEBUG: Image processed successfully, array shape: {img_array.shape}")
        
        # Make prediction
        result = predictor.predict_image(img_array, top_k=3)
        print(f"🔍 DEBUG: Prediction completed successfully")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Store analysis result
        analysis_storage[analysis_id] = {
            'analysis_id': analysis_id,
            'filename': file.filename,
            'timestamp': datetime.now().isoformat(),
            'results': result,
            'file_size': len(contents)
        }
        
        return {
            'success': True,
            'analysis_id': analysis_id,
            'primary_prediction': result['primary_prediction'],
            'top_predictions': result['top_predictions'],
            'filename': file.filename
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Prediction failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }




@router.post("/predict-from-camera")
async def predict_from_camera(file: UploadFile = File(...)):
    """
    Predict from camera capture
    """
    # Use the same logic as predict-from-upload
    return await predict_from_upload(file)


@router.get("/health")
async def health_check():
    status = "healthy" if predictor is not None else "unhealthy"
    return {
        'status': status,
        'total_classes': len(predictor.class_names) if predictor else 0,
        'model_loaded': predictor is not None,
        'timestamp': datetime.now().isoformat()
    }

@router.get("/classes")
async def get_available_classes():
    if predictor is None:
        raise HTTPException(status_code=503, detail="Skin analysis service is not available")
    
    classes = [
        {
            'class_name': class_name,
            'class_id': class_id
        }
        for class_id, class_name in predictor.class_names.items()
    ]
    
    return {
        'total_classes': len(classes),
        'classes': sorted(classes, key=lambda x: x['class_name'])
    }