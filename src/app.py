from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import database
from .models import models
from .routers import users, campaigns, profile

models.Base.metadata.create_all(bind=database.engine)

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

@app.get("/")
def read_root():
    return {"status": "active", "message": "Charity Dapp Backend is Running"}




