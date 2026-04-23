from typing import Optional, List
from sqlalchemy.orm import Session
from models.distributor import Distributor
from repositories.base import BaseRepository


class DistributorRepository(BaseRepository[Distributor]):
    def __init__(self, db_session: Session):
        super().__init__(Distributor, db_session)

    # ------------------------------------------------------------------ #
    #  Read
    # ------------------------------------------------------------------ #

    def get_by_address(self, address: str) -> Optional[Distributor]:
        return self.get(address)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Distributor]:
        return self.get_all(skip=skip, limit=limit)

    def get_banned_distributors(self, skip: int = 0, limit: int = 100) -> List[Distributor]:
        return self.get_multi_by(skip=skip, limit=limit, is_banned=True)

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
    ) -> Distributor:
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

    def update_successful_campaigns(self, address: str, increment: int = 1) -> Optional[Distributor]:
        distributor = self.get(address)
        if distributor:
            new_count = distributor.successful_campaign_count + increment
            return self.update(address, successful_campaign_count=new_count)
        return None

    def set_banned(self, address: str, banned: bool = True) -> Optional[Distributor]:
        return self.update(address, is_banned=banned)

    def set_security_deposit(self, address: str, has_deposit: bool) -> Optional[Distributor]:
        return self.update(address, has_security_deposit=has_deposit)

    def set_active_campaign(self, address: str, campaign_id: Optional[int]) -> Optional[Distributor]:
        return self.update(address, active_campaign_id=campaign_id)