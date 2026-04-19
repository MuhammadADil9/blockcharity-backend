from web3 import Web3
from core.config import settings
from listeners.handlers import (
    campaign_handler, donation_handler, proof_handler, vote_handler
)
import json
import logging

logger = logging.getLogger(__name__)

with open(settings.ABI_PATH) as f:
    contract_abi = json.load(f)
w3 = Web3()
contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=contract_abi)

EVENT_HANDLERS = {
    "CampaignCreated": campaign_handler.handle_campaign_created,
    "MilestoneAchieved": campaign_handler.handle_milestone_achieved,
    "CampaignCompleted": campaign_handler.handle_campaign_completed,
    "CampaignCancelled": campaign_handler.handle_campaign_cancelled,
    "DonationReceived": donation_handler.handle_donation_received,
    "RefundIssued": donation_handler.handle_refund_issued,
    "SecurityRefundIssued": donation_handler.handle_security_refund,
    "ProofUploaded": proof_handler.handle_proof_uploaded,
    "VoteCast": vote_handler.handle_vote_cast,
}

async def process_event(log):
    """Decode log and call handler"""
    try:
        receipt = log  # raw log from WebSocket
        event_name = None
        # Find event signature in ABI
        for event in contract.events:
            if event().abi['signature'] == receipt['topics'][0].hex():
                event_name = event().abi['name']
                break
        if not event_name:
            return
        
        # Decode event data
        decoded = contract.events[event_name]().process_log(receipt)
        args = decoded['args']
        
        handler = EVENT_HANDLERS.get(event_name)
        if handler:
            await handler(args, receipt)
        else:
            logger.info(f"No handler for event: {event_name}")
    except Exception as e:
        logger.error(f"Event processing error: {e}")