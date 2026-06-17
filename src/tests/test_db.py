from config.database import SessionLocal, engine
from models.distributor import Distributor
from models.donor import Donor

try:
    db = SessionLocal()
    print("DB connected")
    print(db.query(Distributor).first())
    print(db.query(Donor).first())
    print("Queries successful")
except Exception as e:
    print(f"Error: {e}")
