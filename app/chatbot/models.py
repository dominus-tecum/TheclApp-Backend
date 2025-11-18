from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.database_base import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    message = Column(String, nullable=False)
    response = Column(String, nullable=False)
    language = Column(String, default="en")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class CheckIn(Base):
    __tablename__ = "check_ins"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    mood = Column(Integer, nullable=False)  # e.g. scale from 1 (bad) to 5 (great)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())