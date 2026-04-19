from models.donation import Donation
from repositories.base import BaseRepository
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc


class DonationRepository(BaseRepository[Donation]):

    def __init__(self, db_session: Session):
        super().__init__(Donation, db_session)

    # ------------------------------------------------------------------ #
    #  Read                                                                #
    # ------------------------------------------------------------------ #

    def get_by_tx_hash(self, tx_hash: str) -> Optional[Donation]:
        """Fetch a single donation by its on-chain transaction hash."""
        return self.get_by(tx_hash=tx_hash)

    def get_by_campaign(
        self,
        campaign_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Donation]:
        """All donations made to a specific campaign."""
        return self.get_multi_by(skip=skip, limit=limit, campaign_id=campaign_id)

    def get_by_donor(
        self,
        donor_address: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Donation]:
        """All donations made by a specific donor address."""
        return self.get_multi_by(skip=skip, limit=limit, donor_address=donor_address)

    def get_donor_total(self, campaign_id: int, donor_address: str) -> int:
        """
        Sum of all wei donated by a specific donor to a specific campaign.
        Returns 0 if no donations exist.
        """
        result = (
            self.db.query(func.sum(Donation.amount))
            .filter(
                Donation.campaign_id == campaign_id,
                Donation.donor_address == donor_address,
            )
            .scalar()
        )
        return int(result) if result is not None else 0

    def get_campaign_donors(self, campaign_id: int) -> List[str]:
        """
        List of unique donor addresses who donated to a campaign.
        Ordered by first donation time.
        """
        rows = (
            self.db.query(Donation.donor_address)
            .filter(Donation.campaign_id == campaign_id)
            .distinct()
            .order_by(Donation.timestamp.asc())
            .all()
        )
        return [row.donor_address for row in rows]

    # ------------------------------------------------------------------ #
    #  Write                                                               #
    # ------------------------------------------------------------------ #

    def create_or_ignore(
        self,
        tx_hash: str,
        campaign_id: int,
        donor_address: str,
        amount: int,
    ) -> Optional[Donation]:
        """
        Insert donation only if tx_hash doesn't already exist.
        Returns the existing or newly created record.
        Returns None if something unexpected prevents the operation.
        
        Safe to call multiple times for the same transaction (idempotent) —
        important for blockchain event replay / re-indexing scenarios.
        """
        existing = self.get_by_tx_hash(tx_hash)
        if existing:
            return existing

        return self.create(
            tx_hash=tx_hash,
            campaign_id=campaign_id,
            donor_address=donor_address,
            amount=amount,
        )

        