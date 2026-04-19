import asyncio
import json
import websockets
from core.config import settings
from listeners.event_processor import process_event
import logging

logger = logging.getLogger(__name__)

async def listen_to_contract_events():
    """Background task: connects WebSocket and forwards events to processor"""
    uri = settings.RPC_URL  # ws://localhost:8545
    while True:
        try:
            async with websockets.connect(uri) as ws:
                # Subscribe to all contract logs
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
                    if "params" in data:
                        await process_event(data["params"]["result"])
        except Exception as e:
            logger.error(f"WebSocket error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)