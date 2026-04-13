#!/bin/bash
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the passed command
echo "Starting application..."
exec "$@"
