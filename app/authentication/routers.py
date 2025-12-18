from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
from .schemas import UserRegister, UserLogin, UserRead
from .service import create_user, authenticate_user
from .auth import create_access_token, get_current_user
from jose import jwt
from app.core.config import settings  # ✅ IMPORT SETTINGS

router = APIRouter(tags=["Authentication"])

# In-memory storage for refresh tokens
REFRESH_TOKENS = {}

# Helper function to create refresh tokens
def create_refresh_token(username: str, user_id: int):
    """Create a refresh token valid for 7 days"""
    expire = datetime.utcnow() + timedelta(days=7)
    refresh_token = jwt.encode(
        {
            "sub": username,
            "user_id": user_id,
            "type": "refresh",
            "exp": expire
        },
        settings.JWT_SECRET_KEY,  # ✅ USE SAME SECRET KEY
        algorithm=settings.ALGORITHM  # ✅ USE SAME ALGORITHM
    )
    
    # Store it in memory
    REFRESH_TOKENS[refresh_token] = {
        "user_id": user_id,
        "username": username,
        "expires_at": expire
    }
    
    return refresh_token

@router.post("/register", response_model=UserRead)
def register(user: UserRegister, db: Session = Depends(get_db)):
    print(f"🔍 REGISTER - Received: {user.dict()}")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        print("❌ REGISTER - Email already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        print("❌ REGISTER - Username already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    created_user = create_user(db, user)
    print(f"✅ REGISTER - User created: {created_user.id}, {created_user.email}, {created_user.username}")
    return created_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"🔍 LOGIN - Attempt: {user.email}")
    
    authenticated_user = authenticate_user(db, user.email, user.password)
    print(f"🔍 LOGIN - User found: {authenticated_user}")
    
    if authenticated_user:
        print(f"🔍 LOGIN - User details: {authenticated_user.email}, {authenticated_user.role}")
    else:
        print("❌ LOGIN - authenticate_user returned None")
    
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 1. Create access token (30 minutes)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": authenticated_user.username}, 
        expires_delta=access_token_expires
    )
    
    # 2. Create refresh token (7 days)
    refresh_token = create_refresh_token(
        username=authenticated_user.username,
        user_id=authenticated_user.id
    )
    
    print(f"✅ LOGIN - Success, tokens created for: {authenticated_user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # ✅ NEW
        "token_type": "bearer", 
        "user": UserRead.from_orm(authenticated_user)
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    Get new access token using refresh token
    """
    print(f"🔍 REFRESH - Attempt with token: {refresh_token[:20]}...")
    
    # Check if token exists
    if refresh_token not in REFRESH_TOKENS:
        print("❌ REFRESH - Token not found in storage")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_data = REFRESH_TOKENS[refresh_token]
    
    # Check if expired
    if datetime.utcnow() > token_data["expires_at"]:
        del REFRESH_TOKENS[refresh_token]  # Clean up expired token
        print("❌ REFRESH - Token expired")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Create new access token (30 minutes)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": token_data["username"]}, 
        expires_delta=access_token_expires
    )
    
    print(f"✅ REFRESH - New access token created for: {token_data['username']}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }

@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user