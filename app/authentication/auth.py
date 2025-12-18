from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models import User, UserRole
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"🔑 [AUTH] Token check started")
    
    if not token:
        print(f"❌ [AUTH] No token provided")
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"✅ [AUTH] Token decoded successfully")
        
        username: str = payload.get("sub")
        if username is None:
            print(f"❌ [AUTH] No username in token")
            raise credentials_exception
            
    except JWTError as e:
        print(f"❌ [AUTH] JWT Error: {str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        print(f"❌ [AUTH] User not found: {username}")
        raise credentials_exception
    
    # CONVERT TO DICTIONARY - THIS IS CRITICAL
    user_dict = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "phone_number": user.phone_number,
        "department": user.department,
        "specialization": user.specialization
    }
    
    print(f"✅ [AUTH] Returning user: {user.username} (ID: {user.id})")
    return user_dict