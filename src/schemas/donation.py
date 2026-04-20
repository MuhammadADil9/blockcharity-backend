from pydantic import BaseModel
from utils.wei_converter import from_units

class DonationResponse(BaseModel):
    id: int
    campaign_id: int
    donor_address: str
    amount_raw: int  # On-chain value (e.g., 2500)
    amount_usdt: float  # Human readable (e.g., 25.0)
    timestamp: datetime

    @classmethod
    def from_orm_with_conversion(cls, donation):
        return cls(
            id=donation.id,
            campaign_id=donation.campaign_id,
            donor_address=donation.donor_address,
            amount_raw=donation.amount,
            amount_usdt=from_units(donation.amount),
            timestamp=donation.timestamp
        )