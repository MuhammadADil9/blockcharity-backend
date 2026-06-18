from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config.database import Base


class Distributor(Base):
    __tablename__ = "distributors"

    address: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profile_pic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Role-specific fields
    successful_campaign_count: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    has_security_deposit: Mapped[bool] = mapped_column(Boolean, default=False)
    active_campaign_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="distributor_user")
    proofs = relationship("Proof", back_populates="uploader")