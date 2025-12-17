#!/bin/bash
# MySQL Investment Dashboard - Deployment Script for EC2

set -e

echo "=================================="
echo "Investment Dashboard - EC2 Setup"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y docker.io docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Create application directory
echo "📁 Creating application directory..."
mkdir -p ~/investment-dashboard
cd ~/investment-dashboard

# Copy application files
echo "📋 Copying application files..."
# Note: Replace with your actual source
# scp -r local_path ubuntu@ec2_instance:/home/ubuntu/investment-dashboard/

# Create systemd service file
echo "🚀 Creating systemd service..."
sudo tee /etc/systemd/system/investment-dashboard.service > /dev/null <<EOF
[Unit]
Description=Investment Dashboard Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/investment-dashboard
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "⚙️  Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable investment-dashboard.service
sudo systemctl start investment-dashboard.service

# Verify service status
echo ""
echo "✅ Service Status:"
sudo systemctl status investment-dashboard.service --no-pager

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "🔗 Access the application at: http://<ec2-instance-ip>:8501"
echo ""
echo "📝 Useful commands:"
echo "   View logs:       journalctl -u investment-dashboard.service -f"
echo "   Stop service:    sudo systemctl stop investment-dashboard.service"
echo "   Start service:   sudo systemctl start investment-dashboard.service"
echo "   Restart service: sudo systemctl restart investment-dashboard.service"
echo ""
