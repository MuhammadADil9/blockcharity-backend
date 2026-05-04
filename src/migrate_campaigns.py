from config.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS proof_deadline TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS voting_deadline TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS activity_status INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS positive_votes INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS negative_votes INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS total_voters INTEGER DEFAULT 0;"))
            conn.commit()
            print("Successfully added columns to campaigns table.")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    run_migration()
