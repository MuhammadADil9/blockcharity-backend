from models.proof import Proof
from repositories.base import BaseRepository
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

class ProofRepository(BaseRepository[Proof]):

    def __init__(self, db_session: Session):
        super().__init__(Proof, db_session)

    # ------------------------------------------------------------------ #
    #  Read
    # ------------------------------------------------------------------ #

    def get_by_campaign(
        self,
        campaign_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Proof]:
        """All proofs submitted for a campaign, oldest first."""
        return (
            self.db.query(Proof)
            .filter(Proof.campaign_id == campaign_id)
            .order_by(Proof.timestamp.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_campaign(self, campaign_id: int) -> Optional[Proof]:
        """Most recently uploaded proof for a campaign."""
        return (
            self.db.query(Proof)
            .filter(Proof.campaign_id == campaign_id)
            .order_by(Proof.timestamp.desc())
            .first()
        )

    # ------------------------------------------------------------------ #
    #  Write
    # ------------------------------------------------------------------ #

    def create_proof(
        self,
        campaign_id: int,
        ipfs_hash: str,
        uploaded_by: str,
    ) -> Proof:
        """Insert a new proof record from a ProofUploaded on-chain event."""
        return self.create(
            campaign_id=campaign_id,
            ipfs_hash=ipfs_hash,
            uploaded_by=uploaded_by,
        )