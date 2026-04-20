from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from models.vote import Vote
from repositories.base import BaseRepository


class VoteRepository(BaseRepository[Vote]):
    def __init__(self, db_session: Session):
        super().__init__(Vote, db_session)

    # ------------------------------------------------------------------ #
    #  Read
    # ------------------------------------------------------------------ #

    def get_by_tx_hash(self, tx_hash: str) -> Optional[Vote]:
        return self.get_by(tx_hash=tx_hash)

    def get_by_campaign_and_voter(
        self, campaign_id: int, voter_address: str
    ) -> Optional[Vote]:
        return (
            self.db.query(Vote)
            .filter(
                Vote.campaign_id == campaign_id,
                Vote.voter_address == voter_address,
            )
            .first()
        )

    def get_campaign_vote_stats(self, campaign_id: int) -> Dict[str, int]:
        result = (
            self.db.query(
                func.count(Vote.id).label("total"),
                func.sum(func.cast(Vote.vote, Integer)).label("yes_count"),
            )
            .filter(Vote.campaign_id == campaign_id)
            .one()
        )
        yes = int(result.yes_count or 0)
        total = int(result.total or 0)
        no = total - yes
        return {"yes": yes, "no": no, "total": total}

    def has_voted(self, campaign_id: int, voter_address: str) -> bool:
        return self.get_by_campaign_and_voter(campaign_id, voter_address) is not None

    # ------------------------------------------------------------------ #
    #  Write
    # ------------------------------------------------------------------ #

    def create_vote(
        self,
        tx_hash: str,
        campaign_id: int,
        voter_address: str,
        vote: bool,
    ) -> Optional[Vote]:
        existing = self.get_by_tx_hash(tx_hash)
        if existing:
            return existing
        return self.create(
            tx_hash=tx_hash,
            campaign_id=campaign_id,
            voter_address=voter_address,
            vote=vote,
        )