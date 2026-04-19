from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base

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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaigns = relationship("Campaign", back_populates="distributor_user")
    donations = relationship("Donation", back_populates="donor_user")
    votes = relationship("Vote", back_populates="voter_user")
