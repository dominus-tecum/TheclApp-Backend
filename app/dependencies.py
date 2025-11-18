from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db  # <-- Import get_db from database.py

# Security scheme for JWT tokens
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)  # <-- Now using the get_db from database.py
) -> dict:
    """
    Dependency to get current user from JWT token
    This is a simplified version - you'll need to implement your actual auth logic
    """
    try:
        # TODO: Replace with your actual JWT verification logic
        # For now, this returns a mock user
        token = credentials.credentials
        
        # Mock user data - replace with actual token decoding
        # Example: payload = jwt.decode(token, "YOUR_SECRET_KEY", algorithms=["HS256"])
        user_data = {
            "id": 1,
            "email": "user@example.com",
            "role": "patient"
        }
        
        return user_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional: Role-based dependencies
def get_current_patient(user: dict = Depends(get_current_user)):
    if user.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

def get_current_doctor(user: dict = Depends(get_current_user)):
    if user.get("role") != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user