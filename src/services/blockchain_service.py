from web3 import Web3
from web3.middleware import geth_poa_middleware
from core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))
        # Inject POA middleware for networks like Ganache or Anvil (optional but safe)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract
        with open(settings.ABI_PATH) as f:
            contract_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=contract_abi
        )
        self.owner_address = settings.OWNER_ADDRESS
        self.owner_private_key = settings.OWNER_PRIVATE_KEY

    def _send_transaction(self, function_call) -> str:
        """Helper to build, sign, and send a transaction."""
        tx = function_call.build_transaction({
            'from': self.owner_address,
            'gas': 500000,  # Adjust as needed
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.owner_address),
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.owner_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info(f"Transaction sent: {tx_hash.hex()}")
        # Optional: wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        logger.info(f"Transaction confirmed in block {receipt.blockNumber}")
        return tx_hash.hex()

    def call_trigger_result(self, campaign_id: int) -> str:
        """Call triggerResult(uint256 _id) as owner."""
        try:
            function_call = self.contract.functions.triggerResult(campaign_id)
            tx_hash = self._send_transaction(function_call)
            logger.info(f"triggerResult called for campaign {campaign_id}, tx: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"Failed to call triggerResult for campaign {campaign_id}: {e}")
            raise

    def call_cancel_campaign_by_smart_contract(self, campaign_id: int) -> str:
        """Call cancelCampaignBySmartContract(uint256 _id) as owner."""
        try:
            function_call = self.contract.functions.cancelCampaignBySmartContract(campaign_id)
            tx_hash = self._send_transaction(function_call)
            logger.info(f"cancelCampaignBySmartContract called for campaign {campaign_id}, tx: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"Failed to cancel campaign {campaign_id} by smart contract: {e}")
            raise