from config.database import SessionLocal
from models.campaign import Campaign
from schemas.user import CampaignResponse

db = SessionLocal()
campaign = db.query(Campaign).filter(
    Campaign.distributor_address == "0x83C549cC62fEd4798545d945daFB597186981E9c",
    Campaign.status == 0
).first()

if campaign:
    try:
        resp = CampaignResponse.model_validate(campaign)
        print("Success:", resp)
    except Exception as e:
        print("Validation Error:", e)
else:
    print("Campaign not found")
