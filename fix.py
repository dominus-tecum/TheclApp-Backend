# check_user_model.py
from main import User
from sqlalchemy import inspect

print("🔍 User Model Structure:")
print(f"Table name: {User.__tablename__}")

# Get column information
inspector = inspect(User)
for column in inspector.columns:
    print(f"  - {column.name}: {column.type}")

print("\n📋 User model attributes:")
for attr_name in dir(User):
    if not attr_name.startswith('_') and not callable(getattr(User, attr_name)):
        print(f"  - {attr_name}")