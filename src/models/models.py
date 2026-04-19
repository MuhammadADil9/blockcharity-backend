from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional 
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    address: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profile_pic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_distributor: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    campaigns = relationship("Campaign", back_populates="distributor_user")
    donations = relationship("Donation", back_populates="donor_user")

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    distributor_address: Mapped[str] = mapped_column(String, ForeignKey("users.address"))

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    milestone_amount: Mapped[str] = mapped_column(String)
    current_amount: Mapped[str] = mapped_column(String, default="0")
    is_active: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    distributor_user = relationship("User", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign")
    
class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String, unique=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    donor_address = Column(String, ForeignKey("users.address"))
    amount = Column(String) # Stored as string
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="donations")
    donor_user = relationship("User", back_populates="donations")

# class SystemEvent(Base):
#     """Tracks which block we have processed to avoid double-counting events"""
#     __tablename__ = "system_events"
#     id = Column(Integer, primary_key=True)
#     last_processed_block = Column(Integer, default=0)