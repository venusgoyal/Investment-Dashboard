#!/bin/bash

# Investment Dashboard - Update Script
# Usage: bash update.sh

set -e

echo "======================================"
echo "Updating Investment Dashboard"
echo "======================================"

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Stop service
echo "Stopping service..."
sudo systemctl stop investment-dashboard

# Rebuild image
echo "Rebuilding Docker image..."
docker build -t investment-dashboard:latest .

# Start service
echo "Starting service..."
sudo systemctl start investment-dashboard

# Wait for startup
sleep 10

# Verify
echo ""
echo "======================================"
if sudo systemctl is-active --quiet investment-dashboard; then
    echo "✓ Update completed successfully"
else
    echo "✗ Service failed to start after update"
    echo "Rolling back..."
    git revert HEAD --no-edit
    docker build -t investment-dashboard:latest .
    sudo systemctl start investment-dashboard
fi
echo "======================================"
