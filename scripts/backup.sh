#!/bin/bash
set -e

# Load environment variables
source .env.prod

# Backup directory
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"

# Create backup
echo "Creating backup..."
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ${DB_USER} -d ${DB_NAME} > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

echo "Backup completed: ${BACKUP_FILE}.gz" 