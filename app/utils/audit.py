# BACKEND/app/utils/audit.py (Python backend file)
from sqlalchemy.orm import Session
from app.models import AuditLog
from datetime import datetime
import json

def log_audit(
    db: Session,
    user_id: int = None,
    username: str = None,
    user_role: str = None,
    action: str = None,
    resource_type: str = None,
    resource_id: int = None,
    patient_id: int = None,
    status: str = 'success',
    purpose: str = None,
    old_value: dict = None,
    new_value: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    audit = AuditLog(
        user_id=user_id,
        username=username,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        patient_id=patient_id,
        status=status,
        purpose=purpose,
        old_value=json.dumps(old_value) if old_value else None,
        new_value=json.dumps(new_value) if new_value else None,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now()
    )
    
    db.add(audit)
    db.commit()
    return audit