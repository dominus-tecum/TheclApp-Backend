# analyze_image.py
import cv2
import numpy as np

image_path = "C:\\temp\\penis_photo.jpg"

img = cv2.imread(image_path)
if img is None:
    print("Could not read image")
    exit()

height, width = img.shape[:2]
print(f"Image size: {width}x{height}")

# Resize like measurement does
if width > 1000:
    scale = 1000 / width
    new_width = 1000
    new_height = int(height * scale)
    img = cv2.resize(img, (new_width, new_height))
    print(f"Resized to: {new_width}x{new_height}")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Analyze pixel values
min_val = np.min(gray)
max_val = np.max(gray)
mean_val = np.mean(gray)
print(f"\nPixel values - Min: {min_val}, Max: {max_val}, Mean: {mean_val:.1f}")

# Show distribution
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
print(f"\nPixel distribution:")
print(f"  Dark (0-50): {np.sum(hist[0:51]):.0f} pixels")
print(f"  Mid (51-200): {np.sum(hist[51:201]):.0f} pixels")
print(f"  Bright (201-255): {np.sum(hist[201:256]):.0f} pixels")

# Try a reasonable threshold for a pen on black background
# The pen should be bright (high pixel values), background dark (low)
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"\nContours found with threshold=200: {len(contours)}")

if contours:
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    x, y, w, h = cv2.boundingRect(largest)
    print(f"Largest contour: area={area:.0f}, size={w}x{h}")
    
    # Save result
    result = img.copy()
    cv2.drawContours(result, [largest], -1, (0, 255, 0), 2)
    cv2.imwrite("C:\\temp\\correct_contour.jpg", result)
    print("\n✅ Saved to C:\\temp\\correct_contour.jpg")
else:
    print("No contours found with threshold=200")
    print("Try lowering the threshold...")
    
    # Try lower threshold
    for t in [150, 100, 50]:
        _, thresh2 = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours2:
            largest2 = max(contours2, key=cv2.contourArea)
            area2 = cv2.contourArea(largest2)
            x2, y2, w2, h2 = cv2.boundingRect(largest2)
            print(f"  Threshold {t}: {len(contours2)} contours, largest area={area2:.0f}, size={w2}x{h2}")