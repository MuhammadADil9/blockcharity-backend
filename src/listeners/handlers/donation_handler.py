from core.database import SessionLocal
from services.campaign_service import CampaignService
from services.donor_service import DonorService
import logging

logger = logging.getLogger(__name__)

async def handle_donation_received(args, receipt):
    """Handle DonationReceived event."""
    db = SessionLocal()
    try:
        # Adjust argument names based on your contract's DonationReceived event
        campaign_id = args['campaignId']  # or 'id'
        donor = args['donor']
        amount = args['amount']
        tx_hash = receipt['transactionHash'].hex()

        # Process donation (updates campaign current_amount and donor total)
        campaign_service = CampaignService(db)
        campaign_service.process_donation(
            campaign_id=campaign_id,
            donor_address=donor,
            amount_wei=amount,
            tx_hash=tx_hash
        )
        db.commit()
        logger.info(f"Processed DonationReceived: campaign {campaign_id}, donor {donor}, amount {amount}")
    except Exception as e:
        logger.error(f"Error in handle_donation_received: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_refund_issued(args, receipt):
    """Handle RefundIssued event (when distributor cancels campaign, donors get refunded)."""
    db = SessionLocal()
    try:
        # Adjust argument names: likely (donor, amount)
        donor = args['donor']
        amount = args['amount']
        # Optional: campaign_id might be in event; if not, you may need to derive from receipt.
        # Your contract's RefundIssued event should include campaignId. Adjust as needed.
        campaign_id = args.get('campaignId', None)
        tx_hash = receipt['transactionHash'].hex()

        # For now, just log. You may want to mark donation as refunded or reduce campaign current_amount.
        # Since you chose not to have a 'refunded' flag, you could decrement campaign.current_amount
        # But careful: campaign may already be canceled. Simpler: just log.
        logger.info(f"RefundIssued: donor {donor}, amount {amount}, campaign {campaign_id}, tx {tx_hash}")
        # Optionally call a service method to handle refund (e.g., update campaign.current_amount)
        # from services.campaign_service import CampaignService
        # service = CampaignService(db)
        # service.process_refund(campaign_id, donor, amount)
        db.commit()
    except Exception as e:
        logger.error(f"Error in handle_refund_issued: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_security_refund(args, receipt):
    """Handle SecurityRefundIssued event (when admin cancels, donors get part of security deposit)."""
    db = SessionLocal()
    try:
        donor = args['donor']
        amount = args['amount']
        campaign_id = args.get('campaignId', None)
        tx_hash = receipt['transactionHash'].hex()
        logger.info(f"SecurityRefundIssued: donor {donor}, amount {amount}, campaign {campaign_id}, tx {tx_hash}")
        db.commit()
    except Exception as e:
        logger.error(f"Error in handle_security_refund: {e}")
        db.rollback()
    finally:
        db.close()