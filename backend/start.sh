#!/bin/bash

# Set production environment
export ENV=prod

# Print environment variables (excluding sensitive data)
echo "Environment variables:"
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL:0:25}..." # Only show first 25 chars
echo "CORS_ORIGINS: $CORS_ORIGINS"

# Extract database host and port from DATABASE_URL
if [[ $DATABASE_URL =~ [@]([^:]+)[:]([0-9]+)[/] ]]; then
    DB_HOST="${BASH_REMATCH[1]}"
    DB_PORT="${BASH_REMATCH[2]}"
    echo "Extracted database connection info:"
    echo "DB_HOST: $DB_HOST"
    echo "DB_PORT: $DB_PORT"
else
    echo "Failed to extract database host and port from DATABASE_URL"
    exit 1
fi

# Test database connection
echo "Testing database connection..."
python << END
import sys
import psycopg2
from urllib.parse import urlparse

db_url = "$DATABASE_URL"
print(f"Parsing DATABASE_URL: {db_url[:25]}...")

try:
    result = urlparse(db_url)
    print(f"Host: {result.hostname}")
    print(f"Port: {result.port}")
    print(f"Database: {result.path[1:]}")  # Remove leading slash
    
    conn = psycopg2.connect(db_url)
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {str(e)}")
    sys.exit(1)
END

# Add PostgreSQL health check
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT"; then
        echo "PostgreSQL is ready!"
        break
    fi
    
    echo "Waiting for PostgreSQL... attempt $i of 30"
    sleep 2
done

# Start Gunicorn with monitoring
echo "Starting Gunicorn..."

gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:$PORT \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120 \
    --graceful-timeout 60 \
    --keep-alive 5 \
    --log-file=- \
    --preload 