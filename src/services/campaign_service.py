import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.campaign_repo import CampaignRepository
from repositories.donation_repo import DonationRepository
from repositories.user_repo import UserRepository
from models.campaign import Campaign
from schemas.campaign import CampaignResponse, CampaignStats

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, db: Session):
        self.campaign_repo = CampaignRepository(db)
        self.donation_repo = DonationRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db

    def sync_campaign_from_event(self, event_args: dict, tx_hash: str) -> Optional[Campaign]:
        """
        Called by CampaignCreated event handler.
        Saves or updates campaign from blockchain event.
        """
        try:
            campaign_id = event_args['campaignId']
            distributor = event_args['distributor']
            milestone = event_args['milestone']

            # Ensure distributor exists in users table
            if not self.user_repo.get_by_address(distributor):
                self.user_repo.create(address=distributor)

            # Upsert campaign
            campaign = self.campaign_repo.upsert(
                unique_fields={'id': campaign_id},
                id=campaign_id,
                distributor_address=distributor,
                milestone_amount=milestone,
                current_amount=0,
                is_active=1,
                status=0,  # 0 = pending (will become active after event, but event means active)
                tx_hash=tx_hash
            )
            logger.info(f"Synced campaign {campaign_id} from event")
            return campaign
        except Exception as e:
            logger.error(f"Failed to sync campaign from event: {e}")
            self.db.rollback()
            return None

    def update_campaign_status(self, campaign_id: int, status: int, **extra) -> Optional[Campaign]:
        """
        Update campaign status (0=pending,1=active,2=completed,3=cancelled)
        Also can update activity_status, current_amount, etc.
        """
        try:
            campaign = self.campaign_repo.update(campaign_id, status=status, **extra)
            if campaign:
                logger.info(f"Campaign {campaign_id} status updated to {status}")
            return campaign
        except Exception as e:
            logger.error(f"Failed to update campaign {campaign_id}: {e}")
            self.db.rollback()
            return None

    def get_all_campaigns(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None,
        distributor: Optional[str] = None
    ) -> List[CampaignResponse]:
        """Fetch campaigns with optional filters, compute aggregations."""
        try:
            if distributor:
                campaigns = self.campaign_repo.get_multi_by(
                    distributor_address=distributor,
                    skip=skip,
                    limit=limit
                )
            elif status is not None:
                campaigns = self.campaign_repo.get_multi_by(
                    status=status,
                    skip=skip,
                    limit=limit
                )
            else:
                campaigns = self.campaign_repo.get_all(skip=skip, limit=limit)

            # Convert to response schema with computed stats
            result = []
            for c in campaigns:
                stats = self.get_campaign_stats(c.id)
                result.append(CampaignResponse(
                    id=c.id,
                    distributor_address=c.distributor_address,
                    title=c.title,
                    description=c.description,
                    milestone_amount=c.milestone_amount,
                    current_amount=c.current_amount,
                    status=c.status,
                    is_active=c.is_active,
                    donor_count=stats['donor_count'],
                    total_raised=stats['total_raised'],
                    avg_donation=stats['avg_donation'],
                    created_at=c.created_at
                ))
            return result
        except Exception as e:
            logger.error(f"Failed to get campaigns: {e}")
            return []

    def get_campaign_details(self, campaign_id: int) -> Optional[CampaignResponse]:
        """Get single campaign with full details and aggregations."""
        try:
            campaign = self.campaign_repo.get_by(id=campaign_id)
            if not campaign:
                return None
            stats = self.get_campaign_stats(campaign_id)
            return CampaignResponse(
                id=campaign.id,
                distributor_address=campaign.distributor_address,
                title=campaign.title,
                description=campaign.description,
                milestone_amount=campaign.milestone_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                is_active=campaign.is_active,
                donor_count=stats['donor_count'],
                total_raised=stats['total_raised'],
                avg_donation=stats['avg_donation'],
                created_at=campaign.created_at
            )
        except Exception as e:
            logger.error(f"Failed to get campaign details {campaign_id}: {e}")
            return None

    def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """
        Compute aggregations: total raised (from donations table),
        donor count, average donation.
        """
        try:
            donations = self.donation_repo.get_by_campaign(campaign_id)
            total_raised = sum(int(d.amount) for d in donations) if donations else 0
            donor_count = len(set(d.donor_address for d in donations))
            avg_donation = total_raised // donor_count if donor_count > 0 else 0
            return {
                'total_raised': total_raised,
                'donor_count': donor_count,
                'avg_donation': avg_donation
            }
        except Exception as e:
            logger.error(f"Failed to compute stats for campaign {campaign_id}: {e}")
            return {'total_raised': 0, 'donor_count': 0, 'avg_donation': 0}