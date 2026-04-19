from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base




class LotteryWinner(Base):
    __tablename__ = "lottery_winners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    distributor_address: Mapped[str] = mapped_column(String, ForeignKey("users.address"))
    campaign_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("campaigns.id"), nullable=True)
    prize_amount: Mapped[int] = mapped_column(Numeric(78, 0))  # Wei amount
    block_number: Mapped[int] = mapped_column(Integer)
    tx_hash: Mapped[str] = mapped_column(String, index=True)
    claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    distributor_user = relationship("User")
    campaign = relationship("Campaign")



#     Track every event from your smart contract

# Show campaign lists and details on frontend

# Display donation history per user

# Allow donors to vote on proofs and see vote counts

# Pick and display lottery winners

# Store off-chain user profiles