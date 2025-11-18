from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.authentication.routers import get_current_user  # Adjust as your structure requires
from app.authentication.services import require_role     # Adjust as your structure requires
from .services import generate_agora_token
from .models import VideoSession
from .schemas import VideoTokenRequest, VideoTokenResponse
from app.database import get_db

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/token", response_model=VideoTokenResponse)
def get_video_token(
    req: VideoTokenRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    require_role(current_user, allowed_roles=["doctor", "admin", "patient"])

    token = generate_agora_token(req.channel_name, req.uid)
    expire_in = 3600

    # Log session for audit/compliance
    session = VideoSession(channel_name=req.channel_name, user_id=current_user["id"])
    db.add(session)
    db.commit()
    db.refresh(session)

    return VideoTokenResponse(
        token=token,
        channel_name=req.channel_name,
        uid=req.uid,
        expire_in=expire_in,
    )