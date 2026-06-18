#!/bin/bash

# Database configuration — read from environment or .env file
# Usage: source ../src/.env && bash clear_db.sh

if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set. Source your .env file first:"
    echo "  source src/.env && bash src/scripts/clear_db.sh"
    exit 1
fi

# Parse DATABASE_URL: postgresql://user:pass@host/dbname
DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

echo "--- Clearing Database: $DB_NAME @ $DB_HOST ---"

# We use PGPASSWORD to avoid interactive prompt
export PGPASSWORD=$DB_PASS

psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "
BEGIN;
DELETE FROM votes;
DELETE FROM proofs;
DELETE FROM donations;
DELETE FROM lottery_winners;
DELETE FROM campaigns;
DELETE FROM sync_state;
DELETE FROM system_events;

-- Reset sequence for campaigns
SELECT setval(pg_get_serial_sequence('campaigns', 'id'), 1, false);

COMMIT;
"

if [ $? -eq 0 ]; then
    echo "Successfully cleared: votes, proofs, donations, lottery_winners, campaigns, sync_state, and system_events."
    echo "Campaign ID sequence reset to 1."
else
    echo "Error occurred while clearing the database."
    exit 1
fi
