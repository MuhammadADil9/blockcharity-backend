from config.database import SessionLocal
from services.campaign_service import CampaignService
import logging

logger = logging.getLogger(__name__)

async def handle_proof_uploaded(args, receipt):
    """Handle ProofUploaded event."""
    db = SessionLocal()
    try:
        # Adjust argument names based on your contract's ProofUploaded event
        campaign_id = args['campaignId']  # or 'id'
        ipfs_hash = args['ipfsHash']     # or 'hash'
        uploaded_by = args['uploadedBy'] # or 'distributor'
        tx_hash = receipt['transactionHash'].hex()

        service = CampaignService(db)
        service.process_proof_uploaded(
            campaign_id=campaign_id,
            ipfs_hash=ipfs_hash,
            uploaded_by=uploaded_by,
            tx_hash=tx_hash
        )
        db.commit()
        logger.info(f"Processed ProofUploaded for campaign {campaign_id}, hash: {ipfs_hash}")
    except Exception as e:
        logger.error(f"Error in handle_proof_uploaded: {e}")
        db.rollback()
    finally:
        db.close()