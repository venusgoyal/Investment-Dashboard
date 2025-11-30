# Investment Dashboard - Docker Build & Deployment Guide

## Docker Setup

### Build the Docker Image

```bash
cd Investment-Dashboard

# Build the image
docker build -t investment-dashboard:latest .

# Verify the image
docker images | grep investment-dashboard
```

### Run Locally (Optional Testing)

```bash
# With AWS credentials from environment
docker run -it \
  -p 8501:8501 \
  -e AWS_ACCESS_KEY_ID=your-key-id \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  -e AWS_REGION=ap-south-1 \
  investment-dashboard:latest

# Or mount AWS credentials file
docker run -it \
  -p 8501:8501 \
  -v ~/.aws:/root/.aws \
  -e AWS_REGION=ap-south-1 \
  investment-dashboard:latest
```

### Push to Docker Registry (Optional)

```bash
# Tag for ECR
docker tag investment-dashboard:latest 123456789012.dkr.ecr.ap-south-1.amazonaws.com/investment-dashboard:latest

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com

# Push image
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/investment-dashboard:latest
```

---

## EC2 Deployment with Auto-Start

### Step 1: Create EC2 Instance

1. Go to AWS EC2 Dashboard
2. Click "Launch Instances"
3. Select: **Ubuntu 22.04 LTS** (AMI)
4. Instance Type: **t3.medium** or higher (for smooth performance)
5. Configure Security Group:
   - Allow SSH (22) from your IP
   - Allow Custom TCP 8501 from 0.0.0.0/0
6. Key Pair: Create or select existing
7. Storage: 20GB minimum
8. Attach IAM Role with DynamoDB permissions
9. Launch instance

### Step 2: Connect to EC2 Instance

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-ec2-public-ip

# For Ubuntu AMI (not Amazon Linux)
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Install Docker

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker --version
```

### Step 4: Clone/Copy Application

**Option A: Clone from Git**
```bash
cd /opt
sudo git clone https://github.com/your-repo/Investment-Dashboard.git
sudo chown -R $USER:$USER Investment-Dashboard
```

**Option B: Copy from Local**
```bash
# From local machine
scp -i your-key.pem -r Investment-Dashboard ubuntu@your-ec2-ip:/opt/

# SSH and set permissions
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo chown -R ubuntu:ubuntu /opt/Investment-Dashboard
```

### Step 5: Build Docker Image on EC2

```bash
cd /opt/Investment-Dashboard
docker build -t investment-dashboard:latest .

# Verify
docker images
```

### Step 6: Configure Environment Variables

Create environment file for Docker:

```bash
# Create .env file
sudo nano /opt/Investment-Dashboard/.env
```

Add the following:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

Save with Ctrl+X, then Y, then Enter.

### Step 7: Create Systemd Service for Auto-Start

Create service file:

```bash
sudo nano /etc/systemd/system/investment-dashboard.service
```

Paste the following content:

```ini
[Unit]
Description=Investment Dashboard Streamlit Application
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/Investment-Dashboard
EnvironmentFile=/opt/Investment-Dashboard/.env
Restart=always
RestartSec=10
TimeoutStartSec=60

# Stop old container if it exists
ExecStartPre=/bin/bash -c 'docker stop investment-dashboard || true'
ExecStartPre=/bin/bash -c 'docker rm investment-dashboard || true'

# Start container
ExecStart=/usr/bin/docker run --name investment-dashboard \
  --env-file /opt/Investment-Dashboard/.env \
  -p 8501:8501 \
  -v /opt/Investment-Dashboard:/app \
  --restart unless-stopped \
  investment-dashboard:latest

# Stop container
ExecStop=/usr/bin/docker stop investment-dashboard

[Install]
WantedBy=multi-user.target
```

### Step 8: Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service (auto-start on reboot)
sudo systemctl enable investment-dashboard

# Start the service
sudo systemctl start investment-dashboard

# Verify service is running
sudo systemctl status investment-dashboard

# View logs
sudo journalctl -u investment-dashboard -f
```

### Step 9: Verify Application

```bash
# Check container is running
docker ps | grep investment-dashboard

# View application logs
docker logs -f investment-dashboard

# Test endpoint
curl -I http://localhost:8501
```

### Step 10: Access Application

Open browser to:
```
http://your-ec2-public-ip:8501
```

---

## Docker Compose Alternative (Recommended for Production)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  investment-dashboard:
    build: .
    container_name: investment-dashboard
    ports:
      - "8501:8501"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=ap-south-1
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./App:/app
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Using Docker Compose

```bash
# On EC2, install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create .env file
cat > /opt/Investment-Dashboard/.env << EOF
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=ap-south-1
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Service Management Commands

### Start Service
```bash
sudo systemctl start investment-dashboard
```

### Stop Service
```bash
sudo systemctl stop investment-dashboard
```

### Restart Service
```bash
sudo systemctl restart investment-dashboard
```

### Check Status
```bash
sudo systemctl status investment-dashboard
```

### View Logs
```bash
sudo journalctl -u investment-dashboard -f
sudo journalctl -u investment-dashboard --no-pager | tail -100
```

### Disable Auto-Start
```bash
sudo systemctl disable investment-dashboard
```

### Re-Enable Auto-Start
```bash
sudo systemctl enable investment-dashboard
```

---

## Updating Application

### Pull Latest Changes
```bash
cd /opt/Investment-Dashboard
git pull origin main
```

### Rebuild Image
```bash
docker build -t investment-dashboard:latest .
```

### Restart Service
```bash
sudo systemctl restart investment-dashboard
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check service logs
sudo journalctl -u investment-dashboard -n 50

# Check Docker logs
docker logs investment-dashboard

# Check if port 8501 is in use
sudo lsof -i :8501
```

### Container Crashes
```bash
# View container logs
docker logs -f investment-dashboard

# Check exit code
docker inspect investment-dashboard | grep -A 5 "State"

# Run container interactively for debugging
docker run -it --env-file .env investment-dashboard:latest /bin/bash
```

### AWS Credentials Error
```bash
# Verify environment file
cat /opt/Investment-Dashboard/.env

# Check if credentials are correctly set in container
docker exec investment-dashboard env | grep AWS

# Verify DynamoDB access
docker exec investment-dashboard aws dynamodb list-tables --region ap-south-1
```

### Port Already in Use
```bash
# Find process using port 8501
sudo netstat -tulpn | grep 8501

# Kill process if needed
sudo kill -9 <PID>

# Or change port in docker service file
```

---

## Monitoring & Logs

### System Logs
```bash
# Real-time logs
sudo journalctl -u investment-dashboard -f

# Last 100 lines
sudo journalctl -u investment-dashboard -n 100

# Last hour
sudo journalctl -u investment-dashboard --since "1 hour ago"
```

### Docker Logs
```bash
# Real-time
docker logs -f investment-dashboard

# Last 50 lines
docker logs --tail 50 investment-dashboard

# With timestamps
docker logs -t investment-dashboard
```

### Container Stats
```bash
# Memory and CPU usage
docker stats investment-dashboard

# Resource limits
docker inspect investment-dashboard | grep -A 10 "HostConfig"
```

---

## Production Best Practices

### 1. Use IAM Role Instead of Hard-Coded Credentials
Instead of .env file, attach IAM role to EC2:

```bash
# Edit service file to remove EnvironmentFile
# EC2 will automatically use the IAM role credentials
```

### 2. Use Secrets Manager for Sensitive Data

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret --name investment-dashboard-config \
  --secret-string '{"aws_access_key_id":"...","aws_secret_access_key":"..."}'
```

### 3. Set Resource Limits in Systemd

```ini
[Service]
# Add these lines to service file
MemoryLimit=1G
CPUQuota=50%
```

### 4. Enable CloudWatch Logging

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

### 5. Use HTTPS with Reverse Proxy

```bash
# Install nginx
sudo apt-get install -y nginx

# Configure nginx as reverse proxy
sudo nano /etc/nginx/sites-available/default
```

Add:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. Enable Auto-Restart on Failure

Already included in service file with:
```ini
Restart=always
RestartSec=10
```

### 7. Enable Log Rotation

```bash
sudo nano /etc/logrotate.d/investment-dashboard
```

Add:
```
/var/log/investment-dashboard.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
```

---

## Cleanup & Uninstall

### Stop and Disable Service
```bash
sudo systemctl stop investment-dashboard
sudo systemctl disable investment-dashboard
```

### Remove Service File
```bash
sudo rm /etc/systemd/system/investment-dashboard.service
sudo systemctl daemon-reload
```

### Remove Docker Image
```bash
docker rmi investment-dashboard:latest
```

### Remove Application
```bash
sudo rm -rf /opt/Investment-Dashboard
```

---

## Quick Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
newgrp docker

# Clone application
cd /opt
sudo git clone <your-repo-url> Investment-Dashboard
sudo chown -R $USER:$USER Investment-Dashboard

# Build image
cd Investment-Dashboard
docker build -t investment-dashboard:latest .

# Create .env file
sudo tee /opt/Investment-Dashboard/.env > /dev/null << EOF
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_REGION=ap-south-1
EOF

# Create systemd service (content in next section)
sudo tee /etc/systemd/system/investment-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Investment Dashboard Streamlit Application
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/Investment-Dashboard
EnvironmentFile=/opt/Investment-Dashboard/.env
Restart=always
RestartSec=10
ExecStartPre=/bin/bash -c 'docker stop investment-dashboard || true'
ExecStartPre=/bin/bash -c 'docker rm investment-dashboard || true'
ExecStart=/usr/bin/docker run --name investment-dashboard \
  --env-file /opt/Investment-Dashboard/.env \
  -p 8501:8501 \
  --restart unless-stopped \
  investment-dashboard:latest
ExecStop=/usr/bin/docker stop investment-dashboard

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable investment-dashboard
sudo systemctl start investment-dashboard

echo "Deployment complete! Access at http://$(hostname -I):8501"
```

Run the script:
```bash
bash deploy.sh
```

---

## Summary

✅ Dockerfile created for containerization  
✅ Docker Compose alternative available  
✅ Systemd service for auto-start on EC2  
✅ Comprehensive deployment guide  
✅ Troubleshooting steps included  
✅ Production best practices documented  
✅ Quick deployment script provided  

Application will now:
- Start automatically when EC2 instance starts
- Restart automatically if it crashes
- Persist across reboots
- Be easily manageable with systemctl commands
