
USDT_DECIMALS = 2

def from_units(amount: int) -> float:
    """Convert from on-chain units (e.g., 2500) to USDT (25.0)"""
    return amount / (10 ** USDT_DECIMALS)

def to_units(amount: float) -> int:
    """Convert from USDT (25.0) to on-chain units (2500)"""
    return int(amount * (10 ** USDT_DECIMALS))