# CockroachDB Investment Dashboard - Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Connection Troubleshooting](#connection-troubleshooting)
5. [Performance Optimization](#performance-optimization)

---

## Local Development Setup

### Step 1: Prepare Your Environment

```bash
# Navigate to the app directory
cd Investment-Dashboard/app-cockroach-db

# Create a Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure CockroachDB Connection

Create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
```

Edit `.streamlit/secrets.toml` and add your CockroachDB connection string:


**Important**: Never commit this file to version control!

### Step 4: Verify SSL Certificate

The `root.crt` file is already included. Verify it exists:

```bash
ls -la root.crt
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Step 6: First-Time Setup

1. **Open the application** in your browser
2. **Create an admin account** (first account automatically becomes admin)
3. **Log in** with your credentials
4. **Create test investments** to verify functionality

---

## Streamlit Cloud Deployment

### Prerequisites
- GitHub account with your repository
- Streamlit Cloud account at https://share.streamlit.io
- CockroachDB cloud account with an active cluster

### Deployment Steps

#### 1. Prepare Your GitHub Repository

```bash
# From the root of your repository
git add -A
git commit -m "Add CockroachDB Investment Dashboard app"
git push origin main
```

#### 2. Create Streamlit Cloud App

1. Go to https://share.streamlit.io
2. Click "Create app"
3. Select your GitHub repository
4. Set the main file path to: `app-cockroach-db/app.py`
5. Click "Deploy"

#### 3. Add Secrets to Streamlit Cloud

After deployment:

1. Click the "..." menu (top right)
2. Select "Settings"
3. Go to "Secrets" tab
4. Add your CockroachDB credentials:
5. Click "Save"

The app will automatically restart with the new secrets.

#### 4. Verify Deployment

- Check that the app is running without errors
- Try registering a new user
- Create a test investment
- Verify the dashboard displays correctly

### Streamlit Cloud Environment Configuration

For optimal performance on Streamlit Cloud:

Create `streamlit/config.toml`:

```toml
[client]
showErrorDetails = false
toolbarMode = "viewer"
hideRunningIndicator = true

[logger]
level = "warning"

[server]
port = 8501
enableCORS = false
```

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Hub account (optional, for private registries)
- CockroachDB connection string

### Step 1: Create Dockerfile

A Dockerfile is already provided in the root directory. For app-cockroach-db specifically:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["streamlit", "run", "app.py"]
```

### Step 2: Build Docker Image

```bash
docker build -t investment-dashboard-cockroachdb:latest \
  --build-arg APP_PATH=app-cockroach-db \
  -f Dockerfile .
```

### Step 3: Run Docker Container

```bash
docker run -p 8501:8501 \
  -e STREAMLIT_COCKROACHDB_DATABASE_URL="postgresql://..." \
  investment-dashboard-cockroachdb:latest
```

Or using environment file:

```bash
# Create .env file
cat > .env << EOF
STREAMLIT_COCKROACHDB_DATABASE_URL=postgresql://venus:password@host:port/db?sslmode=verify-full
EOF

# Run container
docker run -p 8501:8501 --env-file .env \
  investment-dashboard-cockroachdb:latest
```

### Step 4: Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  investment-dashboard:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        APP_PATH: app-cockroach-db
    ports:
      - "8501:8501"
    environment:
      STREAMLIT_COCKROACHDB_DATABASE_URL: ${COCKROACHDB_URL}
      STREAMLIT_SERVER_PORT: 8501
      STREAMLIT_SERVER_ADDRESS: 0.0.0.0
    volumes:
      - ./app-cockroach-db:/app
    restart: unless-stopped
```

Run with Docker Compose:

```bash
COCKROACHDB_URL="postgresql://..." docker-compose up
```

---

## Connection Troubleshooting

### Test Connection Before Deployment

Create a test script `test_connection.py`:

```python
import psycopg2
import sys

DATABASE_URL = "postgresql://?sslmode=verify-full"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    
    # Test a simple query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"CockroachDB Version: {version[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    sys.exit(1)
```

Run the test:

```bash
python test_connection.py
```

### Common Connection Issues

#### Issue: "SSL certificate verification failed"

**Solution**:
- Verify `root.crt` file exists and is readable
- Check file permissions: `chmod 644 root.crt`
- Verify path in secrets matches actual file location
- Ensure `sslmode=verify-full` in connection string

#### Issue: "Connection timeout"

**Solution**:
- Verify CockroachDB cluster is active and running
- Check firewall rules allow connections on port 26257
- Verify IP address is whitelisted (if cluster has IP restrictions)
- Test DNS resolution: `nslookup your-cluster.j77.aws-ap-south-1.cockroachlabs.cloud`

#### Issue: "Authentication failed"

**Solution**:
- Verify username and password are correct
- Check for special characters that need escaping in password
- Ensure database name is correct (usually "defaultdb")
- Verify user has permissions on the database

#### Issue: "No module named 'psycopg2'"

**Solution**:
```bash
pip install --upgrade psycopg2-binary
# Or use psycopg2 instead of psycopg2-binary
pip install --upgrade psycopg2
```

---

## Performance Optimization

### Connection Pooling Configuration

Modify `cockroach_service.py` to add connection pooling:

```python
from psycopg2 import pool

class InvestmentService:
    _connection_pool = None
    
    @classmethod
    def get_connection_pool(cls, database_url):
        if cls._connection_pool is None:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, database_url
            )
        return cls._connection_pool
```

### Query Optimization

1. **Add indexes on frequently searched fields**:
   ```sql
   CREATE INDEX idx_investment_date ON investment (investment_date);
   CREATE INDEX idx_username ON users (username);
   CREATE INDEX idx_user_is_active ON users (is_active);
   ```

2. **Optimize dashboard queries**:
   - Limit data fetched from the database
   - Use pagination for large datasets
   - Cache results in Streamlit session state

### Caching Strategy

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_investments():
    return st.session_state.service.read_all_investments()
```

### Database Maintenance

1. **Regular backups**:
   - CockroachDB handles this automatically
   - Check Cloud Console for backup settings

2. **Monitor database size**:
   ```sql
   SELECT 
       pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
   FROM pg_database
   WHERE datname = 'defaultdb';
   ```

3. **Vacuum and analyze** (CockroachDB does this automatically):
   ```sql
   VACUUM ANALYZE;
   ```

---

## Production Deployment Checklist

- [ ] Verified CockroachDB cluster is in production region
- [ ] Enabled automatic backups in CockroachDB console
- [ ] Set up monitoring and alerts
- [ ] Configured SSL certificate (verify-full mode)
- [ ] Set up rate limiting (if exposed publicly)
- [ ] Configured authentication and RBAC
- [ ] Tested all user flows
- [ ] Verified error handling and logging
- [ ] Set up admin user with strong password
- [ ] Documented database credentials storage
- [ ] Configured CORS settings if needed
- [ ] Set up application logging
- [ ] Verified performance under load
- [ ] Tested disaster recovery procedures

---

## Monitoring & Alerts

### Set Up CockroachDB Cloud Alerts

1. Go to CockroachDB Cloud Console
2. Navigate to Monitoring > Alerts
3. Create alerts for:
   - High CPU usage
   - High memory usage
   - Connection pool exhaustion
   - Query performance degradation

### Application Monitoring

Monitor these metrics:
- Average response time
- Error rate
- User registration rate
- Investment creation/update/delete rate
- Database connection health

### Logging

Configure comprehensive logging in `app.py`:

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
```

---

## Support & Resources

- **CockroachDB Cloud Docs**: https://www.cockroachlabs.com/docs/cockroachdb/latest
- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud
- **Docker Docs**: https://docs.docker.com/
- **psycopg2 Documentation**: https://www.psycopg.org/psycopg2/docs/

---

**Last Updated**: January 2026
**CockroachDB Edition**: v1.0
