from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base




class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tx_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    proof_id: Mapped[int] = mapped_column(Integer, ForeignKey("proofs.id"))
    voter_address: Mapped[str] = mapped_column(String, ForeignKey("users.address"))
    vote: Mapped[bool] = mapped_column(Boolean)  # True = approve, False = reject
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    campaign = relationship("Campaign", back_populates="votes")
    proof = relationship("Proof", back_populates="votes")
    voter_user = relationship("User", back_populates="votes")
