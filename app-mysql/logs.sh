#!/bin/bash
# View logs for Investment Dashboard

DAYS_BACK=${1:-7}

echo "=================================="
echo "Investment Dashboard - Logs"
echo "=================================="
echo ""
echo "📋 Last $DAYS_BACK days of logs:"
echo ""

# If using systemd service
if command -v systemctl &> /dev/null && systemctl is-active --quiet investment-dashboard.service; then
    echo "--- Systemd Service Logs ---"
    journalctl -u investment-dashboard.service --since "$DAYS_BACK days ago" -f
else
    # If using Docker Compose
    echo "--- Docker Compose Logs ---"
    docker-compose logs -f --tail=100
fi
