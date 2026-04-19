from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base



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
    
    milestone_amount: Mapped[int] = mapped_column(Numeric(78, 0))  # Wei amount
    current_amount: Mapped[int] = mapped_column(Numeric(78, 0), default=0)
    is_active: Mapped[int] = mapped_column(Integer, default=0)  # 0=inactive, 1=active
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0=pending, 1=completed, 2=cancelled
    
    ipfs_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Latest proof
    proof_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    distributor_user = relationship("User", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign")
    proofs = relationship("Proof", back_populates="campaign")
    votes = relationship("Vote", back_populates="campaign")
