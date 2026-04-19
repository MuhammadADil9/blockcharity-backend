from models.user import User
from repositories.base import BaseRepository
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc


class UserRepository(BaseRepository[User]):

    def __init__(self, db_session: Session):
        super().__init__(User, db_session)

    # ------------------------------------------------------------------ #
    #  Read                                                                #
    # ------------------------------------------------------------------ #

    def get_by_address(self, address: str) -> Optional[User]:
        """Fetch a single user by their wallet address (primary key)."""
        return self.get_by(address=address)

    def get_all_distributors(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """Return all users with is_distributor=True."""
        return self.get_multi_by(skip=skip, limit=limit, is_distributor=True)

    # ------------------------------------------------------------------ #
    #  Write                                                               #
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
    ) -> User:
        """
        Upsert a user profile by wallet address.
        Creates the record on first login, updates it on subsequent calls.
        Only non-None values are written so partial updates don't wipe fields.
        """
        return self.upsert(
            unique_fields={"address": address},
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            profile_pic=profile_pic,
        )

    def update_profile(
        self,
        address: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        location: Optional[str] = None,
        profile_pic: Optional[str] = None,
    ) -> Optional[User]:
        """
        Update editable profile fields for an existing user.
        Only non-None fields are overwritten — caller can safely pass
        only the fields they want to change.
        """
        instance = self.get_by_address(address)
        if not instance:
            return None

        fields = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "location": location,
            "profile_pic": profile_pic,
        }

        for key, value in fields.items():
            if value is not None:
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def set_distributor_status(
        self, address: str, is_distributor: bool
    ) -> Optional[User]:
        """Toggle the is_distributor flag for a user."""
        instance = self.get_by_address(address)
        if not instance:
            return None

        instance.is_distributor = is_distributor
        self.db.commit()
        self.db.refresh(instance)
        return instance