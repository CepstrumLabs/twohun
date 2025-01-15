#!/bin/bash
set -e

# Load environment variables
source .env.prod

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

BACKUP_FILE=$1

# 1. Stop application
echo "Stopping application..."
docker-compose -f docker-compose.prod.yml down

# 2. Verify backup integrity
echo "Verifying backup..."
gunzip -t "${BACKUP_FILE}"

# 3. Restore backup
echo "Restoring backup..."
gunzip -c "${BACKUP_FILE}" | docker-compose -f docker-compose.prod.yml exec -T db psql -U ${DB_USER} -d ${DB_NAME}

# 4. Start application
echo "Starting application..."
docker-compose -f docker-compose.prod.yml up -d

echo "Restore completed!" 