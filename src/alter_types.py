from config.database import engine
from sqlalchemy import text

def alter_numeric_columns():
    with engine.connect() as conn:
        try:
            # campaigns table
            conn.execute(text("ALTER TABLE campaigns ALTER COLUMN milestone_amount TYPE NUMERIC(78,0) USING milestone_amount::numeric;"))
            conn.execute(text("ALTER TABLE campaigns ALTER COLUMN current_amount TYPE NUMERIC(78,0) USING current_amount::numeric;"))
            
            # donations table
            conn.execute(text("ALTER TABLE donations ALTER COLUMN amount TYPE NUMERIC(78,0) USING amount::numeric;"))
            
            # donors table
            conn.execute(text("ALTER TABLE donors ALTER COLUMN total_donated_wei TYPE NUMERIC(78,0) USING total_donated_wei::numeric;"))
            
            conn.commit()
            print("Successfully converted VARCHAR columns to NUMERIC(78,0).")
        except Exception as e:
            print("Error converting columns:", e)

if __name__ == "__main__":
    alter_numeric_columns()
