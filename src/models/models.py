from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class User(Base):
    __tablename__ = "users"

    address = Column(String, primary_key=True, index=True) # Wallet Address is PK
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    profile_pic = Column(String, nullable=True) # URL to image
    is_distributor = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaigns = relationship("Campaign", back_populates="distributor_user")
    donations = relationship("Donation", back_populates="donor_user")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True) # On-chain ID
    distributor_address = Column(String, ForeignKey("users.address"))
    
    # Off-chain Metadata
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category_name = Column(String, nullable=True) # String representation of Enum
    location = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # On-chain Data Cached (for fast sorting/filtering)
    milestone_amount = Column(String) # Stored as string to handle uint256
    current_amount = Column(String, default="0")
    is_active = Column(Integer, default=0)
    status = Column(Integer, default=0) # 0: Funding, 1: MilestoneMet, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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

class SystemEvent(Base):
    """Tracks which block we have processed to avoid double-counting events"""
    __tablename__ = "system_events"
    id = Column(Integer, primary_key=True)
    last_processed_block = Column(Integer, default=0)