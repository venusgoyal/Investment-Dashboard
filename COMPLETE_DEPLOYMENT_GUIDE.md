# Investment Dashboard - Complete Docker & EC2 Deployment Guide

## 📦 What's Included

This package contains everything needed to deploy the Investment Dashboard on EC2:

| File | Purpose |
|------|---------|
| **Dockerfile** | Container image definition |
| **docker-compose.yml** | Multi-container orchestration (alternative) |
| **investment-dashboard.service** | Systemd service for auto-start |
| **deploy.sh** | One-step deployment script |
| **health-check.sh** | System health verification |
| **restart.sh** | Safe service restart |
| **update.sh** | Application update script |
| **logs.sh** | Log viewer utility |
| **DOCKER_DEPLOYMENT.md** | Detailed deployment documentation |
| **EC2_QUICK_REFERENCE.md** | Quick reference guide |

---

## 🚀 Quick Start (3 Steps)

### Step 1: Launch EC2 Instance

```bash
# Use AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key \
  --security-groups investment-dashboard \
  --region ap-south-1
```

Or use AWS Console:
- Image: Ubuntu 22.04 LTS
- Instance Type: t3.medium
- Storage: 20GB

### Step 2: Configure Security Group

```bash
# Allow SSH
aws ec2 authorize-security-group-ingress \
  --group-name investment-dashboard \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region ap-south-1

# Allow Port 8501
aws ec2 authorize-security-group-ingress \
  --group-name investment-dashboard \
  --protocol tcp \
  --port 8501 \
  --cidr 0.0.0.0/0 \
  --region ap-south-1
```

### Step 3: Deploy

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone and deploy
git clone https://github.com/your-repo/Investment-Dashboard.git
cd Investment-Dashboard
chmod +x deploy.sh
./deploy.sh
```

Done! Application is running at `http://your-ec2-ip:8501`

---

## 🔧 Setting Up IAM Role (Recommended for Production)

Instead of hardcoded credentials, use IAM role:

### Step 1: Create IAM Policy

```bash
# Create policy file: investment-dashboard-policy.json
cat > investment-dashboard-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:*:table/Investment"
    }
  ]
}
EOF

# Create policy
aws iam create-policy \
  --policy-name InvestmentDashboardPolicy \
  --policy-document file://investment-dashboard-policy.json
```

### Step 2: Create IAM Role

```bash
# Create role trust file: trust-policy.json
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name InvestmentDashboardRole \
  --assume-role-policy-document file://trust-policy.json
```

### Step 3: Attach Policy to Role

```bash
aws iam attach-role-policy \
  --role-name InvestmentDashboardRole \
  --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/InvestmentDashboardPolicy
```

### Step 4: Create Instance Profile

```bash
# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name InvestmentDashboardProfile

# Add role to profile
aws iam add-role-to-instance-profile \
  --instance-profile-name InvestmentDashboardProfile \
  --role-name InvestmentDashboardRole
```

### Step 5: Attach to EC2 Instance

```bash
aws ec2 associate-iam-instance-profile \
  --iam-instance-profile Name=InvestmentDashboardProfile \
  --instance-id i-1234567890abcdef0 \
  --region ap-south-1
```

### Step 6: Update Deployment

Edit `.env` file to remove credentials:

```bash
# Remove these lines from .env
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# Keep only
AWS_REGION=ap-south-1
```

---

## 📊 Dockerfile Explanation

```dockerfile
FROM python:3.11-slim
```
- Lightweight Python image (390MB vs 950MB for full image)

```dockerfile
WORKDIR /app
```
- Set working directory inside container

```dockerfile
ENV PYTHONUNBUFFERED=1
```
- Ensure Python output is logged immediately

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends gcc
```
- Install build tools for compiled dependencies

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
- Install Python packages without caching

```dockerfile
COPY App/app.py .
COPY App/dynamodb_service.py .
```
- Copy application files

```dockerfile
HEALTHCHECK CMD python -c "import urllib.request; ..."
```
- Container health check every 30 seconds

---

## 🐳 Docker Images

### Build Image
```bash
docker build -t investment-dashboard:latest .
```

### Image Details
```bash
docker image inspect investment-dashboard:latest
docker image history investment-dashboard:latest
```

### Push to Registry
```bash
# Tag for ECR
docker tag investment-dashboard:latest \
  123456789012.dkr.ecr.ap-south-1.amazonaws.com/investment-dashboard:latest

# Login to ECR
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.ap-south-1.amazonaws.com

# Push
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/investment-dashboard:latest
```

---

## 🔄 Systemd Service Deep Dive

### Service File Breakdown

```ini
[Unit]
Description=Investment Dashboard Streamlit Application
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service
```
- Runs after network and Docker are ready
- Requires Docker to be running

```ini
[Service]
Type=simple
User=ubuntu
Restart=always
RestartSec=10
```
- Simple service (not forking)
- Restarts on failure
- Waits 10 seconds between restarts

```ini
ExecStartPre=/bin/bash -c 'docker stop investment-dashboard || true'
ExecStartPre=/bin/bash -c 'docker rm investment-dashboard || true'
```
- Clean up old containers before starting

```ini
ExecStart=/usr/bin/docker run --name investment-dashboard ...
```
- Main command to run container

```ini
[Install]
WantedBy=multi-user.target
```
- Enables service in multi-user mode (default for servers)

---

## 📈 Monitoring & Maintenance

### CPU & Memory Usage
```bash
# Real-time stats
docker stats investment-dashboard

# One-time snapshot
docker stats --no-stream investment-dashboard
```

### Disk Space
```bash
# Container size
docker ps -s

# Image size
docker images --format "table {{.Repository}}\t{{.Size}}"

# Prune unused data
docker system prune -a
```

### Network
```bash
# Container network settings
docker inspect investment-dashboard | grep -A 20 "NetworkSettings"

# Port mapping
docker port investment-dashboard
```

---

## 🚨 Emergency Procedures

### Service Stuck/Won't Start
```bash
# 1. Check logs
sudo journalctl -u investment-dashboard -n 100

# 2. Stop service
sudo systemctl stop investment-dashboard

# 3. Remove container
docker rm investment-dashboard

# 4. Check Docker daemon
docker ps

# 5. Start service
sudo systemctl start investment-dashboard
```

### Container Memory Leak
```bash
# 1. Check memory usage
docker stats investment-dashboard

# 2. Restart container
docker restart investment-dashboard

# 3. Or via service
sudo systemctl restart investment-dashboard
```

### Port Already in Use
```bash
# 1. Find what's using port 8501
sudo lsof -i :8501

# 2. Kill process
sudo kill -9 <PID>

# 3. Restart service
sudo systemctl restart investment-dashboard
```

---

## 🔐 Security Hardening

### 1. Update System Packages
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

### 2. Enable Firewall
```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 8501/tcp
```

### 3. Configure SSH
```bash
sudo nano /etc/ssh/sshd_config

# Change these settings:
# PermitRootLogin no
# PasswordAuthentication no
# Port 2222

sudo systemctl restart ssh
```

### 4. Use Secrets Manager
```bash
# Store credentials in AWS Secrets Manager
aws secretsmanager create-secret \
  --name investment-dashboard/db-config \
  --secret-string '{"key":"value"}'

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id investment-dashboard/db-config
```

### 5. Enable CloudTrail
```bash
aws cloudtrail create-trail \
  --name investment-dashboard-trail \
  --s3-bucket-name my-audit-bucket
```

---

## 📊 Performance Optimization

### Limit Container Resources
```ini
# In service file, add:
[Service]
MemoryLimit=1G
MemoryAccounting=true
CPUQuota=50%
CPUAccounting=true
```

### Optimize Docker Image
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Enable Image Caching
```bash
# Build with buildkit
DOCKER_BUILDKIT=1 docker build -t investment-dashboard:latest .
```

---

## 🔄 Backup & Disaster Recovery

### Backup Application
```bash
# Backup entire directory
sudo tar -czf investment-dashboard-backup-$(date +%Y%m%d).tar.gz /opt/Investment-Dashboard

# Store in S3
aws s3 cp investment-dashboard-backup-*.tar.gz s3://my-backups/
```

### Backup Database
```bash
# Export DynamoDB table
aws dynamodb scan \
  --table-name Investment \
  --output json > investment-backup.json

# Store in S3
aws s3 cp investment-backup.json s3://my-backups/
```

### Restore from Backup
```bash
# Extract backup
sudo tar -xzf investment-dashboard-backup-*.tar.gz

# Restart service
sudo systemctl restart investment-dashboard
```

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] AWS account setup
- [ ] EC2 key pair created
- [ ] Security groups configured
- [ ] IAM role created (optional but recommended)
- [ ] DynamoDB table created
- [ ] Git repository ready

### Deployment
- [ ] EC2 instance launched
- [ ] Docker installed
- [ ] Application cloned
- [ ] Docker image built
- [ ] Environment file created
- [ ] Systemd service installed
- [ ] Service enabled
- [ ] Service started

### Post-Deployment
- [ ] Application accessible
- [ ] AWS credentials verified
- [ ] DynamoDB access tested
- [ ] Health check passed
- [ ] Logs reviewed
- [ ] Auto-restart verified
- [ ] Backups configured

---

## 🎯 Common Scenarios

### Scenario 1: Update Application
```bash
cd /opt/Investment-Dashboard
git pull origin main
docker build -t investment-dashboard:latest .
sudo systemctl restart investment-dashboard
```

### Scenario 2: Change Environment
```bash
nano /opt/Investment-Dashboard/.env
sudo systemctl restart investment-dashboard
```

### Scenario 3: Rollback Version
```bash
git revert HEAD --no-edit
docker build -t investment-dashboard:latest .
sudo systemctl restart investment-dashboard
```

### Scenario 4: Scale to Multiple Instances
```bash
# Use Auto Scaling Group in AWS
# Or deploy to multiple EC2 instances
# with Application Load Balancer
```

---

## 📞 Troubleshooting Matrix

| Problem | Solution |
|---------|----------|
| Service won't start | Check logs: `sudo journalctl -u investment-dashboard -f` |
| Container crashes | View Docker logs: `docker logs investment-dashboard` |
| Port 8501 unreachable | Check security group, check service status |
| AWS credentials error | Verify .env file, check IAM role |
| DynamoDB connection error | Check table exists, verify IAM permissions |
| High memory usage | Restart container, check for memory leaks |
| Slow application | Check CloudWatch metrics, optimize queries |

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Systemd Documentation](https://systemd.io/)
- [Streamlit Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

---

## ✅ Verification Commands

After deployment, verify everything works:

```bash
# 1. Service status
sudo systemctl status investment-dashboard

# 2. Container running
docker ps | grep investment-dashboard

# 3. Port listening
sudo lsof -i :8501

# 4. Application responding
curl http://localhost:8501

# 5. AWS credentials
docker exec investment-dashboard aws sts get-caller-identity

# 6. DynamoDB access
docker exec investment-dashboard aws dynamodb list-tables --region ap-south-1

# 7. Health check script
bash health-check.sh
```

---

**Deployment Complete! Your Investment Dashboard is now running on EC2 with auto-start capability.** 🎉

For quick reference, see `EC2_QUICK_REFERENCE.md`
