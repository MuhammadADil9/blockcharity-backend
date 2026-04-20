from services.campaign_service import CampaignService
from core.database import SessionLocal

async def handle_campaign_created(args, receipt):
    db = SessionLocal()
    try:
        service = CampaignService(db)
        service.sync_campaign_from_event(args, receipt['transactionHash'].hex())
    finally:
        db.close()