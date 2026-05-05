import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from config.database import SessionLocal
from repositories.campaign_repo import CampaignRepository
import logging

logger = logging.getLogger(__name__)

class TimerService:
    """
    Handles scheduling and checking of proof upload and voting deadlines.
    Deadlines are stored in the campaign table.
    """
    
    def __init__(self):
        self.running = True

    def schedule_proof_deadline(self, campaign_id: int, hours: int = 48) -> None:
        """Store deadline in DB when milestone is achieved."""
        db = SessionLocal()
        try:
            repo = CampaignRepository(db)
            deadline = datetime.utcnow() + timedelta(hours=hours)
            repo.update(campaign_id, proof_deadline=deadline)
            logger.info(f"Proof deadline set for campaign {campaign_id} at {deadline}")
        finally:
            db.close()

    def schedule_voting_deadline(self, campaign_id: int, hours: int = 24) -> None:
        """Store deadline in DB when proof is uploaded."""
        db = SessionLocal()
        try:
            repo = CampaignRepository(db)
            deadline = datetime.utcnow() + timedelta(hours=hours)
            repo.update(campaign_id, voting_deadline=deadline)
            logger.info(f"Voting deadline set for campaign {campaign_id} at {deadline}")
        finally:
            db.close()

    async def check_expired_deadlines(self) -> None:
        """Periodic task: find campaigns with expired deadlines and trigger actions."""
        while self.running:
            db = SessionLocal()
            try:
                repo = CampaignRepository(db)
                now = datetime.utcnow()

                # Check proof deadlines (activity_status = milestoneAchieved = 1)
                campaigns_expired_proof = db.query(Campaign).filter(
                    Campaign.activity_status == 1,
                    Campaign.proof_deadline <= now,
                    Campaign.proof_deadline.isnot(None)
                ).all()

                for campaign in campaigns_expired_proof:
                    logger.info(f"Proof deadline expired for campaign {campaign.id}. Force cancelling.")
                    from services.campaign_service import CampaignService
                    cs = CampaignService(db)
                    cs.force_cancel_no_proof(campaign.id)
                    # Clear deadline to avoid re-trigger
                    repo.update(campaign.id, proof_deadline=None)

                # Check voting deadlines (activity_status = voting = 3)
                campaigns_expired_voting = db.query(Campaign).filter(
                    Campaign.activity_status == 3,
                    Campaign.voting_deadline <= now,
                    Campaign.voting_deadline.isnot(None)
                ).all()

                for campaign in campaigns_expired_voting:
                    logger.info(f"Voting deadline expired for campaign {campaign.id}. Triggering result.")
                    from services.campaign_service import CampaignService
                    cs = CampaignService(db)
                    cs.trigger_result(campaign.id)
                    # Clear deadline to avoid re-trigger
                    repo.update(campaign.id, voting_deadline=None)

            except Exception as e:
                logger.error(f"Error checking deadlines: {e}")
            finally:
                db.close()

            await asyncio.sleep(60)  # Check every minute

    async def start(self):
        """Start the background checker."""
        asyncio.create_task(self.check_expired_deadlines())
        logger.info("TimerService started")