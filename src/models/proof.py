from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base







class Proof(Base):
    __tablename__ = "proofs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    ipfs_hash: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String, ForeignKey("users.address"))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_count_yes: Mapped[int] = mapped_column(Integer, default=0)
    verification_count_no: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    campaign = relationship("Campaign", back_populates="proofs")
    votes = relationship("Vote", back_populates="proof")

