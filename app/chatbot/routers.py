from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from .schemas import (
    ChatRequest, ChatResponse, ChatLogRead,
    CheckInCreate, CheckInRead, ProgressSummary
)
from .services import (
    get_chatbot_response, save_chat_log,
    create_check_in, get_check_ins, get_progress_summary
)
from app.database import get_db

router = APIRouter()

# -----------------------------
# Chatbot Endpoint
# -----------------------------
@router.post("/chatbot/", response_model=ChatResponse)
async def chatbot_endpoint(
    request: ChatRequest,
    language: str = Query("en", description="Language code, e.g., 'en', 'ar', 'hi'"),
    db: Session = Depends(get_db)
):
    """
    AI/NLP-enabled chatbot endpoint.
    Supports multilingual responses via `language` query parameter.
    """
    try:
        reply = get_chatbot_response(
            message=request.message,
            language=language,
            user_id=request.user_id
        )

        # Save chat log with language
        save_chat_log(
            db=db,
            user_id=request.user_id,
            message=request.message,
            response=reply,
            language=language
        )

        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# AI Symptom Checker Endpoint
# -----------------------------
@router.post("/symptom-checker/", response_model=ChatResponse)
async def symptom_checker_endpoint(
    request: ChatRequest,
    language: str = Query("en", description="Language code, e.g., 'en', 'ar', 'hi'"),
    db: Session = Depends(get_db)
):
    """
    AI Symptom Checker endpoint.
    Receives symptom descriptions and provides AI-guided responses.
    """
    try:
        reply = get_chatbot_response(
            message=request.message,
            language=language,
            user_id=request.user_id
        )

        # Save chat log with language and note as symptom check
        save_chat_log(
            db=db,
            user_id=request.user_id,
            message=request.message,
            response=reply,
            language=language
        )

        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Get Chat Logs
# -----------------------------
@router.get("/chatbot/logs/", response_model=list[ChatLogRead])
def get_chat_logs(db: Session = Depends(get_db), user_id: str = None):
    from .models import ChatLog
    query = db.query(ChatLog)
    if user_id:
        query = query.filter(ChatLog.user_id == user_id)
    return query.order_by(ChatLog.timestamp.desc()).all()

# -----------------------------
# Check-in Endpoints
# -----------------------------
@router.post("/checkin/", response_model=CheckInRead)
def check_in(create: CheckInCreate, db: Session = Depends(get_db)):
    checkin = create_check_in(db, create.user_id, create.mood, create.notes)
    return checkin

@router.get("/checkin/", response_model=list[CheckInRead])
def get_user_checkins(user_id: str, db: Session = Depends(get_db)):
    return get_check_ins(db, user_id)

@router.get("/progress/", response_model=ProgressSummary)
def progress_summary(user_id: str, db: Session = Depends(get_db)):
    return get_progress_summary(db, user_id)
