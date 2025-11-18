# find_model_location.py
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Searching for CesareanSectionEntry model...")

try:
    from main import CesareanSectionEntry
    print("✅ Found in: main.py")
except ImportError as e:
    print("❌ Not in main.py")

try:
    from app.models import CesareanSectionEntry
    print("✅ Found in: app.models")
except ImportError as e:
    print("❌ Not in app.models")

try:
    from models import CesareanSectionEntry
    print("✅ Found in: models.py")
except ImportError as e:
    print("❌ Not in models.py")

try:
    from app.database import CesareanSectionEntry
    print("✅ Found in: app.database")
except ImportError as e:
    print("❌ Not in app.database")