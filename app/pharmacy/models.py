from app.database_base import Base
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database_base import Base
from sqlalchemy.orm import relationship

class Pharmacy(Base):
    __tablename__ = "pharmacies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone_number = Column(String(50), nullable=False)
    address = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)
    users = relationship("User", back_populates="pharmacy")

class PharmacyMedication(Base):
    __tablename__ = "pharmacy_medications"
    
    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), nullable=False)
    medication_name = Column(String(200), nullable=False)
    strength = Column(String(50), nullable=True) 
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)