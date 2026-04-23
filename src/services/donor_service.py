from typing import Optional
from sqlalchemy.orm import Session
from repositories.donor_repo import DonorRepository
import logging

logger = logging.getLogger(__name__)

class DonorService:
    def __init__(self, db: Session):
        self.db = db
        self.donor_repo = DonorRepository(db)

    def create_or_update_donor(
        self,
        address: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        profile_pic: Optional[str] = None,
    ) -> None:
        """Ensure donor exists in DB (called from events or API)."""
        self.donor_repo.create_or_update(
            address=address,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            profile_pic=profile_pic,
        )
        logger.info(f"Donor {address} synced")

    def increment_total_donated(self, address: str, amount_wei: int) -> None:
        """Add donation amount to donor's total donated (called from donation handler)."""
        donor = self.donor_repo.increment_total_donated(address, amount_wei)
        if donor:
            logger.info(f"Donor {address} total donated increased by {amount_wei}")
        else:
            # Donor not found - create them first
            self.create_or_update_donor(address)
            self.donor_repo.increment_total_donated(address, amount_wei)

    def get_donor(self, address: str):
        return self.donor_repo.get_by_address(address)

    def get_top_donors(self, limit: int = 10):
        return self.donor_repo.get_top_donors(limit)