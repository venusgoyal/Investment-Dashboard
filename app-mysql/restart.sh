#!/bin/bash
# Restart script for Investment Dashboard

echo "🔄 Restarting Investment Dashboard..."

# If using systemd service
if command -v systemctl &> /dev/null; then
    echo "Using systemd service..."
    sudo systemctl restart investment-dashboard.service
    echo "✅ Service restarted"
    systemctl status investment-dashboard.service --no-pager
else
    # If using Docker Compose directly
    echo "Using Docker Compose..."
    docker-compose down
    docker-compose up -d
    echo "✅ Containers restarted"
    docker-compose ps
fi

echo ""
echo "🔗 Application available at: http://localhost:8501"
