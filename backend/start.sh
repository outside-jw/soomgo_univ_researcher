#!/bin/bash

# Railway startup script
echo "Starting CPS Scaffolding Agent..."

# Run database migrations
echo "Running database migrations..."
python -c "from app.db.migrations import migrate_add_turn_tracking_columns; migrate_add_turn_tracking_columns()"

if [ $? -ne 0 ]; then
    echo "Migration failed, but continuing..."
fi

# Start the application
echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
