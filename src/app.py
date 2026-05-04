from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
# Import all models so their tables are registered with Base
from models.donor import Donor
from models.distributor import Distributor
from models.campaign import Campaign
from models.donation import Donation
from models.vote import Vote
from models.proof import Proof
from models.lottery_winner import LotteryWinner

from api.routers import users, campaigns, profile, rankings, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Charity Dapp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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




