from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.campaign import Campaign
from repositories.base import BaseRepository



class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db_session: Session):
        super().__init__(Campaign, db_session)

    # ------------------------------------------------------------------ #
    #  Read
    # ------------------------------------------------------------------ #

    def get_by_id(self, campaign_id: int) -> Optional[Campaign]:
        return self.get(campaign_id)

    def get_by_distributor(
        self,
        distributor_address: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Campaign]:
        return self.get_multi_by(
            skip=skip,
            limit=limit,
            distributor_address=distributor_address,
        )

    def get_by_status(self, status: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """status: 0=active, 1=completed, 2=canceled"""
        return self.get_multi_by(skip=skip, limit=limit, status=status)

    def get_by_activity_status(self, activity_status: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """activity_status: 0=inFunding,1=milestoneAchieved,2=proofToBeUploaded,3=voting,4=result"""
        return self.get_multi_by(skip=skip, limit=limit, activity_status=activity_status)

    # ------------------------------------------------------------------ #
    #  Write
    # ------------------------------------------------------------------ #

    def update_status(self, campaign_id: int, status: int) -> Optional[Campaign]:
        return self.update(campaign_id, status=status)

    def update_activity_status(self, campaign_id: int, activity_status: int) -> Optional[Campaign]:
        return self.update(campaign_id, activity_status=activity_status)

    def update_current_amount(
        self, campaign_id: int, amount_to_add: int
    ) -> Optional[Campaign]:
        """Atomic increment (safe for concurrent donations)"""
        self.db.query(Campaign).filter(Campaign.id == campaign_id).update(
            {Campaign.current_amount: Campaign.current_amount + amount_to_add},
            synchronize_session=False,
        )
        self.db.commit()
        return self.get(campaign_id)

    def update_vote_counts(
        self, campaign_id: int, positive_votes: int, negative_votes: int, total_voters: int
    ) -> Optional[Campaign]:
        return self.update(
            campaign_id,
            positive_votes=positive_votes,
            negative_votes=negative_votes,
            total_voters=total_voters,
        )

    def create_from_event(
        self,
        campaign_id: int,
        distributor_address: str,
        milestone_amount: int,
        category_name: str = None,
        tx_hash: str = None,
    ) -> Campaign:
        """Called when CampaignCreated event is received"""
        return self.create(
            id=campaign_id,
            distributor_address=distributor_address,
            milestone_amount=milestone_amount,
            category_name=category_name,
            status=0,               # active
            activity_status=0,      # inFunding
            current_amount=0,
            positive_votes=0,
            negative_votes=0,
            total_voters=0,
        )




    