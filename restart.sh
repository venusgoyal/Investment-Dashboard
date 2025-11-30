#!/bin/bash

# Investment Dashboard - Restart Script
# Usage: bash restart.sh

echo "======================================"
echo "Restarting Investment Dashboard"
echo "======================================"

# Option 1: Restart via systemd (Recommended)
echo "Stopping service..."
sudo systemctl stop investment-dashboard

echo "Waiting for graceful shutdown..."
sleep 5

echo "Starting service..."
sudo systemctl start investment-dashboard

echo "Waiting for application to be ready..."
sleep 10

# Check status
echo ""
echo "======================================"
if sudo systemctl is-active --quiet investment-dashboard; then
    echo "✓ Service restarted successfully"
    echo ""
    echo "Service Status:"
    sudo systemctl status investment-dashboard --no-pager
else
    echo "✗ Service failed to start"
    echo ""
    echo "Recent logs:"
    sudo journalctl -u investment-dashboard -n 30 --no-pager
fi
echo "======================================"

# Optional: Show application logs
echo ""
read -p "View application logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker logs -f investment-dashboard
fi
