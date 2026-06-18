from pydantic import BaseModel
from typing import List, Optional


class DistributorRankingItem(BaseModel):
    rank: int
    address: str
    name: str
    successful_campaign_count: int
    total_raised: str  # Wei as string to avoid JS precision loss
    profile_pic: Optional[str] = None

    class Config:
        from_attributes = True


class DonorRankingItem(BaseModel):
    rank: int
    address: str
    name: str
    total_donated: str  # Wei as string
    campaigns_supported: int
    profile_pic: Optional[str] = None

    class Config:
        from_attributes = True


class DistributorRankingsResponse(BaseModel):
    rankings: List[DistributorRankingItem]


class DonorRankingsResponse(BaseModel):
    rankings: List[DonorRankingItem]
