from config.database import SessionLocal
from services.distributor_service import DistributorService
import logging

logger = logging.getLogger(__name__)

async def handle_deposit_made(args, receipt):
    """Handle DepositMade event (distributor paid security deposit)."""
    db = SessionLocal()
    try:
        # Adjust argument names based on your contract's DepositMade event
        distributor = args['distributor']  # or 'sender'
        amount = args['amount']
        tx_hash = receipt['transactionHash'].hex()

        service = DistributorService(db)
        service.update_security_deposit(distributor, has_deposit=True)
        db.commit()
        logger.info(f"Processed DepositMade for distributor {distributor}, amount {amount}, tx {tx_hash}")
    except Exception as e:
        logger.error(f"Error in handle_deposit_made: {e}")
        db.rollback()
    finally:
        db.close()

async def handle_security_withdrawn(args, receipt):
    """Handle SecurityWithdrawn event (distributor withdrew security deposit)."""
    db = SessionLocal()
    try:
        distributor = args['distributor']  # or 'sender'
        amount = args['amount']
        tx_hash = receipt['transactionHash'].hex()

        service = DistributorService(db)
        service.update_security_deposit(distributor, has_deposit=False)
        db.commit()
        logger.info(f"Processed SecurityWithdrawn for distributor {distributor}, amount {amount}, tx {tx_hash}")
    except Exception as e:
        logger.error(f"Error in handle_security_withdrawn: {e}")
        db.rollback()
    finally:
        db.close()