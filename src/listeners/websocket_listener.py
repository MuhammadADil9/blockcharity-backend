import asyncio
import json
import websockets
from core.config import settings
from listeners.event_processor import process_event
import logging

logger = logging.getLogger(__name__)

async def fetch_missed_events(from_block, to_block):
    """Fetch historical logs for missed blocks (called on reconnect)"""
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))  # HTTP for polling
    logs = w3.eth.get_logs({
        "address": settings.CONTRACT_ADDRESS,
        "fromBlock": from_block,
        "toBlock": to_block
    })
    for log in logs:
        await process_event(log)

async def listen_to_contract_events():
    """Background task: WebSocket with missed block recovery"""
    uri = settings.RPC_URL  # ws://localhost:8545
    last_processed_block = await get_last_synced_block()  # implement DB read
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                # Subscribe
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "method": "eth_subscribe",
                    "params": ["logs", {"address": settings.CONTRACT_ADDRESS}],
                    "id": 1
                }
                await ws.send(json.dumps(subscribe_msg))
                logger.info("Subscribed to contract events")
                
                # Optional: send heartbeat ping every 30s
                async def send_ping():
                    while True:
                        await asyncio.sleep(30)
                        await ws.send(json.dumps({"jsonrpc": "2.0", "method": "net_version", "id": 2}))
                asyncio.create_task(send_ping())
                
                async for message in ws:
                    data = json.loads(message)
                    if "params" in data:
                        log = data["params"]["result"]
                        block_num = int(log["blockNumber"], 16)
                        # Update last_processed_block in DB after handling
                        await process_event(log)
                        await update_last_synced_block(block_num)  # implement DB write
        except Exception as e:
            logger.error(f"WebSocket error: {e}. Reconnecting...")
            # On reconnect, fetch missed blocks
            latest_block = w3.eth.block_number
            if last_processed_block < latest_block:
                await fetch_missed_events(last_processed_block + 1, latest_block)
            await asyncio.sleep(5)