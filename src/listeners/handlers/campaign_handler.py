from config.database import SessionLocal
from services.campaign_service import CampaignService
import logging

logger = logging.getLogger(__name__)

async def handle_campaign_created(args, receipt):
    """Handle CampaignCreated event."""
    db = SessionLocal()
    try:
        campaign_id = args['id']  # adjust key name based on your event args
        distributor = args['distributor']
        milestone = args['milestone']
        security_deposit = args['securityDeposit']  # unpacked but not stored
        category = args.get('category', {}).get('name')  # if category is a struct
        tx_hash = receipt['transactionHash'].hex()

        service = CampaignService(db)
        service.sync_campaign_from_event(
            campaign_id=campaign_id,
            distributor_address=distributor,
            milestone_amount=milestone,
            category_name=category,
            tx_hash=tx_hash
        )
        db.commit()
        logger.info(f"Processed CampaignCreated for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error in handle_campaign_created: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_milestone_achieved(args, receipt):
    """Handle MilestoneAchieved event."""
    db = SessionLocal()
    try:
        campaign_id = args['campaignId']  # adjust key name
        service = CampaignService(db)
        service.process_milestone_achieved(campaign_id)
        db.commit()
        logger.info(f"Processed MilestoneAchieved for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error in handle_milestone_achieved: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_funds_withdrawn(args, receipt):
    """Handle FundsWithdrawn event (if added)."""
    db = SessionLocal()
    try:
        campaign_id = args['campaignId']
        distributor = args['distributor']
        amount = args['amount']
        service = CampaignService(db)
        service.process_funds_withdrawn(campaign_id, distributor, amount)
        db.commit()
        logger.info(f"Processed FundsWithdrawn for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error in handle_funds_withdrawn: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_campaign_completed(args, receipt):
    """Handle CampaignCompleted event."""
    db = SessionLocal()
    try:
        campaign_id = args['campaignId']  # adjust key name
        service = CampaignService(db)
        service.process_campaign_completed(campaign_id)
        db.commit()
        logger.info(f"Processed CampaignCompleted for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error in handle_campaign_completed: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_campaign_cancelled(args, receipt):
    """Handle CampaignCancelled event."""
    db = SessionLocal()
    try:
        campaign_id = args['campaignId']  # adjust key name
        reason = args.get('reason', 'Cancelled')  # if event includes reason
        service = CampaignService(db)
        service.process_campaign_cancelled(campaign_id, reason)
        db.commit()
        logger.info(f"Processed CampaignCancelled for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error in handle_campaign_cancelled: {e}")
        db.rollback()
    finally:
        db.close()