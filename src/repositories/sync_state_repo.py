from sqlalchemy.orm import Session
from models.sync_state import SyncState
from repositories.base import BaseRepository

class SyncStateRepository(BaseRepository[SyncState]):
    def __init__(self, db_session: Session):
        super().__init__(SyncState, db_session)

    def get_last_block(self) -> int:
        """Return last processed block number, or 0 if no state exists."""
        state = self.get(1)
        return state.last_processed_block if state else 0

    def update_last_block(self, block_number: int) -> None:
        """Update or create the sync state with the latest block."""
        state = self.get(1)
        if state:
            self.update(1, last_processed_block=block_number)
        else:
            self.create(id=1, last_processed_block=block_number)