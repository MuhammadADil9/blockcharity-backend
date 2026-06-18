import json
import time
from web3 import Web3
from sqlalchemy.orm import Session
from src.config.config import settings
from src.config.database import SessionLocal, engine
from src.models import models

w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))

with open(settings.ABI_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)

contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_campaign_created(event, db: Session):
    args = event['args']
    campaign_id = args['campaignId']
    distributor = args['distributor']
    milestone = str(args['milestone']) # Store as string

    print(f"[*] New Campaign Detected: ID {campaign_id} by {distributor}")

    # Check if exists (might have been created by API first)
    camp = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not camp:
        # Create minimal record (Metadata will be filled by API later)
        camp = models.Campaign(
            id=campaign_id,
            distributor_address=distributor,
            milestone_amount=milestone,
            title=f"Campaign #{campaign_id}", # Placeholder
            description="Waiting for details...", # Placeholder
            status=0 # Funding
        )
        db.add(camp)
    else:
        # Update on-chain facts
        camp.milestone_amount = milestone
        camp.distributor_address = distributor
    
    db.commit()

def handle_donation(event, db: Session):
    args = event['args']
    campaign_id = args['campaignId']
    donor = args['donor']
    amount = str(args['amount'])
    tx_hash = event['transactionHash'].hex()

    print(f"[$] Donation Detected: {amount} to ID {campaign_id}")

    # 1. Record Donation
    donation = models.Donation(
        tx_hash=tx_hash,
        campaign_id=campaign_id,
        donor_address=donor,
        amount=amount
    )
    db.add(donation)

    # 2. Update Campaign Total
    camp = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if camp:
        current = int(camp.current_amount) if camp.current_amount else 0
        new_total = current + int(args['amount'])
        camp.current_amount = str(new_total)
    
    db.commit()

def handle_milestone(event, db: Session):
    campaign_id = event['args']['campaignId']
    print(f"[!] Milestone Achieved: ID {campaign_id}")
    
    camp = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if camp:
        camp.status = 1 # Mark as Milestone Met
        db.commit()

def sync_events():
    db = next(get_db())
    
    # Get last processed block
    sys_event = db.query(models.SystemEvent).first()
    if not sys_event:
        sys_event = models.SystemEvent(last_processed_block=0)
        db.add(sys_event)
        db.commit()
    
    start_block = sys_event.last_processed_block + 1
    current_block = w3.eth.block_number

    if start_block > current_block:
        return # Nothing new

    print(f"Checking blocks {start_block} to {current_block}...")

    # Define Event Filters
    # Note: We filter by specific event names defined in your ABI
    
    # 1. CampaignCreated
    logs_created = contract.events.CampaignCreated.get_logs(fromBlock=start_block, toBlock=current_block)
    for log in logs_created:
        handle_campaign_created(log, db)

    # 2. DonationReceived
    logs_donate = contract.events.DonationReceived.get_logs(fromBlock=start_block, toBlock=current_block)
    for log in logs_donate:
        handle_donation(log, db)

    # 3. MilestoneAchieved
    logs_milestone = contract.events.MilestoneAchieved.get_logs(fromBlock=start_block, toBlock=current_block)
    for log in logs_milestone:
        handle_milestone(log, db)

    # Update processed block
    sys_event.last_processed_block = current_block
    db.commit()

if __name__ == "__main__":
    print("--- Blockchain Indexer Started ---")
    if w3.is_connected():
        print(f"Connected to Anvil at {settings.HTTP_RPC_URL}")
    else:
        print("Error: Could not connect to Anvil.")
    
    while True:
        try:
            sync_events()
        except Exception as e:
            print(f"Error syncing: {e}")
        time.sleep(2) # Poll every 2 seconds