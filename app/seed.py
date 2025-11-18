# seed.py
from app.database import SessionLocal, engine
from app.models import User, Prescription

db = SessionLocal()

# Check if user exists
if not db.query(User).filter(User.id == 1).first():
    patient = User(
        id=1,
        username="patient1",
        email="patient1@example.com",
        password="securepassword",
        role="patient"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

db.close()
print("Seed completed")
