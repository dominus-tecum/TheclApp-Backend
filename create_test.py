# create_test_user.py
from main import SessionLocal, User
from datetime import datetime

db = SessionLocal()
try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.id == 5).first()
    if not existing_user:
        test_user = User(
            id=5,
            username="test_patient",  # Use username instead
            name="Test Patient", 
            email="test@example.com",
            # Remove hashed_password if it doesn't exist
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created with ID=5")
    else:
        print("✅ User with ID=5 already exists")
finally:
    db.close()