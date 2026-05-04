from pydantic import BaseModel
from datetime import datetime

class DonationResponse(BaseModel):
    id: int
    campaign_id: int
    donor_address: str
    amount: int  # Raw integer value
    timestamp: datetime

    class Config:
        from_attributes = True