from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CampaignResponse(BaseModel):
    id: int
    distributor_address: str
    title: Optional[str] = None
    description: Optional[str] = None
    milestone_amount: int
    current_amount: int
    status: int
    is_active: int
    donor_count: int
    total_raised: int
    avg_donation: int
    created_at: datetime

    class Config:
        from_attributes = True