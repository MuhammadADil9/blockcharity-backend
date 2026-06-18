from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import case, desc
from models.notification import Notification, NotificationType
from models.donation import Donation
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_address: str,
        message: str,
        type: NotificationType,
        campaign_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            user_address=user_address,
            campaign_id=campaign_id,
            message=message,
            type=type,
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def broadcast_to_donors(
        self,
        campaign_id: int,
        message: str,
        type: NotificationType,
    ) -> int:
        addresses = (
            self.db.query(Donation.donor_address)
            .filter(Donation.campaign_id == campaign_id)
            .distinct()
            .all()
        )
        for (address,) in addresses:
            self.create(user_address=address, campaign_id=campaign_id, message=message, type=type)
        return len(addresses)

    def get_for_user(
        self,
        user_address: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_address == user_address)
            .order_by(
                case((Notification.is_read == False, 0), else_=1),
                desc(Notification.created_at),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_unread(self, user_address: str) -> int:
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_address == user_address,
                Notification.is_read == False,
            )
            .count()
        )

    def mark_read(self, user_address: str, ids: Optional[List[int]] = None) -> int:
        query = self.db.query(Notification).filter(
            Notification.user_address == user_address,
            Notification.is_read == False,
        )
        if ids is not None:
            query = query.filter(Notification.id.in_(ids))
        return query.update({"is_read": True}, synchronize_session=False)
