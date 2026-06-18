from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from config.config import settings
from config.database import engine, Base
# Import all models so their tables are registered with Base
from models.donor import Donor
from models.distributor import Distributor
from models.campaign import Campaign
from models.donation import Donation
from models.vote import Vote
from models.proof import Proof
from models.lottery_winner import LotteryWinner
from models.sync_state import SyncState

from api.routers import users, campaigns, profile, rankings, analytics
from listeners.websocket_listener import listen_to_contract_events
from services.timer_service import TimerService

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the blockchain event listener as a background task
    logger.info("Starting blockchain event listener...")
    listener_task = asyncio.create_task(listen_to_contract_events())
    
    # Startup: launch the timer service
    logger.info("Starting TimerService...")
    timer_service = TimerService()
    await timer_service.start()
    
    yield
    # Shutdown: cancel the listener
    listener_task.cancel()
    # Shutdown: stop timer service
    timer_service.running = False
    
    try:
        await listener_task
    except asyncio.CancelledError:
        logger.info("Blockchain event listener stopped.")

app = FastAPI(title="Charity Dapp", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(campaigns.router)
app.include_router(profile.router)
app.include_router(rankings.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"status": "active", "message": "Charity Dapp Backend is Running"}
