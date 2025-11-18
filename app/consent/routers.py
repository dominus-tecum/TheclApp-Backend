from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_consents():
    return {"message": "List of consents"}
