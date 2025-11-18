from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User
from .schemas import UserRegister, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: UserRegister):
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        
        # COMMON FIELDS FOR ALL USERS
        name=user.name,
        phone_number=user.phone_number,
        emirates_id=user.emirates_id,
        passport_number=user.passport_number,
        
        # STAFF-SPECIFIC FIELDS
        specialization=user.specialization,
        department=user.department
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user