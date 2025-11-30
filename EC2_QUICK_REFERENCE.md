# Investment Dashboard - EC2 Deployment Quick Reference

## 🚀 One-Step Deployment

The easiest way to deploy on EC2:

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone repository
git clone https://github.com/your-repo/Investment-Dashboard.git
cd Investment-Dashboard

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This script will:
- ✅ Install Docker
- ✅ Build Docker image
- ✅ Create systemd service
- ✅ Start application
- ✅ Enable auto-start on reboot

---

## 📋 Manual Step-by-Step Deployment

### Step 1: Connect to EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Install Docker
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Clone Application
```bash
git clone https://github.com/your-repo/Investment-Dashboard.git /opt/Investment-Dashboard
cd /opt/Investment-Dashboard
```

### Step 4: Build Docker Image
```bash
docker build -t investment-dashboard:latest .
```

### Step 5: Create Environment File
```bash
cat > /opt/Investment-Dashboard/.env << EOF
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
EOF
```

### Step 6: Copy Systemd Service
```bash
sudo cp investment-dashboard.service /etc/systemd/system/
```

### Step 7: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable investment-dashboard
sudo systemctl start investment-dashboard
```

### Step 8: Verify Deployment
```bash
sudo systemctl status investment-dashboard
```

---

## 🔧 Service Management

### View Service Status
```bash
sudo systemctl status investment-dashboard
```

### View Real-time Logs
```bash
sudo journalctl -u investment-dashboard -f
```

### View Recent Logs
```bash
sudo journalctl -u investment-dashboard -n 100 --no-pager
```

### Restart Service
```bash
bash restart.sh
# or manually:
sudo systemctl restart investment-dashboard
```

### Stop Service
```bash
sudo systemctl stop investment-dashboard
```

### Start Service
```bash
sudo systemctl start investment-dashboard
```

### Disable Auto-start
```bash
sudo systemctl disable investment-dashboard
```

### Re-enable Auto-start
```bash
sudo systemctl enable investment-dashboard
```

---

## 🐳 Docker Commands

### Check Running Containers
```bash
docker ps | grep investment-dashboard
```

### View Container Logs
```bash
docker logs -f investment-dashboard
docker logs --tail 50 investment-dashboard
```

### Execute Command in Container
```bash
docker exec investment-dashboard bash
docker exec investment-dashboard aws dynamodb list-tables --region ap-south-1
```

### Stop Container
```bash
docker stop investment-dashboard
```

### Remove Container
```bash
docker rm investment-dashboard
```

---

## 📊 Health Checks

### Quick Health Check
```bash
bash health-check.sh
```

### Check If Port 8501 is Open
```bash
curl http://localhost:8501
curl -I http://localhost:8501
```

### Check AWS Credentials
```bash
docker exec investment-dashboard aws sts get-caller-identity
```

### Check DynamoDB Access
```bash
docker exec investment-dashboard aws dynamodb list-tables --region ap-south-1
```

---

## 🔄 Common Tasks

### View Application Logs
```bash
bash logs.sh
```

### Update Application
```bash
bash update.sh
```

### Restart Service
```bash
bash restart.sh
```

### Check All Services
```bash
bash health-check.sh
```

---

## 🛠️ Troubleshooting

### Service Won't Start
```bash
# Check systemd logs
sudo journalctl -u investment-dashboard -n 50

# Check if Docker is running
docker ps

# Check if port 8501 is in use
sudo lsof -i :8501
```

### Container Crashes Immediately
```bash
# View Docker logs
docker logs investment-dashboard

# Run container interactively
docker run -it --env-file .env investment-dashboard:latest /bin/bash
```

### AWS Credentials Error
```bash
# Verify .env file exists
cat /opt/Investment-Dashboard/.env

# Check Docker environment
docker exec investment-dashboard env | grep AWS

# Test AWS credentials
docker exec investment-dashboard aws sts get-caller-identity
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8501

# Kill process
sudo kill -9 <PID>

# Or use different port in .env
```

---

## 📝 Useful Helper Scripts

All scripts are included in the repository:

| Script | Purpose |
|--------|---------|
| deploy.sh | One-step deployment |
| health-check.sh | System health check |
| restart.sh | Restart service safely |
| update.sh | Update application |
| logs.sh | View logs |

Make them executable:
```bash
chmod +x *.sh
```

---

## 🌐 Access Application

After deployment, access at:
```
http://<EC2-PUBLIC-IP>:8501
```

To find your EC2 public IP:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
# or
hostname -I
```

---

## 💾 Backup & Recovery

### Backup Database Connection
```bash
# Ensure .env is backed up
cp /opt/Investment-Dashboard/.env /opt/Investment-Dashboard/.env.backup
```

### Backup Docker Image
```bash
docker save investment-dashboard:latest > investment-dashboard-backup.tar
```

### Restore from Backup
```bash
docker load < investment-dashboard-backup.tar
sudo systemctl restart investment-dashboard
```

---

## 🔒 Security Best Practices

### Use IAM Role Instead of Credentials
1. Create IAM role with DynamoDB permissions
2. Attach to EC2 instance
3. Remove AWS credentials from .env file

### Enable HTTPS
1. Get SSL certificate (Let's Encrypt)
2. Install nginx as reverse proxy
3. Configure nginx to forward to port 8501

### Restrict Security Group
- SSH: Only from your IP
- HTTP/HTTPS: From specific sources
- Port 8501: From trusted sources only

---

## 📈 Monitoring & Logs

### View Memory Usage
```bash
docker stats investment-dashboard
```

### View System Stats
```bash
free -h
df -h
```

### Enable Log Rotation
```bash
sudo nano /etc/logrotate.d/investment-dashboard
# Configure log rotation policy
```

---

## 🚀 Production Deployment Checklist

- [ ] EC2 instance created and running
- [ ] Security groups configured
- [ ] Docker installed
- [ ] Application cloned/copied
- [ ] .env file with credentials created
- [ ] Docker image built
- [ ] Systemd service created
- [ ] Service enabled for auto-start
- [ ] Service started successfully
- [ ] Application accessible on port 8501
- [ ] AWS credentials verified
- [ ] DynamoDB access confirmed
- [ ] Logs monitored
- [ ] Health check passed

---

## 📞 Quick Support

| Issue | Command |
|-------|---------|
| Service not running | `sudo systemctl status investment-dashboard` |
| View logs | `sudo journalctl -u investment-dashboard -f` |
| Restart | `bash restart.sh` |
| Health check | `bash health-check.sh` |
| Update | `bash update.sh` |

---

## 🎯 Next Steps

1. **Deploy**: Run `./deploy.sh`
2. **Verify**: Run `./health-check.sh`
3. **Monitor**: Run `./logs.sh`
4. **Access**: Open `http://ec2-ip:8501`
5. **Test**: Add an investment and verify it works

---

**Your Investment Dashboard is now running on EC2 with auto-start! 🎉**

For detailed documentation, see `DOCKER_DEPLOYMENT.md`.
