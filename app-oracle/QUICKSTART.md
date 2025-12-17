# Oracle Edition - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd app-oracle
pip install -r requirements.txt
```

### Step 2: Configure Oracle Connection (2 min)

**Option A: Environment Variables (PowerShell)**
```powershell
$env:ORACLE_USER = "system"
$env:ORACLE_PASSWORD = "your_password"
$env:ORACLE_HOST = "localhost"
$env:ORACLE_PORT = "1521"
$env:ORACLE_SERVICE = "XEPDB1"
```

**Option B: .env File**
```
ORACLE_USER=system
ORACLE_PASSWORD=your_password
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
```

### Step 3: Initialize Database (1 min)
```bash
python setup_oracle.py
```

### Step 4: Run Application (1 min)
```bash
streamlit run app.py
```

Application opens automatically at: `http://localhost:8501`

## First Use

1. **Dashboard**: View empty dashboard (no investments yet)
2. **Create**: Add your first investment
3. **View All**: See your investment with live calculations
4. **Update**: Modify your investment
5. **Delete**: Remove the investment

## Sample Data

To load test data:
```bash
python sample_data.py
```

Creates 5 sample investments with different dates and returns.

## Verify Installation

```bash
# Test database connection
python -c "from oracle_service import InvestmentService; print('✅ Oracle connection OK')"

# Run tests
pytest test_oracle_dashboard.py -v
```

## What's Different from DynamoDB Version?

| Aspect | Change |
|--------|--------|
| **Driver** | `boto3` → `cx-Oracle` |
| **Credentials** | AWS IAM → Oracle user/password |
| **Table** | DynamoDB → Oracle RDBMS |
| **Connection** | AWS SDK → Native Oracle |
| **UI & Logic** | 🟢 Identical - No changes |

## Troubleshooting

**Q: "ORA-12514: TNS:listener does not currently know of service"**
A: Check ORACLE_SERVICE name. Run in SQL*Plus:
```sql
SELECT name FROM v$database;
```

**Q: "Module not found: cx_Oracle"**
A: Install with: `pip install cx-Oracle`

**Q: "Connection refused"**
A: Verify Oracle is running and reachable at ORACLE_HOST:ORACLE_PORT

## Next Steps

- Load sample data: `python sample_data.py`
- Run tests: `pytest test_oracle_dashboard.py`
- Deploy with Docker: See DOCKER_DEPLOYMENT.md
- Deploy on EC2: See EC2_DEPLOYMENT.md

## Key Files

- **app.py** (900+ lines): Main Streamlit dashboard
- **oracle_service.py** (400+ lines): Database operations
- **requirements.txt**: Dependencies (5 packages)
- **setup_oracle.py**: Schema initialization
- **sample_data.py**: Test data generator
- **test_oracle_dashboard.py**: Unit tests

---

**Ready to go!** Start the app and create your first investment. 🚀
