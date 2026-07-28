import os
import shutil
import random
import math

# Update these paths as needed
train_dir = r"d:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2\train"
test_dir = r"d:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2\test"

os.makedirs(test_dir, exist_ok=True)

# For each class folder in train
for class_name in os.listdir(train_dir):
    class_path = os.path.join(train_dir, class_name)
    if not os.path.isdir(class_path):
        continue

    # Make corresponding test class folder
    test_class_path = os.path.join(test_dir, class_name)
    os.makedirs(test_class_path, exist_ok=True)

    # List images in class
    images = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
    n_test = math.ceil(len(images) * 0.26)
    test_images = random.sample(images, n_test)

    # Move images
    for img_name in test_images:
        src = os.path.join(class_path, img_name)
        dst = os.path.join(test_class_path, img_name)
        shutil.move(src, dst)
    print(f"Moved {len(test_images)} images from '{class_name}' to test set.")

print("Dataset split complete!")