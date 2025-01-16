#!/bin/bash

export ENV=prod
# Print environment variables (excluding sensitive data)
echo "Environment variables:"
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL:0:25}..." # Only show first 25 chars
echo "CORS_ORIGINS: $CORS_ORIGINS"

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

# Start Gunicorn
echo "Starting Gunicorn..."

exec gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT 