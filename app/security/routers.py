# app/security/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.security.models import SecurityEvent
from app.security.schemas import SecurityEventCreate, SecurityEventResponse

router = APIRouter(prefix="/api/security", tags=["security"])

@router.post("/events", response_model=SecurityEventResponse)
async def log_security_event(
    event: SecurityEventCreate,
    db: Session = Depends(get_db)
):
    """Receive security events from mobile app"""
    try:
        db_event = SecurityEvent(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Log to console for debugging
        print(f"🔒 SECURITY EVENT: {event.event_type} (severity: {event.severity})")
        
        return db_event
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to log security event: {e}")
        raise HTTPException(status_code=500, detail="Failed to log security event")

@router.get("/events", response_model=List[SecurityEventResponse])
async def get_security_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get security events (for admin dashboard)"""
    events = db.query(SecurityEvent).order_by(SecurityEvent.created_at.desc()).offset(skip).limit(limit).all()
    return events


# In app/security/routers.py, add:
@router.get("/dashboard")
def security_dashboard(db: Session = Depends(get_db)):
    # Get recent events
    recent_events = db.query(models.SecurityEvent).order_by(
        models.SecurityEvent.created_at.desc()
    ).limit(50).all()
    
    # Get statistics
    event_counts = db.query(
        models.SecurityEvent.event_type,
        func.count(models.SecurityEvent.id)
    ).group_by(models.SecurityEvent.event_type).all()
    
    severity_counts = db.query(
        models.SecurityEvent.severity,
        func.count(models.SecurityEvent.id)
    ).group_by(models.SecurityEvent.severity).all()
    
    return {
        "recent_events": recent_events,
        "statistics": {
            "by_type": dict(event_counts),
            "by_severity": dict(severity_counts),
            "total_events": db.query(models.SecurityEvent).count()
        },
        "backend_status": "operational"
    }




