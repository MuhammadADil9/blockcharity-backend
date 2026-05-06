from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from config.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))
        # Inject POA middleware for networks like Ganache or Anvil (optional but safe)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # Load contract
        with open(settings.ABI_PATH) as f:
            contract_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=contract_abi
        )
        self.owner_address = settings.OWNER_ADDRESS
        self.owner_private_key = settings.OWNER_PRIVATE_KEY

    def _send_transaction(self, function_call):
        """Build, sign, send a transaction and return (tx_hash_hex, receipt)."""
        tx = function_call.build_transaction({
            'from': self.owner_address,
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.owner_address),
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.owner_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f"Transaction sent: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        logger.info(f"Transaction confirmed in block {receipt.blockNumber}")
        return tx_hash.hex(), receipt

    def call_trigger_result(self, campaign_id: int) -> str:
        """Call triggerResult(uint256 _id) as owner, then process resulting events directly."""
        try:
            function_call = self.contract.functions.triggerResult(campaign_id)
            tx_hash, receipt = self._send_transaction(function_call)
            logger.info(f"triggerResult called for campaign {campaign_id}, tx: {tx_hash}")
            self._process_receipt_events(receipt)
            return tx_hash
        except Exception as e:
            logger.error(f"Failed to call triggerResult for campaign {campaign_id}: {e}")
            raise

    def call_cancel_campaign_by_smart_contract(self, campaign_id: int) -> str:
        """Call cancelCampaignBySmartContract(uint256 _id) as owner."""
        try:
            function_call = self.contract.functions.cancelCampaignBySmartContract(campaign_id)
            tx_hash, receipt = self._send_transaction(function_call)
            logger.info(f"cancelCampaignBySmartContract called for campaign {campaign_id}, tx: {tx_hash}")
            self._process_receipt_events(receipt)
            return tx_hash
        except Exception as e:
            logger.error(f"Failed to cancel campaign {campaign_id} by smart contract: {e}")
            raise

    def _process_receipt_events(self, receipt) -> None:
        """Decode and handle events from a confirmed receipt immediately, without waiting for WebSocket."""
        from listeners.event_processor import process_event
        import asyncio

        for log in receipt.get('logs', []):
            log_dict = dict(log)
            # Convert HexBytes fields to plain types for process_event compatibility
            if hasattr(log_dict.get('transactionHash'), 'hex'):
                log_dict['transactionHash'] = log_dict['transactionHash']
            try:
                asyncio.get_event_loop().run_until_complete(process_event(log_dict))
            except RuntimeError:
                # Already inside a running loop (async context)
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, process_event(log_dict))
                    future.result()