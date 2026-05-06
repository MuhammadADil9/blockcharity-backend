from config.database import SessionLocal
from models.vote import Vote
from models.campaign import Campaign
from models.donor import Donor
from models.distributor import Distributor
from models.donation import Donation
from models.proof import Proof
from models.lottery_winner import LotteryWinner
from models.sync_state import SyncState

db = SessionLocal()

try:
    votes = db.query(Vote).all()
    print(f"Total votes found: {len(votes)}")
    if votes:
        for v in votes:
            campaign = db.query(Campaign).filter(Campaign.id == v.campaign_id).first()
            campaign_title = campaign.title if campaign else "Unknown Campaign"
            print(f"Vote ID: {v.id}")
            print(f"  Campaign: {campaign_title} (ID: {v.campaign_id})")
            print(f"  Voter: {v.voter_address}")
            print(f"  Value: {'Positive' if v.vote else 'Negative'}")
            print(f"  Tx Hash: {v.tx_hash}")
            print("-" * 20)
    else:
        print("No votes found in the 'votes' table.")

finally:
    db.close()
