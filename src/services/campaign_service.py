from typing import Optional
from sqlalchemy.orm import Session
from repositories.campaign_repo import CampaignRepository
from repositories.distributor_repo import DistributorRepository
from repositories.donation_repo import DonationRepository
from models.campaign import Campaign
import logging

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, db: Session):
        self.db = db
        self.campaign_repo = CampaignRepository(db)
        self.distributor_repo = DistributorRepository(db)
        self.donation_repo = DonationRepository(db)

    # ------------------------------------------------------------------
    # Event-driven sync (called by handlers)
    # ------------------------------------------------------------------

    def sync_campaign_from_event(
        self,
        campaign_id: int,
        distributor_address: str,
        milestone_amount: int,
        category_name: Optional[str],
        tx_hash: str
    ) -> Campaign:
        """Called when CampaignCreated event is received."""
        # Ensure distributor exists in DB (create if not)
        distributor = self.distributor_repo.get_by_address(distributor_address)
        if not distributor:
            distributor = self.distributor_repo.create_or_update(
                address=distributor_address
            )
            logger.info(f"Created new distributor record for {distributor_address}")

        # Create campaign record using repo method
        campaign = self.campaign_repo.create_from_event(
            campaign_id=campaign_id,
            distributor_address=distributor_address,
            milestone_amount=milestone_amount,
            category_name=category_name,
            tx_hash=tx_hash
        )
        logger.info(f"Synced campaign {campaign_id} from event")

        # Update distributor's active campaign
        self.distributor_repo.set_active_campaign(distributor_address, campaign_id)

        return campaign

    def update_metadata(
        self,
        campaign_id: int,
        title: str,
        description: str,
        category_name: Optional[str] = None,
        location: Optional[str] = None,
        end_date: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Optional[Campaign]:
        """Update off-chain metadata (called by API after campaign creation)."""
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for metadata update")
            return None

        # Use repo update method (assumes update method accepts these fields)
        # Note: Your Campaign model has these fields; update method uses **kwargs
        return self.campaign_repo.update(
            campaign_id,
            title=title,
            description=description,
            category_name=category_name,
            location=location,
            end_date=end_date,
            image_url=image_url
        )

    def process_donation(
        self,
        campaign_id: int,
        donor_address: str,
        amount_wei: int,
        tx_hash: str
    ) -> None:
        """Called by DonationReceived handler."""
        # Create donation record (idempotent)
        donation = self.donation_repo.create_or_ignore(
            tx_hash=tx_hash,
            campaign_id=campaign_id,
            donor_address=donor_address,
            amount=amount_wei
        )
        if not donation:
            logger.warning(f"Donation {tx_hash} already exists, skipping")
            return

        # Increment campaign current_amount atomically
        campaign = self.campaign_repo.update_current_amount(campaign_id, amount_wei)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for donation")
            return

        # Check if milestone reached
        self._check_milestone_reached(campaign_id)

        # Update donor's total donated (if Donor model exists)
        # We'll assume donor_service is available; for now, call directly
        # (Avoid circular import: import inside method or inject donor_service)
        from services.donor_service import DonorService
        donor_service = DonorService(self.db)
        donor_service.increment_total_donated(donor_address, amount_wei)

    def _check_milestone_reached(self, campaign_id: int) -> None:
        """Internal: if current_amount >= milestone, update activity status and emit timer start."""
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            return

        if campaign.current_amount >= campaign.milestone_amount:
            # Only transition if still in funding stage
            if campaign.activity_status == 0:  # inFunding
                self.campaign_repo.update_activity_status(campaign_id, 1)  # milestoneAchieved
                logger.info(f"Campaign {campaign_id} reached milestone")
                # Start 48-hour timer for proof upload
                self._start_proof_timer(campaign_id)

    def _start_proof_timer(self, campaign_id: int) -> None:
        """Placeholder: schedule a background task to check proof upload after 48h."""
        # Implementation will use Celery, APScheduler, or asyncio.create_task
        # For now, just log and delegate to timer service
        from services.timer_service import TimerService
        timer = TimerService()
        timer.schedule_proof_deadline(campaign_id, hours=48)
        logger.info(f"Scheduled proof deadline for campaign {campaign_id} in 48h")

    def process_milestone_achieved(self, campaign_id: int) -> None:
        """Called by MilestoneAchieved event handler (already handled by _check_milestone_reached,
        but can be used for explicit sync)."""
        campaign = self.campaign_repo.update_activity_status(campaign_id, 1)
        if campaign:
            logger.info(f"Processed milestone achieved event for campaign {campaign_id}")

    def process_funds_withdrawn(self, campaign_id: int, distributor_address: str, amount: int) -> None:
        """Called by FundsWithdrawn event."""
        # Update activity status to proofToBeUploaded (2)
        campaign = self.campaign_repo.update_activity_status(campaign_id, 2)
        if campaign:
            logger.info(f"Funds withdrawn for campaign {campaign_id}, now proofToBeUploaded")
            # No need to start another timer; timer already running from milestone reached

    def process_proof_uploaded(
        self,
        campaign_id: int,
        ipfs_hash: str,
        uploaded_by: str,
        tx_hash: str
    ) -> None:
        """Called by ProofUploaded handler."""
        # Create proof record (using proof_repo)
        from repositories.proof_repo import ProofRepository
        proof_repo = ProofRepository(self.db)
        proof_repo.create_proof(
            campaign_id=campaign_id,
            ipfs_hash=ipfs_hash,
            uploaded_by=uploaded_by
        )
        # Update campaign activity status to voting (3)
        self.campaign_repo.update_activity_status(campaign_id, 3)
        logger.info(f"Proof uploaded for campaign {campaign_id}, now voting stage")
        # Start 24-hour timer for triggerResult
        self._start_voting_timer(campaign_id)

    def _start_voting_timer(self, campaign_id: int) -> None:
        """Schedule triggerResult after 10m."""
        from services.timer_service import TimerService
        timer = TimerService()
        timer.schedule_voting_deadline(campaign_id, minutes=10)
        logger.info(f"Scheduled voting deadline for campaign {campaign_id} in 10m")

    def process_vote_cast(
        self,
        campaign_id: int,
        voter_address: str,
        vote_value: bool,
        tx_hash: str
    ) -> None:
        """Called by VoteCast handler."""
        from repositories.vote_repo import VoteRepository
        vote_repo = VoteRepository(self.db)
        # Create vote record (idempotent)
        vote = vote_repo.create_vote(
            tx_hash=tx_hash,
            campaign_id=campaign_id,
            voter_address=voter_address,
            vote=vote_value
        )
        if not vote:
            logger.warning(f"Vote {tx_hash} already exists, skipping")
            return

        # Update campaign aggregates
        stats = vote_repo.get_campaign_vote_stats(campaign_id)
        self.campaign_repo.update_vote_counts(
            campaign_id,
            positive_votes=stats["yes"],
            negative_votes=stats["no"],
            total_voters=stats["total"]
        )
        logger.info(f"Vote cast for campaign {campaign_id} by {voter_address}: {vote_value}")

    def trigger_result(self, campaign_id: int) -> None:
        """
        Called by timer or admin. 
        This method should call the smart contract's triggerResult() via web3,
        using owner private key. After transaction is mined, the resulting
        event (CampaignCompleted or CampaignCancelled) will be handled separately.
        """
        # Placeholder: actual blockchain call will be implemented in a blockchain service.
        # For now, log and delegate.
        from services.blockchain_service import BlockchainService
        bc = BlockchainService()
        tx_hash = bc.call_trigger_result(campaign_id)
        logger.info(f"Triggered result for campaign {campaign_id}, tx: {tx_hash}")

    def process_campaign_completed(self, campaign_id: int) -> None:
        """Called by CampaignCompleted event handler."""
        campaign = self.campaign_repo.update_status(campaign_id, 1)  # completed
        if campaign:
            self.campaign_repo.update_activity_status(campaign_id, 4)  # result
            # Increment distributor's successful campaigns
            dist_addr = campaign.distributor_address
            self.distributor_repo.update_successful_campaigns(dist_addr, 1)
            self.distributor_repo.set_active_campaign(dist_addr, None)
            logger.info(f"Campaign {campaign_id} completed successfully")

    def process_campaign_cancelled(self, campaign_id: int, reason: str = "Cancelled") -> None:
        """Called by CampaignCancelled event handler."""
        campaign = self.campaign_repo.update_status(campaign_id, 2)  # canceled
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for cancellation")
            return

        self.campaign_repo.update_activity_status(campaign_id, 4)  # result
        
        # Clear active campaign from distributor
        dist_addr = campaign.distributor_address
        self.distributor_repo.set_active_campaign(dist_addr, None)

        if reason == "Cancelled by distributor":
            # Zero out donations and update donor totals
            # We'll fetch all donations for this campaign
            donations = self.donation_repo.get_by_campaign(campaign_id, limit=5000)
            
            # Avoid circular imports by importing inside method
            from services.donor_service import DonorService
            donor_service = DonorService(self.db)
            
            for donation in donations:
                if donation.amount > 0:
                    # Decrement donor's total_donated_wei
                    donor_service.decrement_total_donated(donation.donor_address, int(donation.amount))
                    # Update donation amount to 0 in DB
                    self.donation_repo.update(donation.id, amount=0)
            
            logger.info(f"Campaign {campaign_id} cancelled by distributor. {len(donations)} donations zeroed out.")

        elif reason == "Cancelled by Admin - Fraud/Failure":
            # Mark distributor as banned
            self.distributor_repo.set_banned(dist_addr, True)
            logger.info(f"Campaign {campaign_id} cancelled by admin. Distributor {dist_addr} banned.")
        
        logger.info(f"Processed CampaignCancelled: {campaign_id}, reason: {reason}")

    def force_cancel_no_proof(self, campaign_id: int) -> None:
        """
        Called by timer when no proof uploaded within 48h after milestone.
        Calls contract's cancelCampaignBySmartContract as owner.
        """
        from services.blockchain_service import BlockchainService
        bc = BlockchainService()
        tx_hash = bc.call_cancel_campaign_by_smart_contract(campaign_id)
        logger.info(f"Forced cancel for campaign {campaign_id} (no proof), tx: {tx_hash}")

    # ------------------------------------------------------------------
    # Public query methods (for API)
    # ------------------------------------------------------------------

    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        return self.campaign_repo.get_by_id(campaign_id)

    def get_campaigns_paginated(self, cursor: int, limit: int):
        # Use campaign_repo.get_all with offset/cursor
        # Implementation depends on your pagination style
        pass

    def get_distributor_campaigns(self, distributor_address: str):
        return self.campaign_repo.get_by_distributor(distributor_address)