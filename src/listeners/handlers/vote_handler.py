from core.database import SessionLocal
from services.campaign_service import CampaignService
import logging

logger = logging.getLogger(__name__)

async def handle_vote_cast(args, receipt):
    """Handle VoteCast event."""
    db = SessionLocal()
    try:
        # Adjust argument names based on your contract's VoteCast event
        campaign_id = args['campaignId']  # or 'id'
        voter = args['voter']
        vote_value = args['voteValue']   # True = positive/approve, False = negative/reject
        tx_hash = receipt['transactionHash'].hex()

        service = CampaignService(db)
        service.process_vote_cast(
            campaign_id=campaign_id,
            voter_address=voter,
            vote_value=vote_value,
            tx_hash=tx_hash
        )
        db.commit()
        logger.info(f"Processed VoteCast for campaign {campaign_id}, voter {voter}, vote {vote_value}")
    except Exception as e:
        logger.error(f"Error in handle_vote_cast: {e}")
        db.rollback()
    finally:
        db.close()