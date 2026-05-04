from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from config.database import get_db
from services.ranking_service import RankingService
from schemas.ranking import (
    DistributorRankingsResponse,
    DonorRankingsResponse,
)

router = APIRouter(prefix="/api/rankings", tags=["Rankings"])


@router.get("/distributors", response_model=DistributorRankingsResponse)
def get_distributor_rankings(
    limit: int = Query(default=50, ge=1, le=100, description="Max results to return"),
    db: Session = Depends(get_db),
):
    """Return distributors ranked by successful campaigns and total raised."""
    service = RankingService(db)
    rankings = service.get_distributor_rankings(limit=limit)
    return {"rankings": rankings}


@router.get("/donors", response_model=DonorRankingsResponse)
def get_donor_rankings(
    limit: int = Query(default=50, ge=1, le=100, description="Max results to return"),
    db: Session = Depends(get_db),
):
    """Return donors ranked by total donated and campaigns supported."""
    service = RankingService(db)
    rankings = service.get_donor_rankings(limit=limit)
    return {"rankings": rankings}
