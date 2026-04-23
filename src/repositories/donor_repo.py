from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.donor import Donor
from models.donation import Donation
from repositories.base import BaseRepository


class DonorRepository(BaseRepository[Donor]):
    def __init__(self, db_session: Session):
        super().__init__(Donor, db_session)

    # ------------------------------------------------------------------ #
    #  Read
    # ------------------------------------------------------------------ #

    def get_by_address(self, address: str) -> Optional[Donor]:
        return self.get(address)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Donor]:
        return self.get_all(skip=skip, limit=limit)

    def get_top_donors(self, limit: int = 10) -> List[Donor]:
        return (
            self.db.query(Donor)
            .order_by(Donor.total_donated_wei.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------ #
    #  Write
    # ------------------------------------------------------------------ #

    def create_or_update(
        self,
        address: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        profile_pic: Optional[str] = None,
    ) -> Donor:
        existing = self.get(address)
        if existing:
            return self.update(
                address,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                location=location,
                profile_pic=profile_pic,
            )
        return self.create(
            address=address,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            profile_pic=profile_pic,
        )

    def increment_total_donated(self, address: str, amount_wei: int) -> Optional[Donor]:
        donor = self.get(address)
        if donor:
            new_total = donor.total_donated_wei + amount_wei
            return self.update(address, total_donated_wei=new_total)
        return None