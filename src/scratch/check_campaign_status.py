from config.database import SessionLocal
from models.campaign import Campaign
from models.vote import Vote
from models.donor import Donor
from models.distributor import Distributor
from models.donation import Donation
from models.proof import Proof
from models.lottery_winner import LotteryWinner
from models.sync_state import SyncState

db = SessionLocal()

try:
    campaign = db.query(Campaign).first()
    if campaign:
        print(f"Campaign ID: {campaign.id}")
        print(f"Title: {campaign.title}")
        print(f"Status: {campaign.status} (0=active, 1=completed, 2=canceled)")
        print(f"Activity Status: {campaign.activity_status} (0=funding, 1=milestone, 2=proofReq, 3=voting, 4=result)")
        print(f"Current Amount: {campaign.current_amount}")
        print(f"Positive Votes: {campaign.positive_votes}")
        print(f"Negative Votes: {campaign.negative_votes}")
        print(f"Voting Deadline: {campaign.voting_deadline}")
    else:
        print("No campaigns found.")

finally:
    db.close()
