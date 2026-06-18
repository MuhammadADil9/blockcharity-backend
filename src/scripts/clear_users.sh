#!/bin/bash

# Removes only donor and distributor records.
# Usage: source src/.env && bash src/scripts/clear_users.sh

if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set. Source your .env file first:"
    echo "  source src/.env && bash src/scripts/clear_users.sh"
    exit 1
fi

DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

echo "--- Clearing Users: $DB_NAME @ $DB_HOST ---"

export PGPASSWORD=$DB_PASS

psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "
BEGIN;
DELETE FROM donors;
DELETE FROM distributors;
COMMIT;
"

if [ $? -eq 0 ]; then
    echo "Successfully cleared: donors and distributors."
else
    echo "Error occurred while clearing users."
    exit 1
fi
