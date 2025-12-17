# MySQL Setup Guide for Investment Dashboard

## Prerequisites

- MySQL Server 5.7+ or 8.0+
- Python 3.8+
- pip (Python package manager)

## MySQL Installation & Setup

### Step 1: Create Database and User

```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE investment_db;

-- Create user (if needed)
CREATE USER 'root'@'localhost' IDENTIFIED BY 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON investment_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SELECT * FROM information_schema.schemata WHERE schema_name = 'investment_db';
```

### Step 2: Verify Connection

```bash
# Test connection
mysql -h localhost -u root -p -e "SELECT DATABASE();"
```

## Application Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `mysql-connector-python` - MySQL driver
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `streamlit-option-menu` - Navigation menu

### Step 2: Update MySQL Credentials (if different)

Edit `mysql_service.py` line ~20:
```python
MYSQL_CONFIG = {
    "host": "localhost",      # MySQL host
    "port": 3306,            # MySQL port
    "user": "root",          # MySQL user
    "password": "password",  # MySQL password
    "database": "investment_db"  # Database name
}
```

Or in `app.py` lines ~30-36:
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "investment_db"
}
```

### Step 3: Run Application

```bash
streamlit run app.py
```

Application will open at: `http://localhost:8501`

## Database Schema

The application automatically creates the following table:

```sql
CREATE TABLE investment (
    investment_id VARCHAR(36) PRIMARY KEY,
    investment_amount DECIMAL(15, 2) NOT NULL,
    investment_date DATE NOT NULL,
    annual_return_percentage DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_investment_date (investment_date)
);
```

### Column Details

| Column | Type | Description |
|--------|------|-------------|
| investment_id | VARCHAR(36) | Unique UUID for each investment |
| investment_amount | DECIMAL(15,2) | Initial investment amount |
| investment_date | DATE | Date of investment |
| annual_return_percentage | DECIMAL(5,2) | Annual return % |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## Features

### Dashboard
- View all investments
- Key metrics (Total Invested, Current Value, Return %)
- Investment summary table

### Create
- Add new investments
- Auto-calculate current value
- Display profit/loss

### View All
- Expandable investment cards
- Detailed metrics per investment
- Profit/loss and return % calculations

### Update
- Select investment to modify
- Update amount, date, or return %
- Auto-calculation of new values

### Delete
- Select investment to delete
- Confirmation with investment details
- Permanent deletion

## Calculations

### Current Value
```
Current Value = Principal × (1 + annual_rate)^(years_passed)
```
Where `years_passed = actual_days_passed / 365.25`

### Profit/Loss
```
Profit/Loss = Current Value - Investment Amount
```

### Return Percentage
```
Return % = ((Current Value - Investment Amount) / Investment Amount) × 100
```

## Troubleshooting

### Connection Error
```
Error connecting to MySQL: 2003: Can't connect to MySQL server
```
**Solution:**
- Verify MySQL is running: `mysql -u root -p`
- Check host/port in config
- Ensure credentials are correct
- Verify database exists: `mysql -u root -p -e "SELECT DATABASE();"`

### Authentication Error
```
Error 1045: Access denied for user 'root'@'localhost'
```
**Solution:**
- Verify password in config matches MySQL password
- Check user permissions: `SELECT * FROM mysql.user;`
- Grant privileges: `GRANT ALL ON investment_db.* TO 'root'@'localhost';`

### Table Not Created
**Solution:**
- Application auto-creates table on first run
- Verify permissions: `GRANT ALL ON investment_db.* TO 'root'@'localhost';`
- Manually create: Run SQL from "Database Schema" section

### Application Won't Start
**Solution:**
- Verify MySQL connection: `mysql -u root -p`
- Check port 8501 is available: `lsof -i :8501`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+)

## Backup & Restore

### Backup Database
```bash
# Backup all data
mysqldump -u root -p investment_db > investment_backup.sql

# Backup specific table
mysqldump -u root -p investment_db investment > investment_table.sql
```

### Restore Database
```bash
# Restore from backup
mysql -u root -p investment_db < investment_backup.sql
```

## MySQL Best Practices

✅ Regular backups
✅ Strong passwords
✅ Minimal user privileges (for production)
✅ Connection pooling (via mysql-connector-python)
✅ Index on investment_date for faster queries
✅ Decimal type for financial data (not FLOAT)

## Performance Tips

- Connection is maintained in session state
- Index on investment_date improves query speed
- Use DECIMAL for precision with financial data
- Queries auto-commit after each operation

## Additional Configuration

### Change Port
Edit `.streamlit/config.toml`:
```toml
[server]
port = 8502
```

### Enable External Access
Edit `.streamlit/config.toml`:
```toml
[server]
address = "0.0.0.0"  # From "localhost"
```

### Run with Options
```bash
# Custom port
streamlit run app.py --server.port 8502

# External access
streamlit run app.py --server.address 0.0.0.0

# Logger level
streamlit run app.py --logger.level=debug
```

## Next Steps

1. Verify MySQL setup
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `streamlit run app.py`
4. Open `http://localhost:8501`
5. Create first investment
6. Monitor in MySQL: `SELECT * FROM investment_db.investment;`

---

For more details, see the main README in the parent directory.
