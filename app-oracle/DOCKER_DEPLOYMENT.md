# Oracle Edition - Docker Deployment Guide

## Overview

Deploy the Investment Dashboard with Oracle Database using Docker and docker-compose.

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Oracle Database (running or Docker-based)
- 2GB RAM minimum, 5GB disk space

## Option 1: Dockerize Streamlit App Only (Oracle Separate)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 streamlit && chown -R streamlit:streamlit /app
USER streamlit

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py"]
```

### Build Docker Image

```bash
docker build -t investment-dashboard-oracle:latest .
```

### Run Container (Linux/macOS)

```bash
docker run -d \
  --name investment-dashboard \
  -p 8501:8501 \
  -e ORACLE_USER=system \
  -e ORACLE_PASSWORD=your_password \
  -e ORACLE_HOST=oracle.example.com \
  -e ORACLE_PORT=1521 \
  -e ORACLE_SERVICE=XEPDB1 \
  investment-dashboard-oracle:latest
```

### Run Container (PowerShell)

```powershell
docker run -d `
  --name investment-dashboard `
  -p 8501:8501 `
  -e ORACLE_USER=system `
  -e ORACLE_PASSWORD=your_password `
  -e ORACLE_HOST=oracle.example.com `
  -e ORACLE_PORT=1521 `
  -e ORACLE_SERVICE=XEPDB1 `
  investment-dashboard-oracle:latest
```

## Option 2: Docker Compose with Oracle (Complete Stack)

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  oracle:
    image: gvenzl/oracle-xe:latest
    container_name: oracle-db
    environment:
      ORACLE_PASSWORD: oracle_password_123
      ORACLE_DATABASE: XEPDB1
    ports:
      - "1521:1521"
      - "5500:5500"
    volumes:
      - oracle_data:/opt/oracle/oradata
    healthcheck:
      test: ["CMD", "sqlplus", "-L", "system/oracle_password_123@localhost:1521/XEPDB1", "as", "sysdba"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - investment_network

  streamlit:
    build: .
    container_name: investment-dashboard
    depends_on:
      oracle:
        condition: service_healthy
    environment:
      ORACLE_USER: system
      ORACLE_PASSWORD: oracle_password_123
      ORACLE_HOST: oracle
      ORACLE_PORT: 1521
      ORACLE_SERVICE: XEPDB1
    ports:
      - "8501:8501"
    volumes:
      - ./logs:/app/logs
    networks:
      - investment_network
    restart: always

volumes:
  oracle_data:

networks:
  investment_network:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f streamlit

# Stop services
docker-compose down
```

## Container Management

### View Logs

```bash
# Streamlit logs
docker logs investment-dashboard

# Follow logs in real-time
docker logs -f investment-dashboard

# Last 100 lines
docker logs --tail 100 investment-dashboard
```

### Health Check

```bash
# Check container status
docker ps | grep investment-dashboard

# Check health
docker inspect --format='{{.State.Health.Status}}' investment-dashboard
```

### Stop/Restart

```bash
# Stop
docker stop investment-dashboard

# Start
docker start investment-dashboard

# Restart
docker restart investment-dashboard

# Remove
docker rm investment-dashboard
```

## Database Setup in Container

### Initialize Oracle Schema

```bash
# Execute setup script in container
docker exec oracle sqlplus -S system/oracle_password_123@localhost:1521/XEPDB1 < setup_oracle.sql
```

### Load Sample Data

```bash
# Copy sample_data.py to container and run
docker cp sample_data.py investment-dashboard:/app/
docker exec investment-dashboard python sample_data.py
```

## Networking

### Access Application

- **Local**: http://localhost:8501
- **Network**: http://<container-ip>:8501
- **Docker Network**: http://streamlit:8501

### Connect to Oracle from Host

```bash
sqlplus system/oracle_password_123@localhost:1521/XEPDB1
```

## Environment Variables

Create `.env` file:

```env
ORACLE_USER=system
ORACLE_PASSWORD=oracle_password_123
ORACLE_HOST=oracle
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

Use in compose:
```yaml
env_file: .env
```

## Volumes & Persistence

### Oracle Data Persistence

```yaml
volumes:
  oracle_data:
    driver: local
```

Data survives container restarts but located in Docker system.

### Backup Oracle Data

```bash
docker run --rm \
  -v oracle_data:/data \
  -v $(pwd):/backup \
  busybox tar czf /backup/oracle_backup.tar.gz /data
```

### Restore Oracle Data

```bash
docker run --rm \
  -v oracle_data:/data \
  -v $(pwd):/backup \
  busybox tar xzf /backup/oracle_backup.tar.gz -C /
```

## Performance Tuning

### Resource Limits

```yaml
services:
  streamlit:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Oracle Memory

```yaml
services:
  oracle:
    environment:
      ORACLE_MEMORY: 2G
      ORACLE_SGA_PERCENT: 75
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs investment-dashboard

# Inspect container
docker inspect investment-dashboard

# Run in interactive mode
docker run -it investment-dashboard-oracle:latest bash
```

### Oracle connection failed

```bash
# Test connection
docker exec investment-dashboard python -c \
  "from oracle_service import InvestmentService; print('OK')"

# Check Oracle is running
docker logs oracle
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Remove old images
docker image prune -a
```

## Production Deployment

### Security Considerations

1. **Credentials**: Use Docker secrets or environment variables
2. **Network**: Run behind reverse proxy (nginx, Apache)
3. **SSL**: Enable HTTPS with certificates
4. **Backups**: Regular automated Oracle backups
5. **Updates**: Keep images and dependencies updated

### Reverse Proxy (nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec oracle expdp system/password \
  FULL=Y \
  DIRECTORY=export_dir \
  DUMPFILE=backup_$TIMESTAMP.dmp \
  LOGFILE=backup_$TIMESTAMP.log
```

### Monitoring

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Clean Up

```bash
# Stop and remove all services
docker-compose down

# Remove images
docker rmi investment-dashboard-oracle:latest

# Remove volumes
docker volume rm investment_oracle_data

# Clean system
docker system prune -a --volumes
```

---

**Next Steps**:
- Deploy to AWS ECS: See AWS_DEPLOYMENT.md
- Deploy to Kubernetes: See K8S_DEPLOYMENT.md
- Monitor with Prometheus/Grafana: See MONITORING.md
