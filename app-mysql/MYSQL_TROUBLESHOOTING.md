# Investment Dashboard - MySQL Connection Troubleshooting Guide

## Problem: Cannot Connect to MySQL

### Error Message
```
mysql.connector.errors.DatabaseError: 2003: Can't connect to MySQL server on 'localhost:3306'
```

### Diagnosis Steps

#### 1. Verify MySQL is Running
```bash
# Check if MySQL service is active
sudo systemctl status mysql

# Or for Docker
docker-compose ps | grep mysql

# Try connecting from command line
mysql -h localhost -u root -p
```

**Solution if not running:**
```bash
# Start MySQL service
sudo systemctl start mysql

# Or restart Docker
docker-compose restart mysql

# Wait for MySQL to be ready
sleep 10
```

#### 2. Check Connection Credentials
```bash
# Verify credentials in mysql_service.py or app.py
MYSQL_CONFIG = {
    "host": "localhost",      # ← Check this
    "port": 3306,             # ← Check this
    "user": "root",           # ← Check this
    "password": "password",   # ← Check this
    "database": "investment_db"  # ← Check this
}

# Test with correct credentials
mysql -h localhost -u root -p -e "SELECT 1;"
```

**Solution if credentials wrong:**
```bash
# Update credentials in mysql_service.py line ~20
# Or create MySQL user with correct password
mysql -u root -p <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
EOF
```

#### 3. Verify Port is Open
```bash
# Check if port 3306 is listening
sudo netstat -tlnp | grep 3306
# or
sudo lsof -i :3306

# Check firewall rules
sudo ufw status
```

**Solution if port not listening:**
```bash
# Make sure MySQL is running
sudo systemctl restart mysql

# Add firewall rule if needed
sudo ufw allow 3306/tcp

# Or disable firewall temporarily for testing
sudo ufw disable
```

#### 4. Check Database Exists
```bash
# List all databases
mysql -u root -p -e "SHOW DATABASES;"

# Verify investment_db exists
mysql -u root -p -e "USE investment_db; SELECT COUNT(*) FROM information_schema.tables;"
```

**Solution if database missing:**
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE investment_db;"

# Run schema
mysql -u root -p investment_db < mysql_schema.sql

# Verify table was created
mysql -u root -p -e "USE investment_db; SHOW TABLES;"
```

## Problem: Connection Pool Error

### Error Message
```
Error creating connection pool: can't create pool because another pool with the same name already exists
```

### Solution

```bash
# Restart the application
streamlit run app.py

# Or if using Docker
docker-compose restart streamlit

# Check if multiple instances are running
ps aux | grep streamlit
ps aux | grep python

# Kill any existing processes
pkill -f streamlit
pkill -f python

# Restart Docker containers
docker-compose down
docker-compose up -d
```

## Problem: Table Not Found

### Error Message
```
mysql.connector.errors.ProgrammingError: 1146: Table 'investment_db.investment' doesn't exist
```

### Diagnosis
```bash
# Check if table exists
mysql -u root -p -e "USE investment_db; SHOW TABLES;"

# View table structure
mysql -u root -p -e "USE investment_db; DESCRIBE investment;"
```

### Solution

**Option 1: Application Auto-creates on First Run**
- Simply run the application: `streamlit run app.py`
- Table will be created automatically
- Check: `mysql -u root -p investment_db -e "SHOW TABLES;"`

**Option 2: Create Manually**
```bash
# Run the schema script
mysql -u root -p investment_db < mysql_schema.sql

# Or run SQL directly
mysql -u root -p investment_db <<EOF
CREATE TABLE investment (
    investment_id VARCHAR(36) PRIMARY KEY,
    investment_amount DECIMAL(15, 2) NOT NULL,
    investment_date DATE NOT NULL,
    annual_return_percentage DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_investment_date (investment_date)
);
EOF

# Verify
mysql -u root -p investment_db -e "DESCRIBE investment;"
```

**Option 3: Reset Database**
```bash
# Drop and recreate (⚠️ WARNING: Deletes all data)
mysql -u root -p <<EOF
DROP DATABASE investment_db;
CREATE DATABASE investment_db;
EOF

# Create schema
mysql -u root -p investment_db < mysql_schema.sql

# Run application to populate
streamlit run app.py
```

## Problem: Permission Denied

### Error Message
```
mysql.connector.errors.ProgrammingError: 1045: Access denied for user 'root'@'localhost'
```

### Diagnosis
```bash
# Check MySQL user privileges
mysql -u root -p -e "SELECT user, host FROM mysql.user WHERE user='root';"

# Check database permissions
mysql -u root -p -e "SHOW GRANTS FOR 'root'@'localhost';"
```

### Solution

**Option 1: Grant All Privileges**
```bash
mysql -u root -p <<EOF
GRANT ALL PRIVILEGES ON investment_db.* TO 'root'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';
FLUSH PRIVILEGES;
EOF
```

**Option 2: Create Application User**
```bash
mysql -u root -p <<EOF
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON investment_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Update mysql_service.py with new credentials
# user="app_user"
# password="app_password"
```

**Option 3: Reset Root Password**
```bash
# Stop MySQL
sudo systemctl stop mysql

# Start without permission tables
sudo mysqld_safe --skip-grant-tables &

# Connect and reset password
mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';
EXIT;
EOF

# Restart MySQL normally
sudo systemctl restart mysql
```

## Problem: Remote Connection Fails

### Error Message
```
mysql.connector.errors.DatabaseError: 2003: Can't connect to MySQL server on 'your-server:3306'
```

### Diagnosis
```bash
# Check if MySQL listens on all interfaces
mysql -u root -p -e "SHOW VARIABLES LIKE 'bind_address';"

# Try connecting from another machine
mysql -h <server-ip> -u root -p -e "SELECT 1;"
```

### Solution

**Option 1: Enable Remote Access**
```bash
# Edit /etc/mysql/mysql.conf.d/mysqld.cnf (or /etc/my.cnf)
# Find: bind-address = 127.0.0.1
# Change to: bind-address = 0.0.0.0

sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Or
sudo nano /etc/my.cnf

# Add/modify:
# [mysqld]
# bind-address = 0.0.0.0

# Restart MySQL
sudo systemctl restart mysql

# Verify
mysql -u root -p -e "SHOW VARIABLES LIKE 'bind_address';"
```

**Option 2: Create Remote User**
```bash
mysql -u root -p <<EOF
CREATE USER 'remote_user'@'%' IDENTIFIED BY 'remote_password';
GRANT ALL PRIVILEGES ON investment_db.* TO 'remote_user'@'%';
FLUSH PRIVILEGES;
EOF

# Update mysql_service.py
# host="your-server-ip"
# user="remote_user"
# password="remote_password"
```

**Option 3: Docker Network (if using Docker)**
```bash
# Use service name instead of localhost
# In docker-compose.yml, use: MYSQL_HOST=mysql

# Update mysql_service.py
# host="mysql"  # Service name from docker-compose
```

## Problem: Connection Timeout

### Error Message
```
mysql.connector.errors.InterfaceError: Connection timeout connecting to DB
```

### Diagnosis
```bash
# Check MySQL responsiveness
mysql -u root -p -e "SELECT 1;" --connect-timeout=5

# Check system resources
free -h      # Memory usage
df -h        # Disk space
top -bn1     # CPU usage

# Check MySQL logs
tail -50 /var/log/mysql/error.log
```

### Solution

**Option 1: Increase Connection Timeout**
```python
# In mysql_service.py, update connection config:
config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "investment_db",
    "connection_timeout": 30,  # Increase timeout
    "autocommit": True
}
```

**Option 2: Restart MySQL**
```bash
# Restart the service
sudo systemctl restart mysql

# Or with Docker
docker-compose restart mysql

# Wait for it to be ready
sleep 10
```

**Option 3: Check System Resources**
```bash
# Free up memory if needed
free -h
# If low, stop other services:
sudo systemctl stop <service>

# Check disk space
df -h
# If full, delete old backups or logs:
rm -rf ~/backups/*

# Check process limits
ulimit -a
```

## Problem: Encoding Issues

### Error Message
```
UnicodeDecodeError: 'utf-8' codec can't decode...
```

### Solution

```bash
# Verify database encoding
mysql -u root -p -e "SHOW CREATE DATABASE investment_db;"

# Change to UTF-8
mysql -u root -p <<EOF
ALTER DATABASE investment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# Update table encoding
mysql -u root -p <<EOF
ALTER TABLE investment CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# Update python connection
# In mysql_service.py:
config = {
    ...
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": True
}
```

## Problem: Docker MySQL Not Starting

### Error Message
```
ERROR: for investment-mysql  Cannot start service mysql: driver failed programming external connectivity
```

### Diagnosis
```bash
# Check Docker logs
docker logs investment-mysql

# Check if port is in use
sudo lsof -i :3306

# Check Docker network
docker network ls
docker network inspect investment-network
```

### Solution

**Option 1: Port Already in Use**
```bash
# Find and kill process using port 3306
sudo lsof -i :3306
kill -9 <PID>

# Or change port in docker-compose.yml:
# ports:
#   - "3307:3306"  # Change from 3306 to 3307

# Restart
docker-compose down
docker-compose up -d
```

**Option 2: Clear Docker Volumes**
```bash
# Remove old volumes
docker-compose down -v

# Restart
docker-compose up -d
```

**Option 3: Rebuild Images**
```bash
# Rebuild with fresh images
docker-compose down
docker system prune -a -f

docker-compose up -d --build
```

## Quick Verification Script

```bash
#!/bin/bash
# test_connection.sh

echo "🔍 Testing MySQL Connection..."

# Test 1: MySQL Service
if mysql -u root -p -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ MySQL service is running"
else
    echo "❌ MySQL service is NOT running"
    exit 1
fi

# Test 2: Database
if mysql -u root -p -e "USE investment_db;" > /dev/null 2>&1; then
    echo "✅ Database investment_db exists"
else
    echo "❌ Database investment_db NOT found"
    exit 1
fi

# Test 3: Table
if mysql -u root -p investment_db -e "SELECT COUNT(*) FROM investment;" > /dev/null 2>&1; then
    echo "✅ Table investment exists"
    count=$(mysql -u root -p investment_db -se "SELECT COUNT(*) FROM investment;")
    echo "   Records: $count"
else
    echo "❌ Table investment NOT found"
    exit 1
fi

# Test 4: Port
if nc -z localhost 3306 2>/dev/null; then
    echo "✅ Port 3306 is listening"
else
    echo "❌ Port 3306 is NOT listening"
    exit 1
fi

echo ""
echo "✅ All connection tests passed!"
```

## Getting More Help

If the above solutions don't work:

1. **Check Logs**
   ```bash
   # Application logs
   journalctl -u investment-dashboard.service -n 100
   
   # MySQL logs
   sudo tail -50 /var/log/mysql/error.log
   
   # Docker logs
   docker logs investment-mysql
   ```

2. **Verify Installation**
   ```bash
   python setup_helper.py
   ```

3. **Check MySQL Status**
   ```bash
   mysql_upgrade
   mysqlcheck -u root -p --all-databases
   ```

4. **Reinstall MySQL**
   ```bash
   sudo apt-get remove mysql-server mysql-client
   sudo apt-get install mysql-server mysql-client
   sudo mysql_secure_installation
   ```

---

**Last Updated:** 2024  
**Troubleshooting Guide v1.0**
