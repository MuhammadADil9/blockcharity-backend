from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from services.analytics_service import AnalyticsService
from schemas.analytics import DistributorAnalyticsResponse, DonorAnalyticsResponse, PlatformAnalyticsResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])



@router.get("/distributor/{address}", response_model=DistributorAnalyticsResponse)
def get_distributor_analytics(address: str, db: Session = Depends(get_db)):
    """Return aggregated analytics for a specific distributor."""
    service = AnalyticsService(db)
    result = service.get_distributor_analytics(address)
    if result is None:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return result


@router.get("/donor/{address}", response_model=DonorAnalyticsResponse)
def get_donor_analytics(address: str, db: Session = Depends(get_db)):
    """Return aggregated analytics for a specific donor."""
    service = AnalyticsService(db)
    result = service.get_donor_analytics(address)
    if result is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    return result



@router.get("/platform", response_model=PlatformAnalyticsResponse)
def get_platform_analytics(db: Session = Depends(get_db)):
    """Return aggregated analytics for the entire platform."""
    service = AnalyticsService(db)
    return service.get_platform_analytics()
