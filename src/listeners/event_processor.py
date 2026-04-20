from web3 import Web3
from core.config import settings
from listeners.handlers import (
    campaign_handler, donation_handler, proof_handler, vote_handler
)
import json
import logging

logger = logging.getLogger(__name__)

# Load ABI once
with open(settings.ABI_PATH) as f:
    contract_abi = json.load(f)

# Connect to Web3 provider (HTTP for historical, WS for real-time)
w3 = Web3(Web3.WebsocketProvider(settings.RPC_URL))  # or HTTPProvider for polling

contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=contract_abi)

# Precompute event signature -> event name mapping
event_signatures = {}
for event_name, event in contract.events.items():
    event_signatures[event.abi['signature']] = event_name

EVENT_HANDLERS = {
    "CampaignCreated": campaign_handler.handle_campaign_created,
    "DonationReceived": donation_handler.handle_donation_received,
    "MilestoneAchieved": campaign_handler.handle_milestone_achieved,
    "ProofUploaded": proof_handler.handle_proof_uploaded,
    "VoteCast": vote_handler.handle_vote_cast,
    "CampaignCompleted": campaign_handler.handle_campaign_completed,
    "CampaignCancelled": campaign_handler.handle_campaign_cancelled,
    "RefundIssued": donation_handler.handle_refund_issued,
    "SecurityRefundIssued": donation_handler.handle_security_refund,
}

async def process_event(log):
    """Decode log and call handler"""
    try:
        topic = log['topics'][0].hex()
        event_name = event_signatures.get(topic)
        if not event_name:
            return
        
        # Decode event data
        decoded = contract.events[event_name]().process_log(log)
        args = decoded['args']
        
        handler = EVENT_HANDLERS.get(event_name)
        if handler:
            await handler(args, log)
        else:
            logger.info(f"No handler for event: {event_name}")
    except Exception as e:
        logger.error(f"Event processing error: {e}")