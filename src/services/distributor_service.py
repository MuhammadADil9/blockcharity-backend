from typing import Optional
from sqlalchemy.orm import Session
from repositories.distributor_repo import DistributorRepository
import logging

logger = logging.getLogger(__name__)

class DistributorService:
    def __init__(self, db: Session):
        self.db = db
        self.distributor_repo = DistributorRepository(db)

    def create_or_update_distributor(
        self,
        address: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        profile_pic: Optional[str] = None,
    ) -> None:
        """Ensure distributor exists in DB (called from events or API)."""
        self.distributor_repo.create_or_update(
            address=address,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            profile_pic=profile_pic,
        )
        logger.info(f"Distributor {address} synced")

    def update_security_deposit(self, address: str, has_deposit: bool) -> None:
        """Update distributor's security deposit status (called from DepositMade/SecurityWithdrawn events)."""
        self.distributor_repo.set_security_deposit(address, has_deposit)
        logger.info(f"Distributor {address} security deposit set to {has_deposit}")

    def update_active_campaign(self, address: str, campaign_id: Optional[int]) -> None:
        """Set which campaign the distributor is currently running (called on create/cancel/complete)."""
        self.distributor_repo.set_active_campaign(address, campaign_id)

    def increment_successful_campaigns(self, address: str) -> None:
        """Called when a campaign completes successfully."""
        self.distributor_repo.update_successful_campaigns(address, increment=1)
        logger.info(f"Distributor {address} successful campaign count increased")

    def ban_distributor(self, address: str) -> None:
        """Called when admin force-cancels a campaign due to fraud."""
        self.distributor_repo.set_banned(address, banned=True)
        # Also remove security deposit status (deposit is consumed for refund)
        self.distributor_repo.set_security_deposit(address, False)
        logger.warning(f"Distributor {address} has been banned")

    def get_distributor(self, address: str):
        return self.distributor_repo.get_by_address(address)

    def get_banned_distributors(self, skip: int = 0, limit: int = 100):
        return self.distributor_repo.get_banned_distributors(skip, limit)