# repositories/campaign_repo.py
from repositories.base import BaseRepository
from models.campaign import Campaign

class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db_session):
        super().__init__(Campaign, db_session)
    
    # Add custom methods if needed
    def get_active_campaigns(self, skip: int = 0, limit: int = 100):
        return self.get_multi_by(skip=skip, limit=limit, is_active=1)
    
    def get_by_distributor(self, distributor_address: str):
        return self.get_multi_by(distributor_address=distributor_address)