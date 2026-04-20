# In donation_handler.py
from services.donation_service import DonationService
from core.database import SessionLocal

async def handle_donation_received(args, receipt):
    db = SessionLocal()
    try:
        service = DonationService(db)
        service.process_donation_event(args, receipt['transactionHash'].hex())
    finally:
        db.close()