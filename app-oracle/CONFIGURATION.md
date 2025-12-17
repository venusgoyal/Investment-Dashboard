# Oracle Edition - Configuration Guide

## Environment Variables

### Oracle Database Connection

```powershell
# PowerShell example
$env:ORACLE_USER = "system"
$env:ORACLE_PASSWORD = "your_secure_password"
$env:ORACLE_HOST = "localhost"
$env:ORACLE_PORT = "1521"
$env:ORACLE_SERVICE = "XEPDB1"
```

### Variable Reference

| Variable | Default | Example | Notes |
|----------|---------|---------|-------|
| ORACLE_USER | system | system | Database username |
| ORACLE_PASSWORD | oracle | secure_pwd | Database password |
| ORACLE_HOST | localhost | 192.168.1.10 | Oracle server IP/hostname |
| ORACLE_PORT | 1521 | 1521 | Oracle listener port |
| ORACLE_SERVICE | XEPDB1 | XEPDB1 | Database service name |

### Streamlit Configuration

```toml
# .streamlit/config.toml

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
headless = true
port = 8501
enableCORS = false
maxUploadSize = 200
```

## Connection String Formats

### Local Oracle XE
```
Host: localhost
Port: 1521
Service: XEPDB1
User: system
```

### Remote Oracle DB
```
Host: db.example.com
Port: 1521
Service: ORCL
User: dashboard_user
```

### Oracle Cloud Infrastructure
```
Host: xxxxx.oraclecloud.com
Port: 1521
Service: service_name_high
User: admin
```

## Security Best Practices

### 1. Credential Management

❌ **Do NOT hardcode credentials**
```python
# BAD
connection = cx_Oracle.connect('system', 'password', 'localhost:1521/XEPDB1')
```

✅ **Use environment variables**
```python
# GOOD
db_user = os.getenv('ORACLE_USER')
db_password = os.getenv('ORACLE_PASSWORD')
connection = cx_Oracle.connect(db_user, db_password, dsn)
```

### 2. Using .env Files

Create `.env` file (not in git):
```
ORACLE_USER=system
ORACLE_PASSWORD=secure_password_123
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
user = os.getenv('ORACLE_USER')
```

### 3. Database User Permissions

Create dedicated application user:
```sql
CREATE USER dashboard_user IDENTIFIED BY "secure_password_123";
GRANT CREATE SESSION TO dashboard_user;
GRANT CREATE TABLE TO dashboard_user;
GRANT UNLIMITED TABLESPACE TO dashboard_user;
```

Connect as:
```
ORACLE_USER=dashboard_user
ORACLE_PASSWORD=secure_password_123
```

### 4. Network Security

```sql
-- Enable password expiration
ALTER PROFILE default LIMIT PASSWORD_LIFE_TIME 90;

-- Force password complexity
ALTER PROFILE default LIMIT PASSWORD_VERIFY_FUNCTION verify_function;

-- Limit failed login attempts
ALTER PROFILE default LIMIT FAILED_LOGIN_ATTEMPTS 5;
ALTER PROFILE default LIMIT PASSWORD_LOCK_TIME 1;
```

## Connection Pooling

### cx_Oracle Connection Pool

```python
import cx_Oracle

# Create connection pool
pool = cx_Oracle.SessionPool(
    user="system",
    password="oracle",
    dsn="localhost:1521/XEPDB1",
    min=2,
    max=5,
    increment=1,
    homogeneous=True
)

# Get connection from pool
connection = pool.acquire()

# Use connection
cursor = connection.cursor()
cursor.execute("SELECT * FROM Investment")

# Release to pool
pool.release(connection)
```

## Performance Tuning

### Query Optimization

```python
# Use bind variables (prevents SQL injection, improves performance)
cursor.execute("""
    SELECT * FROM Investment 
    WHERE investment_date = :1
""", [investment_date])
```

### Indexes

```sql
-- Created automatically by setup_oracle.py
CREATE INDEX idx_investment_date ON Investment(investment_date);
CREATE INDEX idx_created_at ON Investment(created_at);
CREATE INDEX idx_investment_id ON Investment(investment_id);
```

### Connection Settings

```python
# Set fetch size for better performance
cursor.arraysize = 1000

# Enable bulk operations
cursor.execute("ALTER SESSION SET PLSQL_WARNINGS='ENABLE:ALL'")
```

## Logging Configuration

### Python Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('investment_dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Oracle SQL Tracing

```sql
-- Enable SQL trace
ALTER SESSION SET SQL_TRACE=TRUE;

-- View trace files
SELECT trace_filename FROM v$diag_trace_file WHERE tracing_enabled='Yes';
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup_oracle.sh
BACKUP_DIR="/backups/oracle"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

expdp system/password@XEPDB1 \
  FULL=Y \
  DIRECTORY=backup_dir \
  DUMPFILE=full_backup_${TIMESTAMP}.dmp \
  LOGFILE=full_backup_${TIMESTAMP}.log
```

### Point-in-Time Recovery

```sql
-- Startup in mount mode
STARTUP MOUNT;

-- Recover to specific time
RECOVER DATABASE UNTIL TIME '2024-01-15 14:30:00';

-- Open with resetlogs
ALTER DATABASE OPEN RESETLOGS;
```

## Disaster Recovery

### Database Cloning

```sql
-- On source database
CREATE PFILE FROM SPFILE;

-- Copy files to target machine
-- Create initORCL.ora on target
-- Create database directories

-- On target
STARTUP NOMOUNT PFILE='initORCL.ora';
CREATE DATABASE ORCL ...;
```

### Data Migration

```sql
-- Export from source
expdp system/password FULL=Y DUMPFILE=source.dmp;

-- Import to target
impdp system/password FULL=Y DUMPFILE=source.dmp;
```

## Monitoring

### Check Database Status

```sql
-- Connection status
SELECT * FROM v$session WHERE username='SYSTEM';

-- Table space usage
SELECT tablespace_name, SUM(bytes)/1024/1024 MB 
FROM dba_data_files 
GROUP BY tablespace_name;

-- Active sessions
SELECT sid, serial#, username, event FROM v$session_wait;
```

### Python Monitoring

```python
def check_db_health():
    cursor.execute("SELECT COUNT(*) FROM Investment")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM v$session")
    active_sessions = len(cursor.fetchall())
    
    return {
        'status': 'healthy' if count >= 0 else 'error',
        'investments': count,
        'active_sessions': active_sessions
    }
```

## Upgrade Procedures

### Oracle Database Upgrade

```bash
# Pre-upgrade checks
./preupgrade.jar

# Upgrade database
./upgrade.sh

# Post-upgrade validation
./postupgrade.sql
```

### Application Upgrade

```bash
# Stop application
docker stop investment-dashboard

# Backup data
python backup_oracle.py

# Pull new code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python setup_oracle.py

# Start application
docker start investment-dashboard
```

## Common Issues

### Connection Pool Exhausted

**Problem**: "cx_Oracle.DatabaseError: DPI-1010"

**Solution**:
```python
# Increase pool size
pool = cx_Oracle.SessionPool(..., max=20)

# Or close unused connections
connection.close()
```

### Table Not Found

**Problem**: "ORA-00942: table or view does not exist"

**Solution**:
```bash
# Verify table exists
python -c "from oracle_service import InvestmentService; print('OK')"

# If not, initialize
python setup_oracle.py
```

### Character Encoding Issues

**Problem**: Special characters display incorrectly

**Solution**:
```python
# Set encoding in connection
connection = cx_Oracle.connect(
    user=user,
    password=password,
    dsn=dsn,
    encoding="UTF-8"
)
```

---

**Related Documentation**:
- README.md - Project overview
- QUICKSTART.md - 5-minute setup
- DOCKER_DEPLOYMENT.md - Docker deployment
- EC2_DEPLOYMENT.md - AWS EC2 setup
