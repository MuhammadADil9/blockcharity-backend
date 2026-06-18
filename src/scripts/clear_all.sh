#!/bin/bash

# Removes ALL data including campaigns, donations, votes, proofs, users, and notifications.
# Usage: source src/.env && bash src/scripts/clear_all.sh

if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set. Source your .env file first:"
    echo "  source src/.env && bash src/scripts/clear_all.sh"
    exit 1
fi

DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

echo "--- Full Database Wipe: $DB_NAME @ $DB_HOST ---"

export PGPASSWORD=$DB_PASS

psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "
BEGIN;
DELETE FROM notifications;
DELETE FROM votes;
DELETE FROM proofs;
DELETE FROM donations;
DELETE FROM lottery_winners;
DELETE FROM campaigns;
DELETE FROM sync_state;
DELETE FROM system_events;
DELETE FROM donors;
DELETE FROM distributors;

SELECT setval(pg_get_serial_sequence('campaigns', 'id'), 1, false);
SELECT setval(pg_get_serial_sequence('notifications', 'id'), 1, false);

COMMIT;
"

if [ $? -eq 0 ]; then
    echo "Successfully cleared all tables: notifications, votes, proofs, donations, lottery_winners, campaigns, sync_state, system_events, donors, distributors."
    echo "Sequences reset to 1."
else
    echo "Error occurred during full wipe."
    exit 1
fi
