from app.database_base import Base  # <-- Import Base directly from database_base
from app.database import engine     # <-- Assuming engine is defined in app/database.py

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created!")