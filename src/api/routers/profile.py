from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from models.donor import Donor
from models.distributor import Distributor
from pydantic import BaseModel
from schemas.user import UserContactInfo
from config.database import get_db
import base64

_ALLOWED_PREFIXES = ("data:image/jpeg;base64,", "data:image/png;base64,")
_MAX_DECODED_BYTES = 10 * 1024 * 1024  # 10MB

def _validate_profile_pic(value: str) -> str:
    if not any(value.startswith(p) for p in _ALLOWED_PREFIXES):
        raise HTTPException(status_code=400, detail="profile_pic must be a data URI with image/jpeg or image/png")
    b64_data = value.split(",", 1)[1]
    try:
        decoded = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="profile_pic contains invalid Base64 data")
    if len(decoded) > _MAX_DECODED_BYTES:
        raise HTTPException(status_code=400, detail="Image exceeds 10MB limit")
    return value

class UserSettingsUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profilePic: Optional[str] = None

router = APIRouter(prefix="/api", tags=["Profile"])

@router.get("/{address}/profile", response_model=UserContactInfo)
def get_user_contact_info(address: str, db: Session = Depends(get_db)):
    # Check distributors first, then donors
    user = db.query(Distributor).filter(Distributor.address == address).first()
    if not user:
        user = db.query(Donor).filter(Donor.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserContactInfo(
        address=user.address,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        location=user.location,
        profile_pic=user.profile_pic
    )

@router.patch("/settings/{address}", response_model=UserContactInfo)
def update_user_settings(address: str, settings: UserSettingsUpdate, db: Session = Depends(get_db)):
    # Check distributors first
    user = db.query(Distributor).filter(Distributor.address == address).first()
    if not user:
        # Check donors
        user = db.query(Donor).filter(Donor.address == address).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update only provided fields
    if settings.firstName is not None:
        user.first_name = settings.firstName
    if settings.lastName is not None:
        user.last_name = settings.lastName
    if settings.email is not None:
        user.email = settings.email
    if settings.phone is not None:
        user.phone = settings.phone
    if settings.location is not None:
        user.location = settings.location
    if settings.profilePic is not None:
        user.profile_pic = _validate_profile_pic(settings.profilePic)
        
    db.commit()
    db.refresh(user)
    
    return UserContactInfo(
        address=user.address,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        location=user.location,
        profile_pic=user.profile_pic
    )