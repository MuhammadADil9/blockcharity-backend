from sqlalchemy.orm import Session
from core.database import SessionLocal
from repositories.campaign_repo import CampaignRepository
from repositories.user_repo import UserRepository
import logging

logger = logging.getLogger(__name__)

async def handle_campaign_created(args, receipt):
    """Save new campaign from event"""
    db = SessionLocal()
    try:
        # Ensure user exists (distributor)
        user_repo = UserRepository(db)
        user = user_repo.get_by(address=args['distributor'])
        if not user:
            user_repo.create(address=args['distributor'])

        # Create campaign record
        campaign_repo = CampaignRepository(db)
        campaign_repo.upsert(
            unique_fields={'id': args['campaignId']},
            id=args['campaignId'],
            distributor_address=args['distributor'],
            milestone_amount=args['milestone'],
            current_amount=0,
            is_active=1,
            status=0,
            tx_hash=receipt['transactionHash'].hex()
        )
        logger.info(f"Campaign {args['campaignId']} saved")
    finally:
        db.close()