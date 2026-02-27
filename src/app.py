from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Import your local modules
from .config import database
from .models import models
from .schemas import schemas
from .config.database import get_db

# Initialize Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Charity Dapp")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SYSTEM ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "active", "message": "Charity Dapp Backend is Running"}


# --- USER & AUTH ENDPOINTS ---

@app.get("/users/{address}", response_model=schemas.UserResponse)
def get_user(address: str, db: Session = Depends(get_db)):
    """
    Fetch a user by wallet address. 
    """
    print(f"Triggered /users/{address} endpoint")

    user = db.query(models.User).filter(models.User.address == address).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/registeruser", response_model=schemas.UserResponse)
def register_user(user_in: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    existing_user = db.query(models.User).filter(models.User.address == user_in.walletAddress).first()
    if existing_user:
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


# --- PROFILE ENDPOINTS ---

@app.get("/{address}/profile", response_model=schemas.UserContactInfo)
def get_user_contact_info(address: str, db: Session = Depends(get_db)):
    """
    Returns specific contact details.
    """
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


# --- CAMPAIGN ENDPOINTS ---

@app.post("/{address}/create/", response_model=schemas.CampaignResponse)
def create_campaign(
    address: str, 
    campaign_data: schemas.CampaignCreateRequest, 
    db: Session = Depends(get_db)
):
    # 1. Verify User Exists
    user = db.query(models.User).filter(models.User.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="Distributor not found")

    # 2. Check for existing campaign
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_data.id).first()

    if db_campaign:
        # Update existing record
        db_campaign.title = campaign_data.title
        db_campaign.description = campaign_data.description
        db_campaign.location = campaign_data.location
        db_campaign.end_date = campaign_data.endDate 
        db_campaign.milestone_amount = campaign_data.milestone
        
        if db_campaign.category_name is None:
            db_campaign.category_name = "Education"
    else:
        # Create new record
        db_campaign = models.Campaign(
            id=campaign_data.id,
            distributor_address=address,
            title=campaign_data.title,
            description=campaign_data.description,
            location=campaign_data.location,
            end_date=campaign_data.endDate,
            milestone_amount=campaign_data.milestone,
            current_amount="0",
            status=0,
            is_active=1,
            category_name="Education",
            image_url=""
        )
        db.add(db_campaign)

    db.commit()
    db.refresh(db_campaign)
    return db_campaign


@app.get("/{address}/list/", response_model=List[schemas.CampaignResponse])
def get_distributor_campaigns(address: str, db: Session = Depends(get_db)):
    """
    Fetch all campaigns for a specific distributor.
    """
    return db.query(models.Campaign).filter(models.Campaign.distributor_address == address).all()