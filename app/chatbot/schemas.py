from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

class ChatLogRead(BaseModel):
    id: int
    user_id: Optional[str]
    message: str
    response: str
    language: str
    timestamp: datetime

    class Config:
        orm_mode = True

class CheckInCreate(BaseModel):
    mood: int  # 1-5
    notes: Optional[str] = None
    user_id: str

class CheckInRead(BaseModel):
    id: int
    user_id: str
    mood: int
    notes: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True

class ProgressSummary(BaseModel):
    user_id: str
    average_mood: float
    check_in_count: int
    latest_mood: Optional[int] = None
    latest_notes: Optional[str] = None
    latest_timestamp: Optional[datetime] = None