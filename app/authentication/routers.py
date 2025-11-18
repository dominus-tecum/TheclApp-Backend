from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from .schemas import UserRegister, UserLogin, UserRead
from .service import create_user, authenticate_user
from .auth import create_access_token, get_current_user

router = APIRouter(tags=["Authentication"])

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
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": authenticated_user.username}, 
        expires_delta=access_token_expires
    )
    
    print(f"✅ LOGIN - Success, token created for: {authenticated_user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user": UserRead.from_orm(authenticated_user)
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