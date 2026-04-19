from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base





class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tx_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    donor_address: Mapped[str] = mapped_column(String, ForeignKey("users.address"))
    amount: Mapped[int] = mapped_column(Numeric(78, 0))  # Wei amount
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    campaign = relationship("Campaign", back_populates="donations")
    donor_user = relationship("User", back_populates="donations")