from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: int
    user_address: str
    campaign_id: Optional[int] = None
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarkReadRequest(BaseModel):
    ids: Optional[List[int]] = None
    all: bool = False
