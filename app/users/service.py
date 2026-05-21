from sqlalchemy.orm import Session
from app.models import User
from app.authentication.auth import get_password_hash

def create_user(db: Session, user_data):
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        phone_number=user_data.phone_number,
        role="patient",
        status="pending",
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    from app.authentication.auth import verify_password
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user