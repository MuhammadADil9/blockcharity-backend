from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.donor import Donor
from models.distributor import Distributor
from schemas.user import UserRegisterRequest
from config.database import get_db

router = APIRouter(tags=["Users"])


@router.get("/check-user")
def check_user(address: str = Query(..., description="Wallet address to look up"), db: Session = Depends(get_db)):
    """
    Check if a user with the given wallet address exists.
    Returns user fields + role ('donor' or 'distributor').
    """
    # Check distributors table first
    distributor = db.query(Distributor).filter(Distributor.address == address).first()
    if distributor:
        return {
            "exists": True,
            "role": "distributor",
            "address": distributor.address,
            "firstName": distributor.first_name,
            "lastName": distributor.last_name,
            "email": distributor.email,
            "phone": distributor.phone,
            "location": distributor.location,
            "profilePic": distributor.profile_pic,
        }

    # Check donors table
    donor = db.query(Donor).filter(Donor.address == address).first()
    if donor:
        return {
            "exists": True,
            "role": "donor",
            "address": donor.address,
            "firstName": donor.first_name,
            "lastName": donor.last_name,
            "email": donor.email,
            "phone": donor.phone,
            "location": donor.location,
            "profilePic": donor.profile_pic,
        }

    # User not found in either table
    return {"exists": False}


@router.post("/registeruser")
def register_user(user_in: UserRegisterRequest, db: Session = Depends(get_db)):
    # Wallet address uniqueness
    if db.query(Donor).filter(Donor.address == user_in.walletAddress).first() or \
       db.query(Distributor).filter(Distributor.address == user_in.walletAddress).first():
        raise HTTPException(status_code=400, detail="Wallet address already registered")

    # Email uniqueness across both tables
    if db.query(Donor).filter(Donor.email == user_in.email).first() or \
       db.query(Distributor).filter(Distributor.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Phone uniqueness across both tables
    if db.query(Donor).filter(Donor.phone == user_in.phone).first() or \
       db.query(Distributor).filter(Distributor.phone == user_in.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    if user_in.role == "distributor":
        new_user = Distributor(
            address=user_in.walletAddress,
            first_name=user_in.firstName,
            last_name=user_in.lastName,
            email=user_in.email,
            phone=user_in.phone,
            location=user_in.country,
        )
    else:
        new_user = Donor(
            address=user_in.walletAddress,
            first_name=user_in.firstName,
            last_name=user_in.lastName,
            email=user_in.email,
            phone=user_in.phone,
            location=user_in.country,
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "address": new_user.address,
        "firstName": new_user.first_name,
        "lastName": new_user.last_name,
        "email": new_user.email,
        "phone": new_user.phone,
        "location": new_user.location,
        "role": user_in.role,
    }