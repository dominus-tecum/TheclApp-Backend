# reset_db.py
from main import Base, engine  # ✅ Import from main.py

print("🗑️ Recreating database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Database tables recreated!")
print("📊 Tables created: users, cesarean_section_entries")