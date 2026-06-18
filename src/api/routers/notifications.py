from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from services.notification_service import NotificationService
from schemas.notification import NotificationResponse, MarkReadRequest

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/{address}", response_model=List[NotificationResponse])
def get_notifications(
    address: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    service = NotificationService(db)
    return service.get_for_user(address, skip=skip, limit=limit)


@router.get("/{address}/unread-count")
def get_unread_count(address: str, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return {"unread_count": service.count_unread(address)}


@router.put("/{address}/mark-read")
def mark_notifications_read(
    address: str,
    body: MarkReadRequest,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    ids = None if body.all else body.ids
    count = service.mark_read(address, ids=ids)
    db.commit()
    return {"marked_read": count}
