from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..config.database import get_db

router = APIRouter(tags=["Profile"])

@router.get("/{address}/profile", response_model=schemas.UserContactInfo)
def get_user_contact_info(address: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserContactInfo(
        firstName=user.first_name,
        lastName=user.last_name,
        email=user.email,
        phone=user.phone,
        country=user.location
    )