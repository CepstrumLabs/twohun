#!/bin/bash

# Configuration
BACKUP_DIR="/path/to/backups"
DB_USER="your_user"
DB_NAME="your_db"
RETENTION_DAYS=30

# Create backup
BACKUP_FILE="${BACKUP_DIR}/backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U ${DB_USER} -d ${DB_NAME} > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

# Delete old backups
find ${BACKUP_DIR} -type f -mtime +${RETENTION_DAYS} -delete
