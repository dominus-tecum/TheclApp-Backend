# create_tables.py
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.fertility.models import *

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
print("Created tables:", list(Base.metadata.tables.keys()))