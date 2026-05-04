from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.campaign import Campaign
from models.donation import Donation
from models.vote import Vote
from models.donor import Donor
from models.distributor import Distributor
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_distributor_analytics(self, address: str) -> Dict[str, Any]:
        """Aggregate analytics scoped to a single distributor's campaigns."""

        # Verify distributor exists
        distributor = self.db.query(Distributor).filter(Distributor.address == address).first()
        if not distributor:
            return None

        campaigns = (
            self.db.query(Campaign)
            .filter(Campaign.distributor_address == address)
            .all()
        )

        total_campaigns = len(campaigns)
        active_campaigns = sum(1 for c in campaigns if c.status == 0)
        completed_campaigns = sum(1 for c in campaigns if c.status == 1)

        total_raised = sum(int(c.current_amount) for c in campaigns)

        # Count distinct donors across all distributor's campaigns
        total_donors = (
            self.db.query(func.count(func.distinct(Donation.donor_address)))
            .join(Campaign, Campaign.id == Donation.campaign_id)
            .filter(Campaign.distributor_address == address)
            .scalar()
        ) or 0

        # Campaign success rate
        campaign_success_rate = 0.0
        if total_campaigns > 0:
            campaign_success_rate = round((completed_campaigns / total_campaigns) * 100, 1)

        # Vote approval rate across all campaigns
        total_positive = sum(c.positive_votes for c in campaigns)
        total_negative = sum(c.negative_votes for c in campaigns)
        total_votes = total_positive + total_negative
        vote_approval_rate = 0.0
        if total_votes > 0:
            vote_approval_rate = round((total_positive / total_votes) * 100, 1)

        # Funding progress of active campaign
        funding_progress = 0.0
        active_campaign = next((c for c in campaigns if c.status == 0), None)
        if active_campaign and int(active_campaign.milestone_amount) > 0:
            funding_progress = round(
                (int(active_campaign.current_amount) / int(active_campaign.milestone_amount)) * 100,
                1,
            )

        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "completed_campaigns": completed_campaigns,
            "total_raised": str(total_raised),
            "total_donors": total_donors,
            "campaign_success_rate": campaign_success_rate,
            "vote_approval_rate": vote_approval_rate,
            "funding_progress": funding_progress,
        }

    def get_donor_analytics(self, address: str) -> Dict[str, Any]:
        """Aggregate analytics scoped to a single donor."""

        # Verify donor exists
        donor = self.db.query(Donor).filter(Donor.address == address).first()
        if not donor:
            return None

        # Total donated (from donor model — already tracked)
        total_donated = int(donor.total_donated_wei)

        # Campaigns supported
        campaigns_supported = (
            self.db.query(func.count(func.distinct(Donation.campaign_id)))
            .filter(Donation.donor_address == address)
            .scalar()
        ) or 0

        # Total votes cast
        total_votes_cast = (
            self.db.query(func.count(Vote.id))
            .filter(Vote.voter_address == address)
            .scalar()
        ) or 0

        # Average donation
        avg_donation = 0
        if campaigns_supported > 0:
            avg_donation = total_donated // campaigns_supported

        return {
            "total_donated": str(total_donated),
            "campaigns_supported": campaigns_supported,
            "total_votes_cast": total_votes_cast,
            "avg_donation": str(avg_donation),
        }
