#!/usr/bin/env bash
# Start script for Render deployment

echo "Starting Wiki Quiz Generator API..."

# Navigate to backend directory
cd backend

# Run the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
