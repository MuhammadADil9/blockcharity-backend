import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.donation_repo import DonationRepository
from repositories.campaign_repo import CampaignRepository
from repositories.user_repo import UserRepository
from models.donation import Donation

logger = logging.getLogger(__name__)

class DonationService:
    def __init__(self, db: Session):
        self.donation_repo = DonationRepository(db)
        self.campaign_repo = CampaignRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db

    def process_donation_event(self, event_args: dict, tx_hash: str) -> Optional[Donation]:
        """
        Called by DonationReceived event handler.
        - Ensures donor user exists
 - Updates campaign current_amount
 - Saves donation record
        """
        try:
            campaign_id = event_args['campaignId']
            donor = event_args['donor']
            amount = event_args['amount']

            # Ensure donor exists in users table
            if not self.user_repo.get_by_address(donor):
                self.user_repo.create(address=donor)

            # Update campaign current_amount (add donation)
            campaign = self.campaign_repo.get_by(id=campaign_id)
            if campaign:
                new_amount = int(campaign.current_amount or 0) + int(amount)
                self.campaign_repo.update(campaign_id, current_amount=str(new_amount))
            else:
                logger.warning(f"Campaign {campaign_id} not found for donation event")

            # Save donation (use upsert to avoid duplicate tx_hash)
            donation = self.donation_repo.upsert(
                unique_fields={'tx_hash': tx_hash},
                tx_hash=tx_hash,
                campaign_id=campaign_id,
                donor_address=donor,
                amount=str(amount)
            )
            logger.info(f"Donation recorded: {tx_hash} for campaign {campaign_id}")
            return donation
        except Exception as e:
            logger.error(f"Failed to process donation event: {e}")
            self.db.rollback()
            return None

    def get_donations_by_campaign(self, campaign_id: int, skip: int = 0, limit: int = 100) -> List[Donation]:
        try:
            return self.donation_repo.get_multi_by(campaign_id=campaign_id, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get donations for campaign {campaign_id}: {e}")
            return []

    def get_donations_by_user(self, user_address: str, skip: int = 0, limit: int = 100) -> List[Donation]:
        try:
            return self.donation_repo.get_multi_by(donor_address=user_address, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get donations for user {user_address}: {e}")
            return []

    def has_user_donated_to_campaign(self, user_address: str, campaign_id: int) -> bool:
        """Used by vote validation: check if user donated to this campaign."""
        try:
            donations = self.donation_repo.get_multi_by(
                donor_address=user_address,
                campaign_id=campaign_id,
                limit=1
            )
            return len(donations) > 0
        except Exception as e:
            logger.error(f"Failed to check donation for user {user_address}, campaign {campaign_id}: {e}")
            return False

    def get_user_total_donated(self, user_address: str) -> int:
        """Sum of all donations by user (in wei)."""
        try:
            donations = self.donation_repo.get_multi_by(donor_address=user_address)
            total = sum(int(d.amount) for d in donations) if donations else 0
            return total
        except Exception as e:
            logger.error(f"Failed to compute total donated for {user_address}: {e}")
            return 0

    def get_campaign_total_raised_from_db(self, campaign_id: int) -> int:
        """Sum of all donations for a campaign (from DB)."""
        try:
            donations = self.donation_repo.get_multi_by(campaign_id=campaign_id)
            total = sum(int(d.amount) for d in donations) if donations else 0
            return total
        except Exception as e:
            logger.error(f"Failed to compute total raised for campaign {campaign_id}: {e}")
            return 0