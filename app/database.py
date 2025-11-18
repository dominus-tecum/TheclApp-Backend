from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_base import Base  # <-- use database_base.py

DATABASE_URL = "sqlite:///./hospiapp.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# optional: create tables
Base.metadata.create_all(bind=engine)