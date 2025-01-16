#!/bin/bash

# Print environment variables (excluding sensitive data)
echo "Environment variables:"
echo "PORT: $PORT"
echo "API_URL: $REACT_APP_API_URL"

# Replace $PORT in nginx config
echo "Configuring Nginx to listen on port $PORT..."
sed -i "s/\$PORT/$PORT/g" /etc/nginx/conf.d/default.conf

# Test nginx config
echo "Testing Nginx configuration..."
nginx -t

# Start Nginx
echo "Starting Nginx..."
exec nginx -g "daemon off;" 