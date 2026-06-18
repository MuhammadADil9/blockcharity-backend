import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env relative to this file so it works regardless of cwd
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_CONFIG_DIR = Path(__file__).resolve().parent  # .../src/config/


def _require_env(key: str) -> str:
    """Return env var value or raise if missing/empty."""
    value = os.getenv(key, "")
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set.")
    return value


class Settings:
    # Database
    DATABASE_URL: str = _require_env("DATABASE_URL")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # Blockchain
    RPC_URL: str = _require_env("RPC_URL")          # WebSocket for events
    HTTP_RPC_URL: str = _require_env("HTTP_RPC_URL")
    CONTRACT_ADDRESS: str = _require_env("CONTRACT_ADDRESS")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "31337"))  # Anvil default

    # App
    APP_NAME: str = "BloCharity"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    # Voting
    VOTE_THRESHOLD_PERCENT: int = int(os.getenv("VOTE_THRESHOLD_PERCENT", "50"))

    # Lottery (cron)
    LOTTERY_INTERVAL_HOURS: int = int(os.getenv("LOTTERY_INTERVAL_HOURS", "24"))

    # Paths — resolve relative to this file so it works from any cwd
    ABI_PATH: str = str(_CONFIG_DIR / "abi.json")

    # Owner keys (for blockchain service)
    OWNER_ADDRESS: str = os.getenv("OWNER_ADDRESS", "")
    OWNER_PRIVATE_KEY: str = os.getenv("OWNER_PRIVATE_KEY", "")

    # IPFS (Pinata)
    PINATA_API_KEY: str = os.getenv("PINATA_API_KEY", "")
    PINATA_API_SECRET: str = os.getenv("PINATA_API_SECRET", "")
    PINATA_JWT: str = os.getenv("PINATA_JWT", "")

    # Transaction config
    GAS_LIMIT: int = int(os.getenv("GAS_LIMIT", "500000"))

    # OpenAI (chatbot)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()