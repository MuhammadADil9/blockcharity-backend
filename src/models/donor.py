from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config.database import Base


class Donor(Base):
    __tablename__ = "donors"

    address: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profile_pic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Role-specific fields
    total_donated_wei: Mapped[int] = mapped_column(Numeric(78, 0), default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    donations = relationship("Donation", back_populates="donor_user")
    votes = relationship("Vote", back_populates="voter_user")