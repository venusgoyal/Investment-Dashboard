#!/bin/bash

# Investment Dashboard - One-Step Deployment Script for EC2
# Usage: bash deploy.sh

set -e

echo "======================================"
echo "Investment Dashboard - EC2 Deployment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    print_error "This script is designed for Ubuntu. Please adjust for your OS."
    exit 1
fi

print_info "Starting deployment process..."

# Step 1: Update system
print_info "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install Docker
print_info "Installing Docker..."
sudo apt-get install -y docker.io

# Add user to docker group
sudo usermod -aG docker $USER
print_info "Added $USER to docker group"

# Step 3: Create application directory
print_info "Creating application directory..."
sudo mkdir -p /opt/Investment-Dashboard
sudo chown -R $USER:$USER /opt/Investment-Dashboard

# Step 4: Clone or copy application
print_info "Please ensure the Investment-Dashboard code is in /opt/Investment-Dashboard"
print_warning "If code is not there, clone it now: git clone <repo-url> /opt/Investment-Dashboard"

if [ ! -f "/opt/Investment-Dashboard/Dockerfile" ]; then
    print_error "Dockerfile not found in /opt/Investment-Dashboard"
    print_warning "Please copy the project files to /opt/Investment-Dashboard and run this script again"
    exit 1
fi

# Step 5: Build Docker image
print_info "Building Docker image..."
cd /opt/Investment-Dashboard
docker build -t investment-dashboard:latest .

# Step 6: Create .env file
print_info "Creating environment file..."
print_warning "Enter your AWS credentials when prompted"

echo ""
read -p "AWS Access Key ID: " AWS_KEY_ID
read -sp "AWS Secret Access Key: " AWS_SECRET
echo ""
read -p "AWS Region (default: ap-south-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-ap-south-1}

# Write .env file
sudo tee /opt/Investment-Dashboard/.env > /dev/null << EOF
AWS_ACCESS_KEY_ID=$AWS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET
AWS_REGION=$AWS_REGION
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

print_info "Environment file created"

# Step 7: Copy systemd service file
print_info "Creating systemd service..."
sudo cp /opt/Investment-Dashboard/investment-dashboard.service /etc/systemd/system/

# Replace username in service file if different from ubuntu
if [ "$USER" != "ubuntu" ]; then
    sudo sed -i "s/User=ubuntu/User=$USER/" /etc/systemd/system/investment-dashboard.service
    print_info "Updated service file for user: $USER"
fi

# Step 8: Enable and start service
print_info "Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable investment-dashboard
sudo systemctl start investment-dashboard

# Step 9: Verify service
sleep 5
print_info "Verifying service status..."
if sudo systemctl is-active --quiet investment-dashboard; then
    print_info "Service is running successfully!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u investment-dashboard -f"
    exit 1
fi

# Step 10: Get EC2 IP
EC2_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "======================================"
echo -e "${GREEN}Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "Access your application at:"
echo -e "${GREEN}http://$EC2_IP:8501${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:        sudo journalctl -u investment-dashboard -f"
echo "  Service status:   sudo systemctl status investment-dashboard"
echo "  Restart service:  sudo systemctl restart investment-dashboard"
echo "  Stop service:     sudo systemctl stop investment-dashboard"
echo ""
print_info "The service will auto-start on system reboot"
echo ""
