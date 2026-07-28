import cv2
import numpy as np
from ultralytics import YOLO
import os

# Load pre-trained model (or train custom model)
# For now, we'll use a custom model for penis detection
# If not available, use manual marking fallback

class PenisDetector:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load trained YOLO model for penis detection"""
        model_path = "models/penis_detection.pt"
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            print("⚠️ Model not found. Using manual detection fallback.")
            self.model = None
    
    def detect_penis(self, image_path: str):
        """Detect penis in image and return bounding box"""
        if self.model:
            results = self.model(image_path)
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    # Get the largest detected object
                    box = boxes[0].xyxy[0].tolist()
                    return {
                        "success": True,
                        "x1": box[0], "y1": box[1],
                        "x2": box[2], "y2": box[3],
                        "confidence": float(boxes[0].conf[0])
                    }
        
        # Fallback: use edge detection
        return self.detect_penis_manual(image_path)
    
    def detect_penis_manual(self, image_path: str):
        """Fallback: Use edge detection to find elongated shape"""
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image"}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find elongated contour (likely penis)
        best_contour = None
        best_elongation = 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 0 and h > 0:
                elongation = max(w, h) / min(w, h)
                area = cv2.contourArea(contour)
                if elongation > 2 and area > 1000:
                    if elongation > best_elongation:
                        best_elongation = elongation
                        best_contour = (x, y, w, h)
        
        if best_contour:
            x, y, w, h = best_contour
            return {
                "success": True,
                "x1": x, "y1": y,
                "x2": x + w, "y2": y + h,
                "confidence": 0.6
            }
        
        return {"success": False, "error": "Could not detect penis"}


detector = PenisDetector()


def measure_from_detection(image_path: str, card_width_pixels: float, inches_per_pixel: float):
    """Measure penis length from detected boundaries"""
    result = detector.detect_penis(image_path)
    
    if not result["success"]:
        return result
    
    # Calculate length in pixels
    length_pixels = result["y2"] - result["y1"]  # Vertical measurement
    # Or use horizontal if horizontal orientation
    if (result["x2"] - result["x1"]) > length_pixels:
        length_pixels = result["x2"] - result["x1"]
    
    length_inches = length_pixels * inches_per_pixel
    
    return {
        "success": True,
        "length_inches": length_inches,
        "confidence": result["confidence"],
        "bounding_box": (result["x1"], result["y1"], result["x2"], result["y2"])
    }