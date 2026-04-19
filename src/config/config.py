import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:lenovoubuntuu@localhost/dapp_db")
    
    # Blockchain
    RPC_URL: str = os.getenv("RPC_URL", "ws://localhost:8545")  # WebSocket for events
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "31337"))  # Anvil default
    
    # App
    APP_NAME: str = "BloCharity"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Voting
    VOTE_THRESHOLD_PERCENT: int = int(os.getenv("VOTE_THRESHOLD_PERCENT", "50"))
    
    # Lottery (cron)
    LOTTERY_INTERVAL_HOURS: int = int(os.getenv("LOTTERY_INTERVAL_HOURS", "24"))
    
    # Paths
    ABI_PATH: str = os.getenv("ABI_PATH", "abi.json")

settings = Settings()