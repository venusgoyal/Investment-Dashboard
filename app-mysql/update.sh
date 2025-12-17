#!/bin/bash
# Update script for Investment Dashboard

echo "🔄 Updating Investment Dashboard..."

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Restart service
if command -v systemctl &> /dev/null; then
    echo "🚀 Restarting service..."
    sudo systemctl restart investment-dashboard.service
    systemctl status investment-dashboard.service --no-pager
else
    echo "🚀 Restarting containers..."
    docker-compose down
    docker-compose up -d
    docker-compose ps
fi

echo ""
echo "✅ Update complete!"
