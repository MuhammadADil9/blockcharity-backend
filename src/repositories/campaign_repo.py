# repositories/campaign_repo.py
from models.campaign import Campaign
from repositories.base import BaseRepository
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db_session: Session):
        super().__init__(Campaign, db_session)

    # ------------------------------------------------------------------ #
    #  Read                                                                #
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

    def get_active_campaigns(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Campaign]:
        return self.get_multi_by(skip=skip, limit=limit, is_active=1)

    # ------------------------------------------------------------------ #
    #  Write                                                               #
    # ------------------------------------------------------------------ #

    def update_status(self, campaign_id: int, status: int) -> Optional[Campaign]:
        return self.update(campaign_id, status=status)

    def update_current_amount(
        self, campaign_id: int, amount_to_add: int
    ) -> Optional[Campaign]:
        """Atomic SQL-level increment — safe under concurrent donations."""
        self.db.query(Campaign).filter(Campaign.id == campaign_id).update(
            {Campaign.current_amount: Campaign.current_amount + amount_to_add},
            synchronize_session=False,
        )
        self.db.commit()
        return self.get(campaign_id)

    def update_proof_hash(self, campaign_id: int, ipfs_hash: str) -> Optional[Campaign]:
        return self.update(campaign_id, ipfs_hash=ipfs_hash)

    def set_proof_verified(self, campaign_id: int, verified: bool = True) -> Optional[Campaign]:
        return self.update(campaign_id, proof_verified=verified)





    