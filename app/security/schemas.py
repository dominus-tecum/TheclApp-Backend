# app/security/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SecurityEventBase(BaseModel):
    event_type: str
    severity: str
    user_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None

class SecurityEventCreate(SecurityEventBase):
    pass

class SecurityEventResponse(SecurityEventBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True