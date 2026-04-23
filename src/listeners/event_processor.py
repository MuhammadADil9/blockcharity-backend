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

# Connect to Web3 provider (use HTTP for event log decoding; WebSocket for subscription is separate)
# Note: Web3.WebsocketProvider is deprecated. Use Web3(Web3.WebsocketProvider(...)) is fine for older versions,
# but for compatibility, use HTTPProvider for decoding. The WebSocket connection is handled in websocket_listener.
w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))

contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=contract_abi)

# Precompute event signature -> event name mapping (once, for performance)
event_signatures = {}
for event_name, event in contract.events.items():
    # Get the event's signature hash (topics[0])
    event_signatures[event.abi['signature']] = event_name

# Handler registry
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
    # Add FundsWithdrawn if you add the event to contract
}

async def process_event(log):
    """
    Decode a raw log (from WebSocket or historical fetch) and dispatch to handler.
    log: dict with 'topics', 'data', 'blockNumber', etc.
    """
    try:
        # Extract event signature (first topic)
        topic = log['topics'][0].hex()
        event_name = event_signatures.get(topic)
        if not event_name:
            # Unknown event, ignore
            return

        # Decode the log using the contract's event
        # Note: contract.events[event_name] returns an event object, call it with process_log
        event_obj = getattr(contract.events, event_name)
        decoded = event_obj().process_log(log)
        args = decoded['args']

        handler = EVENT_HANDLERS.get(event_name)
        if handler:
            # Call async handler, passing args and the raw log (if needed)
            await handler(args, log)
        else:
            logger.warning(f"No handler registered for event: {event_name}")
    except Exception as e:
        logger.error(f"Event processing error: {e}", exc_info=True)