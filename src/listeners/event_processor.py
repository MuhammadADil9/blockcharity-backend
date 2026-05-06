from web3 import Web3
from config.config import settings
from listeners.handlers import (
    campaign_handler, donation_handler, proof_handler, vote_handler
)
import json
import logging

logger = logging.getLogger(__name__)

# Load ABI once
with open(settings.ABI_PATH) as f:
    contract_abi = json.load(f)

# Connect to Web3 provider (HTTP for event log decoding)
w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))

contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=contract_abi)

# Build event signature -> event name mapping from ABI directly
# web3 v7 doesn't support contract.events.items()
event_signatures = {}
for item in contract_abi:
    if item.get('type') == 'event':
        name = item['name']
        input_types = ','.join(inp['type'] for inp in item['inputs'])
        sig_text = f"{name}({input_types})"
        sig_hash = Web3.keccak(text=sig_text).hex()
        # Store without 0x prefix for consistent matching
        event_signatures[sig_hash] = name
        logger.info(f"Registered event: {name} -> {sig_hash[:16]}...")

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
    "FundsWithdrawn": campaign_handler.handle_funds_withdrawn,
}


def _normalize_log(log):
    """
    Normalize a log from either WebSocket (hex strings) or eth.get_logs (HexBytes)
    into a format that web3's process_log can handle.
    """
    from hexbytes import HexBytes

    normalized = dict(log)

    # Normalize topics: ensure they are HexBytes
    if 'topics' in normalized:
        normalized['topics'] = [
            HexBytes(t) if isinstance(t, str) else t
            for t in normalized['topics']
        ]

    # Normalize data
    if 'data' in normalized and isinstance(normalized['data'], str):
        normalized['data'] = HexBytes(normalized['data'])

    # Normalize transactionHash
    if 'transactionHash' in normalized and isinstance(normalized['transactionHash'], str):
        normalized['transactionHash'] = HexBytes(normalized['transactionHash'])

    # Normalize blockNumber (WebSocket sends hex string)
    if 'blockNumber' in normalized and isinstance(normalized['blockNumber'], str):
        normalized['blockNumber'] = int(normalized['blockNumber'], 16)

    # Normalize logIndex
    if 'logIndex' in normalized and isinstance(normalized['logIndex'], str):
        normalized['logIndex'] = int(normalized['logIndex'], 16)

    # Normalize transactionIndex
    if 'transactionIndex' in normalized and isinstance(normalized['transactionIndex'], str):
        normalized['transactionIndex'] = int(normalized['transactionIndex'], 16)

    # Normalize blockHash
    if 'blockHash' in normalized and isinstance(normalized['blockHash'], str):
        normalized['blockHash'] = HexBytes(normalized['blockHash'])

    # Normalize address to checksum
    if 'address' in normalized and isinstance(normalized['address'], str):
        normalized['address'] = Web3.to_checksum_address(normalized['address'])

    return normalized


async def process_event(log):
    """
    Decode a raw log (from WebSocket or historical fetch) and dispatch to handler.
    """
    try:
        # Normalize the log first
        normalized = _normalize_log(log)

        # Extract event signature (first topic)
        topic_raw = normalized['topics'][0]
        # Convert to hex string without 0x prefix for matching
        if hasattr(topic_raw, 'hex'):
            topic = topic_raw.hex()
        else:
            topic = topic_raw.lstrip('0x')

        event_name = event_signatures.get(topic)
        if not event_name:
            logger.debug(f"Unknown event topic: {topic[:16]}...")
            return

        # Decode the log using the contract's event
        event_obj = getattr(contract.events, event_name)
        decoded = event_obj().process_log(normalized)
        args = decoded['args']

        handler = EVENT_HANDLERS.get(event_name)
        if handler:
            await handler(args, normalized)
            logger.info(f"Handled event: {event_name}")
        else:
            logger.warning(f"No handler registered for event: {event_name}")
    except Exception as e:
        logger.error(f"Event processing error: {e}", exc_info=True)