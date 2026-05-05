import asyncio
import json
import websockets
from web3 import Web3
from config.config import settings
from listeners.event_processor import process_event
from repositories.sync_state_repo import SyncStateRepository
from config.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

w3 = Web3(Web3.HTTPProvider(settings.HTTP_RPC_URL))


async def fetch_missed_events(from_block, to_block):
    logs = w3.eth.get_logs({
        "address": settings.CONTRACT_ADDRESS,
        "fromBlock": from_block,
        "toBlock": to_block
    })
    for log in logs:
        await process_event(log)


async def listen_to_contract_events():
    uri = settings.RPC_URL

    # Load last processed block from DB
    db = SessionLocal()
    try:
        repo = SyncStateRepository(db)
        last_processed = repo.get_last_block() or 0
    finally:
        db.close()

    while True:
        try:
            # 🔁 Catch up missed blocks BEFORE reconnecting
            latest_block = w3.eth.block_number
            if last_processed < latest_block:
                logger.info(f"Catching up from {last_processed} to {latest_block}")
                await fetch_missed_events(last_processed + 1, latest_block)
                last_processed = latest_block

                db = SessionLocal()
                try:
                    repo = SyncStateRepository(db)
                    repo.update_last_block(last_processed)
                finally:
                    db.close()

            # 🔌 Connect to WebSocket
            async with websockets.connect(uri) as ws:
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "method": "eth_subscribe",
                    "params": ["logs", {"address": settings.CONTRACT_ADDRESS}],
                    "id": 1
                }
                await ws.send(json.dumps(subscribe_msg))
                logger.info("Subscribed to contract events")

                async for message in ws:
                    data = json.loads(message)

                    if "params" not in data:
                        continue

                    log = data["params"]["result"]
                    block_num = int(log["blockNumber"], 16)

                    await process_event(log)

                    if block_num > last_processed:
                        last_processed = block_num

                        # Persist progress
                        db = SessionLocal()
                        try:
                            repo = SyncStateRepository(db)
                            repo.update_last_block(last_processed)
                        finally:
                            db.close()

        except Exception as e:
            logger.error(f"WebSocket error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)