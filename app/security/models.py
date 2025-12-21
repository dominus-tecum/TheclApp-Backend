# app/security/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database_base import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # 'root_detected', 'debugger_attached', etc.
    severity = Column(String(20), nullable=False)    # 'low', 'medium', 'high', 'critical'
    user_id = Column(String(255), nullable=True)     # Optional: link to user
    device_info = Column(JSON, nullable=True)        # Platform, version, model
    additional_data = Column(JSON, nullable=True)    # Extra context
    ip_address = Column(String(45), nullable=True)   # Client IP
    user_agent = Column(Text, nullable=True)         # Device/browser info
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())