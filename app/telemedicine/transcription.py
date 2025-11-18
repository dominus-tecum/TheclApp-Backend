from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import openai
import os

router = APIRouter()

# Load OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...),
    patient_id: str = Form(...)
):
    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Call OpenAI Whisper API
        with open(tmp_path, "rb") as audio_file:
            transcript = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return JSONResponse({
            "patient_id": patient_id,
            "transcript": transcript.text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
