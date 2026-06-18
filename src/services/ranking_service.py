from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from models.distributor import Distributor
from models.campaign import Campaign
from models.donor import Donor
from models.donation import Donation
import logging

logger = logging.getLogger(__name__)


class RankingService:
    def __init__(self, db: Session):
        self.db = db

    def get_distributor_rankings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Rank distributors by successful_campaign_count DESC,
        then by total raised (sum of current_amount) DESC as tiebreaker.
        """
        results = (
            self.db.query(
                Distributor.address,
                Distributor.first_name,
                Distributor.last_name,
                Distributor.profile_pic,
                func.coalesce(
                    func.sum(case((Campaign.status == 1, 1), else_=0)), 0
                ).label("successful_campaign_count"),
                func.coalesce(func.sum(Campaign.current_amount), 0).label("total_raised"),
            )
            .outerjoin(Campaign, Campaign.distributor_address == Distributor.address)
            .filter(Distributor.is_banned == False)
            .group_by(
                Distributor.address,
                Distributor.first_name,
                Distributor.last_name,
                Distributor.profile_pic,
            )
            .order_by(
                desc("successful_campaign_count"),
                desc("total_raised"),
            )
            .limit(limit)
            .all()
        )

        rankings = []
        for rank, row in enumerate(results, start=1):
            name = f"{row.first_name or ''} {row.last_name or ''}".strip() or "Anonymous"
            rankings.append({
                "rank": rank,
                "address": row.address,
                "name": name,
                "successful_campaign_count": row.successful_campaign_count,
                "total_raised": str(int(row.total_raised)),
                "profile_pic": row.profile_pic,
            })

        return rankings

    def get_donor_rankings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Rank donors by total donated DESC,
        then by number of distinct campaigns supported DESC as tiebreaker.
        """
        results = (
            self.db.query(
                Donor.address,
                Donor.first_name,
                Donor.last_name,
                Donor.profile_pic,
                func.coalesce(func.sum(Donation.amount), 0).label("total_donated"),
                func.count(func.distinct(Donation.campaign_id)).label("campaigns_supported"),
            )
            .outerjoin(Donation, Donation.donor_address == Donor.address)
            .group_by(
                Donor.address,
                Donor.first_name,
                Donor.last_name,
                Donor.profile_pic,
            )
            .order_by(
                desc("total_donated"),
                desc("campaigns_supported"),
            )
            .limit(limit)
            .all()
        )

        rankings = []
        for rank, row in enumerate(results, start=1):
            name = f"{row.first_name or ''} {row.last_name or ''}".strip() or "Anonymous"
            rankings.append({
                "rank": rank,
                "address": row.address,
                "name": name,
                "total_donated": str(int(row.total_donated)),
                "campaigns_supported": row.campaigns_supported,
                "profile_pic": row.profile_pic,
            })

        return rankings
