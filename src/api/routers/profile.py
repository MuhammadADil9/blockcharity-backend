from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.donor import Donor
from models.distributor import Distributor
from schemas.user import UserContactInfo
from config.database import get_db

router = APIRouter(tags=["Profile"])

@router.get("/{address}/profile", response_model=UserContactInfo)
def get_user_contact_info(address: str, db: Session = Depends(get_db)):
    # Check distributors first, then donors
    user = db.query(Distributor).filter(Distributor.address == address).first()
    if not user:
        user = db.query(Donor).filter(Donor.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserContactInfo(
        firstName=user.first_name,
        lastName=user.last_name,
        email=user.email,
        phone=user.phone,
        country=user.location
    )