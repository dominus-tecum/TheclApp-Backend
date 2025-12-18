import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
import json
import os
from pathlib import Path
from datetime import datetime

class SkinAwarenessApp:
    def __init__(self, model_path, class_json_path):
        self.model = tf.keras.models.load_model(model_path)
        with open(class_json_path, 'r') as f:
            self.class_indices = json.load(f)
        self.class_names = {v: k for k, v in self.class_indices.items()}
        
        # Medical information for each condition
        self.condition_info = {
            'Acne': {
                'description': 'Common skin condition with pimples, blackheads, and inflammation',
                'urgency': 'low',
                'action': 'Consult dermatologist for treatment options'
            },
            'Benign growths and moles': {
                'description': 'Typically harmless skin growths that should be monitored for changes',
                'urgency': 'low', 
                'action': 'Regular monitoring; see doctor if changes occur'
            },
            'Infectious Skin disease': {
                'description': 'Skin conditions caused by bacteria, viruses, or fungi',
                'urgency': 'medium',
                'action': 'Medical evaluation recommended for proper treatment'
            },
            'Inflammatory Skin Condition': {
                'description': 'Skin inflammation that may include redness, swelling, or irritation',
                'urgency': 'medium',
                'action': 'Dermatologist consultation advised'
            },
            'Sun_Sunlight_Damage': {
                'description': 'Skin changes due to sun exposure, including sun spots and damage',
                'urgency': 'low',
                'action': 'Sun protection; regular skin checks'
            },
            'Suspicious Growth': {
                'description': 'Skin growth that requires medical evaluation to rule out concerns',
                'urgency': 'high',
                'action': 'Urgent dermatologist evaluation recommended'
            },
            'Unknown_Normal': {
                'description': 'Appears to be normal skin or common benign condition',
                'urgency': 'low', 
                'action': 'Continue regular skin monitoring'
            },
            'Warts': {
                'description': 'Small, rough growths caused by viral infection',
                'urgency': 'low',
                'action': 'Can be treated by dermatologist if bothersome'
            },
            'pigment disorder': {
                'description': 'Changes in skin coloring or pigmentation',
                'urgency': 'low',
                'action': 'Dermatologist evaluation for accurate diagnosis'
            }
        }
    
    def predict_image(self, image_path):
        """Predict skin condition from image"""
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        predictions = self.model.predict(img_array, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        # Get top 3 predictions
        top_k_indices = np.argsort(predictions[0])[-3:][::-1]
        top_predictions = []
        
        for idx in top_k_indices:
            top_predictions.append({
                'class_name': self.class_names[idx],
                'confidence': float(predictions[0][idx])
            })
        
        return {
            'primary_prediction': {
                'class_name': self.class_names[predicted_class_idx],
                'confidence': float(confidence)
            },
            'top_predictions': top_predictions
        }
    
    def get_confidence_level(self, confidence):
        """Determine confidence level with emoji and color"""
        if confidence > 0.7:
            return '🟢 HIGH', 'high'
        elif confidence > 0.5:
            return '🟡 MODERATE', 'medium'
        else:
            return '🔴 LOW', 'low'
    
    def get_urgency_message(self, condition_name):
        """Get urgency level and message"""
        info = self.condition_info.get(condition_name, {
            'description': 'Skin condition requiring evaluation',
            'urgency': 'medium',
            'action': 'Consult healthcare professional'
        })
        
        urgency_map = {
            'high': ('🚨 URGENT', 'Schedule appointment soon'),
            'medium': ('⚠️  RECOMMENDED', 'Schedule when convenient'),
            'low': ('✅ ROUTINE', 'Next regular checkup')
        }
        
        return info, urgency_map[info['urgency']]
    
    def generate_patient_report(self, image_path):
        """Generate complete patient-friendly report"""
        result = self.predict_image(image_path)
        primary = result['primary_prediction']
        
        # Confidence level
        confidence_emoji, confidence_level = self.get_confidence_level(primary['confidence'])
        
        # Condition information
        condition_info, (urgency_emoji, urgency_timing) = self.get_urgency_message(primary['class_name'])
        
        # Generate report
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'image_name': Path(image_path).name,
            'primary_prediction': primary['class_name'],
            'confidence': primary['confidence'],
            'confidence_level': f"{confidence_emoji} {confidence_level.upper()} CONFIDENCE",
            'condition_description': condition_info['description'],
            'urgency': f"{urgency_emoji} {urgency_timing}",
            'recommended_action': condition_info['action'],
            'alternative_conditions': result['top_predictions'][1:3],  # Skip first (primary)
            'disclaimer': 'This AI analysis is for educational purposes only and should not replace professional medical advice.'
        }
        
        return report
    
    def display_report(self, report):
        """Display beautiful patient-friendly report"""
        print("\n" + "="*60)
        print("🎯 SKIN AWARENESS ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📅 Analysis Date: {report['timestamp']}")
        print(f"🖼️  Image: {report['image_name']}")
        
        print(f"\n🔍 PRIMARY FINDING:")
        print(f"   Condition: {report['primary_prediction']}")
        print(f"   Confidence: {report['confidence_level']}")
        print(f"   Description: {report['condition_description']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   Action: {report['recommended_action']}")
        print(f"   Timing: {report['urgency']}")
        
        if report['alternative_conditions']:
            print(f"\n🔍 OTHER POSSIBILITIES:")
            for i, alt in enumerate(report['alternative_conditions'], 1):
                print(f"   {i}. {alt['class_name']} ({alt['confidence']:.1%} confidence)")
        
        print(f"\n📋 NEXT STEPS:")
        print("   1. Save this report for your records")
        print("   2. Share with your healthcare provider")
        print("   3. Monitor for any changes")
        print("   4. Schedule professional evaluation")
        
        print(f"\n⚠️  IMPORTANT:")
        print(f"   {report['disclaimer']}")
        print("="*60)

def main():
    # Initialize the app
    MODEL_PATH = r"D:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2\skin_model_finetuned_20251023-225002.keras"
    CLASS_JSON_PATH = r"D:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2\class_indices.json"
    
    app = SkinAwarenessApp(MODEL_PATH, CLASS_JSON_PATH)
    
    # Test folder
    TEST_FOLDER = r"D:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2\post_train_test_picture"
    test_folder = Path(TEST_FOLDER)
    
    if not test_folder.exists():
        print(f"❌ Test folder not found: {TEST_FOLDER}")
        return
    
    # Find images
    image_files = list(test_folder.glob('*.jpg')) + list(test_folder.glob('*.png')) + list(test_folder.glob('*.jpeg'))
    
    if not image_files:
        print("❌ No images found in test folder")
        return
    
    print(f"🧪 SKIN AWARENESS APP")
    print(f"Found {len(image_files)} images to analyze")
    print("="*50)
    
    for image_path in image_files:
        print(f"\n📊 Analyzing: {image_path.name}")
        report = app.generate_patient_report(str(image_path))
        app.display_report(report)
        
        # Ask if user wants to continue
        if image_path != image_files[-1]:
            input("\nPress Enter to analyze next image...")

if __name__ == "__main__":
    main()