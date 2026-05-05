#!/bin/bash

# Database configuration
DB_NAME="dapp_db"
DB_USER="postgres"
DB_PASS="lenovoubuntuu"

echo "--- Clearing Database Logic ---"

# We use PGPASSWORD to avoid interactive prompt
export PGPASSWORD=$DB_PASS

psql -U $DB_USER -d $DB_NAME -c "
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
