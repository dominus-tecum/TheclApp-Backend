# create_test_user.py
from main import SessionLocal, User

db = SessionLocal()
try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.id == 5).first()
    if not existing_user:
        test_user = User(
            id=5,
            username="test_patient",
            email="test@example.com", 
            name="Test Patient",
            password_hash="temp_password",  # Required field
            role="PATIENT",  # Required field - must be one of the allowed roles
            is_active=True  # Required field
            # Optional fields can be omitted
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created with ID=5")
    else:
        print("✅ User with ID=5 already exists")
finally:
    db.close()