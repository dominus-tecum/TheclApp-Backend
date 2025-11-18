# recreate_postnatal_tables.py
from app.postnatal.models import Base
from app.database import engine

def recreate_tables():
    # Drop all postnatal tables
    Base.metadata.drop_all(bind=engine, tables=[
        Base.metadata.tables['postnatal_entries'],
        Base.metadata.tables['postnatal_profiles']
    ])
    
    # Create all postnatal tables
    Base.metadata.create_all(bind=engine, tables=[
        Base.metadata.tables['postnatal_entries'],
        Base.metadata.tables['postnatal_profiles']
    ])
    
    print("Postnatal tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()