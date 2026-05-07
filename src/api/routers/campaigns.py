from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from models.campaign import Campaign
from models.distributor import Distributor
from models.donation import Donation
from models.donor import Donor
from schemas.user import CampaignCreateRequest, CampaignResponse, DonorDonationResponse
from config.database import get_db
from services.ipfs_service import IPFSService

router = APIRouter(prefix="/api", tags=["Campaigns"])

@router.post("/campaigns/{id}/upload-proof")
async def upload_proof(id: int, file: UploadFile = File(...)):
    """Uploads a proof file to IPFS and returns the CID."""
    try:
        max_size = 10 * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        ipfs_service = IPFSService()
        cid = ipfs_service.upload_file(contents, file.filename)

        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from models.vote import Vote

@router.get("/donor/{address}/donations", response_model=List[DonorDonationResponse])
def get_donor_donations(address: str, db: Session = Depends(get_db)):
    """Returns all campaigns the donor has contributed to, with their total amount donated per campaign."""
    donor = db.query(Donor).filter(Donor.address == address).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")

    rows = (
        db.query(
            Campaign,
            func.sum(Donation.amount).label("amount_donated"),
        )
        .join(Donation, Donation.campaign_id == Campaign.id)
        .filter(Donation.donor_address == address)
        .group_by(Campaign.id)
        .all()
    )

    result = []
    for campaign, amount_donated in rows:
        # Check if donor has voted for this campaign
        voted = db.query(Vote).filter(
            Vote.campaign_id == campaign.id,
            Vote.voter_address == address
        ).first() is not None

        result.append(DonorDonationResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            location=campaign.location,
            category_name=campaign.category_name,
            status=campaign.status,
            activity_status=campaign.activity_status,
            distributor_address=campaign.distributor_address,
            amount_donated=int(amount_donated),
            current_amount=int(campaign.current_amount),
            milestone_amount=int(campaign.milestone_amount),
            end_date=campaign.end_date,
            voted=voted
        ))
    return result

@router.get("/distributor/{address}/active-campaign", response_model=Optional[CampaignResponse])
def get_active_campaign(address: str, db: Session = Depends(get_db)):
    """Returns the currently active campaign for a distributor, or null."""
    campaign = db.query(Campaign).filter(
        Campaign.distributor_address == address,
        Campaign.status == 0
    ).first()
    return campaign

@router.get("/distributor/{address}/campaigns", response_model=List[CampaignResponse])
def get_distributor_campaigns_all(address: str, db: Session = Depends(get_db)):
    """Returns all campaigns created by a distributor (active, completed, and cancelled)."""
    distributor = db.query(Distributor).filter(Distributor.address == address).first()
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return db.query(Campaign).filter(Campaign.distributor_address == address).all()

@router.get("/campaigns", response_model=List[CampaignResponse])
def get_campaigns(filter: str = Query("all", description="all | active | finished"), db: Session = Depends(get_db)):
    """Returns campaigns based on the specified filter."""
    query = db.query(Campaign)

    if filter == "active":
        query = query.filter(Campaign.status == 0)
    elif filter == "finished":
        query = query.filter(Campaign.status.in_([1, 2]))

    return query.all()

@router.get("/campaigns/{id}", response_model=CampaignResponse)
def get_campaign_by_id(id: int, user_address: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Returns a single campaign by its on-chain ID, with optional user-specific info."""
    campaign = db.query(Campaign).filter(Campaign.id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {id} not found")
    
    # Total distinct donors for this campaign
    campaign.total_donors = db.query(func.count(func.distinct(Donation.donor_address))) \
        .filter(Donation.campaign_id == id).scalar() or 0

    # If user_address is provided, enrich with personal stats
    if user_address:
        campaign.is_donor = db.query(Donation).filter(
            Donation.campaign_id == id,
            Donation.donor_address == user_address
        ).first() is not None

        campaign.voted = db.query(Vote).filter(
            Vote.campaign_id == id,
            Vote.voter_address == user_address
        ).first() is not None

    return campaign

@router.post("/campaigns/{address}/create/", response_model=CampaignResponse)
def create_campaign(address: str, campaign_data: CampaignCreateRequest, db: Session = Depends(get_db)):
    user = db.query(Distributor).filter(Distributor.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail="Distributor not found")

    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_data.id).first()
    if db_campaign:
        db_campaign.title = campaign_data.title
        db_campaign.description = campaign_data.description
        db_campaign.location = campaign_data.location
        db_campaign.end_date = campaign_data.endDate
        db_campaign.milestone_amount = int(campaign_data.milestone)
        db_campaign.category_name = campaign_data.category
    else:
        db_campaign = Campaign(
            id=campaign_data.id,
            distributor_address=address,
            title=campaign_data.title,
            description=campaign_data.description,
            location=campaign_data.location,
            end_date=campaign_data.endDate,
            milestone_amount=int(campaign_data.milestone),
            category_name=campaign_data.category,
            current_amount=0,
            status=0,
            activity_status=0,
            positive_votes=0,
            negative_votes=0,
            total_voters=0,
            image_url=""
        )
        db.add(db_campaign)

    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/campaigns/{address}/list/", response_model=List[CampaignResponse])
def get_distributor_campaigns(address: str, db: Session = Depends(get_db)):
    return db.query(Campaign).filter(Campaign.distributor_address == address).all()
