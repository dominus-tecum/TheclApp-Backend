from sqlalchemy import Column, Integer, String, DateTime
from app.database_base import Base  # Import Base from your centralized database.py
import datetime

class VideoSession(Base):
    __tablename__ = "video_sessions"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Add more fields as needed (appointment_id, participants, etc.)