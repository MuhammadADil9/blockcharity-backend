from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..schemas.schemas import CATEGORY_LABELS, CampaignCategory
from ..config.database import get_db

router = APIRouter(tags=["Campaigns"])

@router.post("/{address}/create/", response_model=schemas.CampaignResponse)
def create_campaign(address: str, campaign_data: schemas.CampaignCreateRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="Distributor not found")

    category_label = CATEGORY_LABELS.get(CampaignCategory(campaign_data.category), "Unknown")

    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_data.id).first()
    if db_campaign:
        db_campaign.title = campaign_data.title
        db_campaign.description = campaign_data.description
        db_campaign.location = campaign_data.location
        db_campaign.end_date = campaign_data.endDate
        db_campaign.milestone_amount = campaign_data.milestone
        db_campaign.category_name = category_label
    else:
        db_campaign = models.Campaign(
            id=campaign_data.id,
            distributor_address=address,
            title=campaign_data.title,
            description=campaign_data.description,
            location=campaign_data.location,
            end_date=campaign_data.endDate,
            milestone_amount=campaign_data.milestone,
            category_name=category_label,
            current_amount="0",
            status=0,
            is_active=1,
            image_url=""
        )
        db.add(db_campaign)

    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/{address}/list/", response_model=List[schemas.CampaignResponse])
def get_distributor_campaigns(address: str, db: Session = Depends(get_db)):
    return db.query(models.Campaign).filter(models.Campaign.distributor_address == address).all()