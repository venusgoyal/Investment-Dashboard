# MySQL Investment Dashboard - EC2 Deployment Guide

Complete guide to deploy the MySQL Investment Dashboard on AWS EC2 with auto-start and monitoring.

## Prerequisites

- AWS Account with EC2 access
- Ubuntu 20.04+ AMI
- EC2 instance type: t2.micro (free tier) or higher
- Security group with inbound rules for ports 8501 (HTTP) and 3306 (MySQL)
- Git installed on EC2 instance

## Architecture

```
┌─────────────────────────────────────┐
│     EC2 Instance (Ubuntu)           │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │  Docker Compose               │  │
│  ├─────────────────┬─────────────┤  │
│  │  MySQL Container│  Streamlit  │  │
│  │  Port 3306      │  Port 8501  │  │
│  └─────────────────┴─────────────┘  │
├─────────────────────────────────────┤
│  systemd Service                    │
│  (investment-dashboard.service)     │
└─────────────────────────────────────┘
```

## Step-by-Step Deployment

### Step 1: Launch EC2 Instance

1. Go to AWS EC2 Dashboard
2. Click "Launch Instance"
3. Select "Ubuntu Server 20.04 LTS" (or newer)
4. Choose instance type: t2.micro (free tier) or t2.small
5. Configure security group:
   - **Inbound Rules:**
     - Type: HTTP, Port: 80, Source: 0.0.0.0/0
     - Type: HTTPS, Port: 443, Source: 0.0.0.0/0
     - Type: Custom TCP, Port: 8501, Source: 0.0.0.0/0
     - Type: MySQL/Aurora, Port: 3306, Source: 0.0.0.0/0 (restrict in production)
   - **Outbound Rules:** Allow all
6. Review and launch
7. Create or select key pair
8. Download .pem file (keep it safe!)

### Step 2: Connect to EC2

```bash
# On your local machine
chmod 400 your-key.pem

# SSH into instance
ssh -i your-key.pem ubuntu@<ec2-instance-ip>

# Or use EC2 Instance Connect (through AWS Console)
```

### Step 3: Update System & Install Docker

```bash
# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker-compose --version
```

### Step 4: Clone or Upload Application

#### Option A: Clone from Git
```bash
# Clone repository
git clone <your-repo-url> ~/investment-dashboard
cd ~/investment-dashboard/app-mysql
```

#### Option B: Upload Files
```bash
# From your local machine
scp -i your-key.pem -r app-mysql ubuntu@<ec2-instance-ip>:~/investment-dashboard

# Connect and navigate
ssh -i your-key.pem ubuntu@<ec2-instance-ip>
cd ~/investment-dashboard
```

### Step 5: Create Systemd Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/investment-dashboard.service > /dev/null <<'EOF'
[Unit]
Description=Investment Dashboard Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/investment-dashboard/app-mysql
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable investment-dashboard.service

# Start service
sudo systemctl start investment-dashboard.service
```

### Step 6: Verify Deployment

```bash
# Check service status
sudo systemctl status investment-dashboard.service

# View logs
journalctl -u investment-dashboard.service -f

# Check container status
docker-compose ps

# Verify ports are listening
sudo netstat -tlnp | grep -E '8501|3306'

# Test application
curl http://localhost:8501/_stcore/health
```

### Step 7: Verify Database

```bash
# Enter MySQL container
docker-compose exec mysql mysql -u root -ppassword investment_db

# In MySQL shell
SELECT * FROM investment;
DESCRIBE investment;
EXIT;
```

## Access Application

From your browser:
```
http://<ec2-instance-public-ip>:8501
```

Example: `http://203.0.113.45:8501`

## Management Commands

### Service Management

```bash
# View service status
sudo systemctl status investment-dashboard.service

# Start service
sudo systemctl start investment-dashboard.service

# Stop service
sudo systemctl stop investment-dashboard.service

# Restart service
sudo systemctl restart investment-dashboard.service

# View service logs
journalctl -u investment-dashboard.service -f

# View last 50 lines of logs
journalctl -u investment-dashboard.service -n 50

# View logs from specific time
journalctl -u investment-dashboard.service --since "2 hours ago"
```

### Docker Management

```bash
# View running containers
docker ps

# View container logs
docker-compose logs -f

# View specific container logs
docker logs investment-mysql -f
docker logs investment-streamlit -f

# Stop containers
docker-compose stop

# Start containers
docker-compose start

# Restart containers
docker-compose restart

# Remove containers
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Database Management

```bash
# Access MySQL
docker-compose exec mysql mysql -u root -ppassword investment_db

# Backup database
docker-compose exec mysql mysqldump -u root -ppassword investment_db > backup.sql

# Restore database
docker-compose exec mysql mysql -u root -ppassword investment_db < backup.sql

# Check database size
docker-compose exec mysql mysql -u root -ppassword -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb FROM information_schema.tables WHERE table_schema = 'investment_db';"
```

## Monitoring

### Health Check

```bash
# Run health check script
./health-check.sh

# Or manually check
curl http://localhost:8501/_stcore/health
mysql -h localhost -u root -ppassword -e "SELECT 1;"
```

### Continuous Monitoring

```bash
# Watch service logs in real-time
journalctl -u investment-dashboard.service -f --output=short

# Monitor system resources
top
# or
htop  # Install: sudo apt-get install htop

# Monitor disk space
df -h

# Monitor Docker container stats
docker stats
```

### Automated Monitoring (CloudWatch)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure and start CloudWatch agent (see AWS docs)
```

## Backup & Disaster Recovery

### Daily Backup Script

```bash
#!/bin/bash
# backup.sh - Create daily backup

BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/investment_db_$DATE.sql"

# Backup database
docker-compose exec -T mysql mysqldump -u root -ppassword investment_db > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 30 backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup created: ${BACKUP_FILE}.gz"
```

### Setup Automated Backups

```bash
# Make script executable
chmod +x backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/ubuntu/investment-dashboard/backup.sh
```

### Restore from Backup

```bash
# List backups
ls -lh ~/backups/

# Restore specific backup
docker-compose exec mysql mysql -u root -ppassword investment_db < ~/backups/investment_db_20240101_020000.sql
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status investment-dashboard.service

# Check logs for errors
journalctl -u investment-dashboard.service -n 100

# Test Docker Compose manually
cd ~/investment-dashboard/app-mysql
docker-compose up

# Common issues:
# - Port already in use: sudo lsof -i :8501
# - Permission denied: Check docker group membership: groups ubuntu
# - No space left: df -h
```

### MySQL Connection Error

```bash
# Check if MySQL container is running
docker-compose ps

# View MySQL logs
docker logs investment-mysql

# Test MySQL connection from host
docker-compose exec mysql mysql -u root -ppassword -e "SELECT 1;"

# Check MySQL configuration
docker-compose exec mysql mysql -u root -ppassword -e "SHOW VARIABLES LIKE 'bind_address';"
```

### Streamlit Not Loading

```bash
# Check Streamlit container logs
docker logs investment-streamlit

# Check if port is open
sudo netstat -tlnp | grep 8501

# Check firewall rules
sudo ufw status

# Allow port 8501
sudo ufw allow 8501/tcp

# Test connection
curl http://localhost:8501/_stcore/health
```

### Application Performance Issues

```bash
# Check Docker container resources
docker stats

# Monitor system resources
free -h  # Memory usage
top     # CPU usage

# Check MySQL slow queries
docker-compose exec mysql mysql -u root -ppassword -e "SHOW VARIABLES LIKE 'slow_query_log';"

# Enable slow query log
docker-compose exec mysql mysql -u root -ppassword -e "SET GLOBAL slow_query_log='ON';"
```

## Updates & Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose up -d --build

# Verify changes
curl http://localhost:8501/_stcore/health
```

### Update Docker & System

```bash
# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Update Docker
sudo apt-get install --only-upgrade docker.io

# Restart services
sudo systemctl restart docker
sudo systemctl restart investment-dashboard.service
```

### Upgrade MySQL

```bash
# Backup first!
docker-compose exec mysql mysqldump -u root -ppassword investment_db > backup.sql

# Update docker-compose.yml MySQL version
# Edit docker-compose.yml: image: mysql:8.0.xx

# Rebuild
docker-compose down
docker-compose up -d

# Verify upgrade
docker-compose exec mysql mysql -u root -ppassword -e "SELECT VERSION();"
```

## Security Hardening

### 1. Change Default Credentials

```bash
# Change MySQL password
docker-compose exec mysql mysql -u root -ppassword
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_strong_password';
mysql> FLUSH PRIVILEGES;
mysql> EXIT;

# Update docker-compose.yml with new password
# Update MYSQL_ROOT_PASSWORD and connection strings
```

### 2. Restrict Security Groups

```bash
# SSH access only from specific IPs
# Port 8501 only from specific IPs
# Port 3306 only from EC2 instance security group (not 0.0.0.0/0)
```

### 3. Enable SSL/TLS

```bash
# Generate SSL certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/streamlit.key \
  -out /etc/ssl/certs/streamlit.crt

# Update streamlit config with SSL settings
# See .streamlit/config.toml
```

### 4. Database User Permissions

```bash
# Create limited MySQL user for application
docker-compose exec mysql mysql -u root -ppassword <<EOF
CREATE USER 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON investment_db.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
EOF
```

### 5. Enable Firewall

```bash
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 8501/tcp    # Streamlit
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## Scaling & Production

### Load Balancing

```
┌──────────────┐
│  Load        │
│  Balancer    │
└──────┬───────┘
       │
    ┌──┴──┬──────┐
    │     │      │
  ┌─▼─┐ ┌─▼─┐ ┌─▼─┐
  │EC2│ │EC2│ │EC2│
  └───┘ └───┘ └───┘
    │
  ┌─▼──────────┐
  │ RDS MySQL  │
  │ (managed)  │
  └────────────┘
```

### Use Managed RDS MySQL

```bash
# Update docker-compose.yml to use RDS endpoint
MYSQL_HOST=investment-db.xxxxxx.us-east-1.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=<from Secrets Manager>
```

## Cost Optimization

### EC2
- Use t2.micro for free tier
- Stop instance when not in use
- Set auto-shutdown: `sudo shutdown -h +2`

### RDS (if using managed MySQL)
- Use storage auto-scaling
- Enable backups (automated)
- Use Multi-AZ for production only

### Data Transfer
- Keep MySQL in same region
- Use VPC for private communication
- Cache frequently accessed data

## Performance Tuning

### MySQL Optimization

```bash
# Increase connection pool size
docker-compose exec mysql mysql -u root -ppassword -e "SET GLOBAL max_connections=1000;"

# Enable query cache (MySQL 5.7)
docker-compose exec mysql mysql -u root -ppassword -e "SET GLOBAL query_cache_size=268435456;"

# Optimize indexes
docker-compose exec mysql mysql -u root -ppassword investment_db -e "ANALYZE TABLE investment;"
```

### Streamlit Optimization

```bash
# Update .streamlit/config.toml
[client]
maxUploadSize = 200

[server]
maxUploadSize = 200
enableXsrfProtection = true
```

## Disaster Recovery Plan

### Recovery Time Objective (RTO): < 15 minutes
### Recovery Point Objective (RPO): < 1 hour

1. **Daily backups** at 2 AM UTC
2. **Automated backups** stored in S3
3. **Redundant servers** in different AZs (production)
4. **Database snapshots** every 4 hours

### Recovery Procedure

```bash
# 1. Launch new EC2 instance from AMI
# 2. Clone application code
# 3. Restore latest backup
docker-compose exec mysql mysql -u root -ppassword investment_db < latest_backup.sql
# 4. Verify data integrity
# 5. Start application
sudo systemctl start investment-dashboard.service
```

## Support & Next Steps

### Useful AWS Resources
- EC2 Dashboard: https://console.aws.amazon.com/ec2/
- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/
- RDS Console: https://console.aws.amazon.com/rds/
- Elastic IPs: https://console.aws.amazon.com/ec2/ (under Network & Security)

### Additional Services to Consider
- Route 53: DNS management
- Elastic Load Balancer: Load balancing
- RDS: Managed database service
- S3: Backup storage
- CloudFront: CDN
- Secrets Manager: Credential management

---

**Last Updated:** 2024
**Version:** 1.0.0
**Status:** Production Ready
