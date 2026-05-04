from pydantic import BaseModel


class DistributorAnalyticsResponse(BaseModel):
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    total_raised: str  # Wei as string
    total_donors: int
    campaign_success_rate: float  # Percentage 0-100
    vote_approval_rate: float  # Percentage 0-100
    funding_progress: float  # Percentage of active campaign, 0 if no active campaign


class DonorAnalyticsResponse(BaseModel):
    total_donated: str  # Wei as string
    campaigns_supported: int
    total_votes_cast: int
    avg_donation: str  # Wei as string
