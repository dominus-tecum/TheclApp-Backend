from sqlalchemy.orm import Session
from .models import ChatLog, CheckIn
import openai  # for GPT-3.5 integration
import os
from langdetect import detect

# -----------------------------
# FAQS
# -----------------------------
FAQS = {
    "what are your opening hours": {
        "en": "Our hospital operates 24/7.",
        "ar": "يعمل مستشفانا على مدار الساعة طوال أيام الأسبوع.",
        "hi": "हमारा अस्पताल 24/7 खुला रहता है।"
    },
    "how do i book an appointment": {
        "en": "You can book an appointment by providing your preferred date and doctor.",
        "ar": "يمكنك حجز موعد من خلال تزويدنا بالتاريخ والطبيب المفضل لديك.",
        "hi": "आप अपनी पसंदीदा तारीख और डॉक्टर बताकर अपॉइंटमेंट बुक कर सकते हैं।"
    }
}

# -----------------------------
# Intent detection (basic)
# -----------------------------
def detect_intent(message: str) -> str:
    msg = message.lower()
    if any(word in msg for word in ["hello", "hi", "namaste", "مرحبا"]):
        return "greeting"
    if "appointment" in msg or "book" in msg or "موعد" in msg or "बुक" in msg:
        return "book_appointment"
    if "prescription" in msg or "دواء" in msg or "दवाई" in msg:
        return "request_prescription"
    return "unknown"

# -----------------------------
# Language detection
# -----------------------------
def detect_language(message: str) -> str:
    try:
        lang = detect(message)
        if lang not in ["en", "ar", "hi"]:
            return "en"
        return lang
    except:
        return "en"

# -----------------------------
# FAQ matching
# -----------------------------
def match_faq(message: str, language: str):
    msg = message.lower()
    for q, answers in FAQS.items():
        if q in msg:
            return answers.get(language, answers["en"])
    return None

# -----------------------------
# Core Chatbot Response
# -----------------------------
def get_chatbot_response(message: str, language: str = None, user_id: str = None, mode: str = "chat") -> str:
    """
    Returns response to user message.
    mode="chat" for general chatbot
    mode="symptom_checker" for health symptom checking
    """
    # 1) Detect language
    if language is None:
        language = detect_language(message)

    # 2) FAQ match
    faq_answer = match_faq(message, language)
    if faq_answer:
        return faq_answer

    # 3) Intent detection (only for general chat)
    if mode == "chat":
        intent = detect_intent(message)
        if intent == "greeting":
            greetings = {
                "en": "Hello! How can I assist you today?",
                "ar": "مرحبًا! كيف يمكنني مساعدتك اليوم؟",
                "hi": "नमस्ते! मैं आपकी आज कैसे मदद कर सकता हूँ?"
            }
            return greetings.get(language, greetings["en"])
        elif intent == "book_appointment":
            responses = {
                "en": "To book an appointment, please provide your preferred doctor and date.",
                "ar": "لحجز موعد، يرجى تزويدنا بالطبيب والتاريخ المفضلين.",
                "hi": "अपॉइंटमेंट बुक करने के लिए, कृपया अपना पसंदीदा डॉक्टर और तारीख बताएं।"
            }
            return responses.get(language, responses["en"])
        elif intent == "request_prescription":
            responses = {
                "en": "Please provide your prescription details or medication name.",
                "ar": "يرجى تقديم تفاصيل الوصفة أو اسم الدواء.",
                "hi": "कृपया अपनी प्रिस्क्रिप्शन विवरण या दवा का नाम प्रदान करें।"
            }
            return responses.get(language, responses["en"])

    # 4) AI/NLP response using GPT-3.5
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        if mode == "symptom_checker":
            system_prompt = (
                f"You are a helpful medical assistant. "
                f"Provide guidance on symptoms described by the user. "
                f"Respond in {language}. "
                f"Do not give a diagnosis, only general advice and steps to seek care."
            )
        else:
            system_prompt = f"You are a helpful assistant responding in {language}."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        ai_message = response.choices[0].message.content.strip()
        return ai_message
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "An error occurred. Please try again later."

# -----------------------------
# Save chat log
# -----------------------------
def save_chat_log(db: Session, user_id: str, message: str, response: str, language: str):
    chat_log = ChatLog(
        user_id=user_id,
        message=message,
        response=response,
        language=language
    )
    db.add(chat_log)
    db.commit()
    db.refresh(chat_log)
    return chat_log

# -----------------------------
# Check-in functions
# -----------------------------
def create_check_in(db: Session, user_id: str, mood: int, notes: str = None):
    check_in = CheckIn(user_id=user_id, mood=mood, notes=notes)
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    return check_in

def get_check_ins(db: Session, user_id: str):
    return db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(CheckIn.timestamp.desc()).all()

def get_progress_summary(db: Session, user_id: str):
    check_ins = db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(CheckIn.timestamp.desc()).all()
    count = len(check_ins)
    if count == 0:
        return {
            "user_id": user_id,
            "average_mood": 0,
            "check_in_count": 0,
            "latest_mood": None,
            "latest_notes": None,
            "latest_timestamp": None,
        }
    avg_mood = sum(c.mood for c in check_ins) / count
    latest = check_ins[0]
    return {
        "user_id": user_id,
        "average_mood": avg_mood,
        "check_in_count": count,
        "latest_mood": latest.mood,
        "latest_notes": latest.notes,
        "latest_timestamp": latest.timestamp,
    }
