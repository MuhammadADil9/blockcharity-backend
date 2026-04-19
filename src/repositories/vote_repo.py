from models.vote import Vote
from repositories.base import BaseRepository
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc


# repositories/vote_repo.py

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.vote import Vote
from repositories.base import BaseRepository


class VoteRepository(BaseRepository[Vote]):

    def __init__(self, db_session: Session):
        super().__init__(Vote, db_session)

    # ------------------------------------------------------------------ #
    #  Read                                                                #
    # ------------------------------------------------------------------ #

    def get_by_tx_hash(self, tx_hash: str) -> Optional[Vote]:
        """Fetch a single vote by its on-chain transaction hash."""
        return self.get_by(tx_hash=tx_hash)

    def get_by_campaign_and_voter(
        self, campaign_id: int, voter_address: str
    ) -> Optional[Vote]:
        """Fetch a vote cast by a specific voter on a specific campaign."""
        return (
            self.db.query(Vote)
            .filter(
                Vote.campaign_id == campaign_id,
                Vote.voter_address == voter_address,
            )
            .first()
        )

    def get_campaign_vote_stats(self, campaign_id: int) -> dict:
        """
        Return total approve and reject vote counts for a campaign.
        Result: { "yes": int, "no": int, "total": int }
        """
        result = (
            self.db.query(
                func.count(Vote.id).label("total"),
                func.sum(
                    func.cast(Vote.vote, Integer)
                ).label("yes_count"),
            )
            .filter(Vote.campaign_id == campaign_id)
            .one()
        )

        yes  = int(result.yes_count or 0)
        total = int(result.total or 0)
        no   = total - yes

        return {"yes": yes, "no": no, "total": total}

    def has_voted(self, campaign_id: int, voter_address: str) -> bool:
        """Return True if the voter has already cast a vote on this campaign."""
        return self.get_by_campaign_and_voter(campaign_id, voter_address) is not None

    # ------------------------------------------------------------------ #
    #  Write                                                               #
    # ------------------------------------------------------------------ #

    def create_vote(
        self,
        tx_hash: str,
        campaign_id: int,
        proof_id: int,
        voter_address: str,
        vote: bool,
    ) -> Optional[Vote]:
        """
        Insert a new vote from a VoteCast on-chain event.
        Idempotent — returns existing record if tx_hash already exists.
        """
        existing = self.get_by_tx_hash(tx_hash)
        if existing:
            return existing

        return self.create(
            tx_hash=tx_hash,
            campaign_id=campaign_id,
            proof_id=proof_id,
            voter_address=voter_address,
            vote=vote,
        )