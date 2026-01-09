#!/usr/bin/env bash
# Build script for Render deployment

echo "Building Wiki Quiz Generator..."

# Navigate to backend directory
cd backend

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
