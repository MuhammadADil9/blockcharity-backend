from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tx_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    voter_address: Mapped[str] = mapped_column(String, ForeignKey("donors.address"))
    vote: Mapped[bool] = mapped_column(Boolean)  # True = positive/approve, False = negative/reject
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    campaign = relationship("Campaign", back_populates="votes")
    voter_user = relationship("Donor", back_populates="votes")