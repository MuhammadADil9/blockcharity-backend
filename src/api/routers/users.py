from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..config.database import get_db

router = APIRouter(tags=["Users"])

@router.get("/users/{address}", response_model=schemas.UserResponse)
def get_user(address: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.address == address).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/registeruser", response_model=schemas.UserResponse)
def register_user(user_in: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.address == user_in.walletAddress).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered")

    new_user = models.User(
        address=user_in.walletAddress,
        first_name=user_in.firstName,
        last_name=user_in.lastName,
        email=user_in.email,
        phone=user_in.phone,
        location=user_in.country,
        is_distributor=(user_in.role == "distributor")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user