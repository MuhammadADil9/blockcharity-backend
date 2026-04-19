from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import IntEnum



class CampaignCategory(IntEnum):
    weatherCrisis = 0
    shelter = 1
    food = 2

CATEGORY_LABELS = {
    CampaignCategory.weatherCrisis: "Weather Crisis",
    CampaignCategory.shelter: "Shelter",
    CampaignCategory.food: "Food",
}



# 1. The Base: Fields common to both reading and writing
class UserBase(BaseModel):
    address: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None # We mapped 'country' to this
    profile_pic: Optional[str] = None
    is_distributor: bool = False

# 2. The Request: What the frontend SENDS (camelCase to match JS)
class UserRegisterRequest(BaseModel):
    walletAddress: str
    firstName: str
    lastName: str
    country: str
    email: str
    phone: str
    role: str

# 3. The Response: What the backend REPLIES (snake_case from DB)
class UserResponse(UserBase):
    created_at: Optional[datetime] = None

    class Config:
        # This tells Pydantic to read data even if it's an ORM object (SQLAlchemy)
        from_attributes = True


class UserContactInfo(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None # Maps to 'location' in DB

    class Config:
        from_attributes = True



class CampaignCreateRequest(BaseModel):
    id: int
    title: str
    description: str
    location: str
    endDate: datetime
    milestone: str
    category: int = 0  # 0=weatherCrisis, 1=shelter, 2=food

    class Config:
        from_attributes = True

class CampaignResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    milestone_amount: str
    current_amount: str
    status: int          # 0: Funding, 1: Met, etc.
    end_date: datetime
    distributor_address: str
    
    class Config:
        from_attributes = True