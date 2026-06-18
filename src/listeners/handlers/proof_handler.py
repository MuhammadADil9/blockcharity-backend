from config.database import SessionLocal
from services.campaign_service import CampaignService
from services.notification_service import NotificationService
from models.notification import NotificationType
import logging

logger = logging.getLogger(__name__)

async def handle_proof_uploaded(args, receipt):
    """Handle ProofUploaded event."""
    db = SessionLocal()
    try:
        # Match ABI: event ProofUploaded(uint256 indexed campaignId, string ipfsHash)
        campaign_id = args['campaignId']
        ipfs_hash = args['ipfsHash']
        tx_hash = receipt['transactionHash'].hex()

        service = CampaignService(db)
        
        # We fetch the campaign to get the uploader (distributor) address
        campaign = service.get_campaign(campaign_id)
        uploaded_by = campaign.distributor_address if campaign else None

        if uploaded_by:
            service.process_proof_uploaded(
                campaign_id=campaign_id,
                ipfs_hash=ipfs_hash,
                uploaded_by=uploaded_by,
                tx_hash=tx_hash
            )

            try:
                title = campaign.title if campaign else f"Campaign #{campaign_id}"
                notif = NotificationService(db)
                notif.broadcast_to_donors(
                    campaign_id=campaign_id,
                    message=f"Proof of work has been uploaded for '{title}'. Review it and cast your vote.",
                    type=NotificationType.ActionRequired,
                )
            except Exception as ne:
                logger.error(f"Notification error in handle_proof_uploaded: {ne}")

            db.commit()
            logger.info(f"Processed ProofUploaded for campaign {campaign_id}, hash: {ipfs_hash}")
        else:
            logger.error(f"Could not find campaign {campaign_id} to attribute proof to.")
    except Exception as e:
        logger.error(f"Error in handle_proof_uploaded: {e}")
        db.rollback()
    finally:
        db.close()