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
    campaign_count = db.query(Campaign).count()
    vote_count = db.query(Vote).count()
    print(f"Campaigns in database: {campaign_count}")
    print(f"Votes in database: {vote_count}")

finally:
    db.close()
