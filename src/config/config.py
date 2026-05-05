import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

_CONFIG_DIR = Path(__file__).resolve().parent  # .../src/config/

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:lenovoubuntuu@localhost/dapp_db")
    
    # Blockchain
    RPC_URL: str = os.getenv("RPC_URL", "ws://localhost:8545")  # WebSocket for events
    HTTP_RPC_URL: str = os.getenv("HTTP_RPC_URL", "http://localhost:8545")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "31337"))  # Anvil default
    
    # App
    APP_NAME: str = "BloCharity"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Voting
    VOTE_THRESHOLD_PERCENT: int = int(os.getenv("VOTE_THRESHOLD_PERCENT", "50"))
    
    # Lottery (cron)
    LOTTERY_INTERVAL_HOURS: int = int(os.getenv("LOTTERY_INTERVAL_HOURS", "24"))
    
    # Paths — resolve relative to this file so it works from any cwd
    ABI_PATH: str = str(_CONFIG_DIR / "abi.json")
    
    # Owner keys (for blockchain service)
    OWNER_ADDRESS: str = os.getenv("OWNER_ADDRESS", "")
    OWNER_PRIVATE_KEY: str = os.getenv("OWNER_PRIVATE_KEY", "")

settings = Settings()