# Investment Dashboard - MySQL Quick Reference

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify setup
python setup_helper.py

# 3. Load sample data
python quickstart.py

# 4. Run application
streamlit run app.py
```

🎯 Open: http://localhost:8501

## 📋 Common Commands

### Local Development

| Command | Purpose |
|---------|---------|
| `streamlit run app.py` | Start application |
| `python setup_helper.py` | Verify installation |
| `python quickstart.py` | Load sample data |
| `python -m pytest test_investment_dashboard.py` | Run tests |

### Docker

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start containers |
| `docker-compose down` | Stop containers |
| `docker-compose logs -f` | View logs |
| `docker-compose ps` | Container status |
| `docker-compose restart` | Restart services |

### MySQL

| Command | Purpose |
|---------|---------|
| `mysql -u root -p` | Connect to MySQL |
| `mysql -u root -p investment_db < mysql_schema.sql` | Create schema |
| `mysql -u root -p -e "USE investment_db; SELECT * FROM investment;"` | Query data |
| `mysqldump -u root -p investment_db > backup.sql` | Backup database |

### Systemd Service (EC2)

| Command | Purpose |
|---------|---------|
| `sudo systemctl start investment-dashboard.service` | Start service |
| `sudo systemctl stop investment-dashboard.service` | Stop service |
| `sudo systemctl restart investment-dashboard.service` | Restart service |
| `sudo systemctl status investment-dashboard.service` | View status |
| `journalctl -u investment-dashboard.service -f` | View logs |

## 🛠️ Troubleshooting

### MySQL Not Connecting
```bash
# Verify MySQL is running
mysql -u root -p -e "SELECT 1;"

# Check if investment_db exists
mysql -u root -p -e "SHOW DATABASES;"

# Create database if missing
mysql -u root -p -e "CREATE DATABASE investment_db;"
```

### Port 8501 Already in Use
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

### Streamlit Won't Start
```bash
# Verify Python version (3.8+)
python --version

# Verify dependencies
pip list | grep streamlit

# Install missing dependencies
pip install -r requirements.txt
```

### Docker Issues
```bash
# Verify Docker is running
docker ps

# Check container logs
docker-compose logs investment-streamlit
docker-compose logs investment-mysql

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

## 📊 Database Info

### Connection Details
- **Host:** localhost
- **Port:** 3306  
- **User:** root
- **Password:** password
- **Database:** investment_db

### Table Structure
```sql
CREATE TABLE investment (
    investment_id VARCHAR(36) PRIMARY KEY,
    investment_amount DECIMAL(15, 2),
    investment_date DATE,
    annual_return_percentage DECIMAL(5, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Quick Queries
```sql
-- View all investments
SELECT * FROM investment;

-- Count investments
SELECT COUNT(*) FROM investment;

-- Sum invested amount
SELECT SUM(investment_amount) FROM investment;

-- Latest investments
SELECT * FROM investment ORDER BY created_at DESC LIMIT 5;

-- Find by date range
SELECT * FROM investment WHERE investment_date BETWEEN '2024-01-01' AND '2024-12-31';
```

## 📂 File Structure

```
app-mysql/
├── app.py                       # Main application
├── mysql_service.py             # Database layer
├── requirements.txt             # Dependencies
├── .streamlit/config.toml      # Streamlit config
├── Dockerfile                   # Docker image
├── docker-compose.yml          # Docker services
├── test_investment_dashboard.py # Tests
├── quickstart.py               # Sample data loader
├── setup_helper.py             # Setup validator
├── mysql_schema.sql            # Database schema
├── README.md                   # Full documentation
├── MYSQL_SETUP.md             # Setup guide
├── MYSQL_DEPLOYMENT.md        # Deployment guide
├── deploy.sh                   # Deploy script
├── health-check.sh            # Health check
├── restart.sh                 # Restart script
├── logs.sh                    # View logs
└── update.sh                  # Update script
```

## 🔧 Configuration

### Change MySQL Credentials
Edit `mysql_service.py` line ~20:
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",           # Change here
    "password": "password",   # Change here
    "database": "investment_db"
}
```

### Change Streamlit Settings
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"       # Primary color
font = "sans serif"            # Font

[server]
port = 8501                    # Port
headless = true                # Headless mode
```

### Change App Port
```bash
# Method 1: Config file
# Edit .streamlit/config.toml: port = 8502

# Method 2: Command line
streamlit run app.py --server.port 8502

# Method 3: Environment variable
export STREAMLIT_SERVER_PORT=8502
streamlit run app.py
```

## 💡 Usage Tips

### Create Investment
1. Open "Create" page
2. Enter amount, date, return %
3. Click "Create Investment"
4. ✅ Investment added with calculated value

### View Investments
1. Open "View All" page
2. See all investments in expandable list
3. Each shows: amount, date, return %, current value, profit/loss

### Update Investment
1. Open "Update" page
2. Select investment from dropdown
3. Modify details
4. Click "Update Investment"
5. ✅ Changes saved and recalculated

### Delete Investment
1. Open "Delete" page
2. Select investment
3. Review details
4. Click "Delete Investment"
5. ✅ Deleted permanently

## 📈 Calculation Formulas

### Current Value
$$\text{Current Value} = P \times \left(1 + \frac{r}{100}\right)^{\frac{d}{365.25}}$$

Where:
- P = Principal (investment amount)
- r = Annual return percentage
- d = Days passed since investment

### Profit/Loss
$$\text{Profit/Loss} = \text{Current Value} - P$$

### Return Percentage
$$\text{Return %} = \frac{\text{Current Value} - P}{P} \times 100$$

## 🐳 Docker Deployment

### Start Services
```bash
docker-compose up -d
```

### Access Application
```
http://localhost:8501
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Images
```bash
docker-compose up -d --build
```

## ☁️ EC2 Deployment

### Deploy
```bash
./deploy.sh
```

### Monitor
```bash
./health-check.sh
journalctl -u investment-dashboard.service -f
```

### Restart
```bash
./restart.sh
```

### Update
```bash
./update.sh
```

## 🔐 Security

### Production Checklist
- [ ] Change default MySQL password
- [ ] Use environment variables for credentials
- [ ] Enable SSL/TLS
- [ ] Restrict security group rules
- [ ] Set strong passwords
- [ ] Enable regular backups
- [ ] Monitor logs
- [ ] Use read-only database users for reports

### Use Environment Variables
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=secure_password
export MYSQL_DATABASE=investment_db
```

Then update code:
```python
import os
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| mysql-connector-python | ≥8.0.33 | MySQL driver |
| streamlit | ≥1.28.0 | Web framework |
| pandas | ≥2.0.0 | Data manipulation |
| streamlit-option-menu | ≥0.3.5 | Navigation menu |
| python-dateutil | ≥2.8.2 | Date utilities |

## 🆘 Support

### Get Help
1. Check [README.md](README.md)
2. Read [MYSQL_SETUP.md](MYSQL_SETUP.md)
3. Review [MYSQL_DEPLOYMENT.md](MYSQL_DEPLOYMENT.md)
4. Run `python setup_helper.py`

### Common Issues

| Issue | Solution |
|-------|----------|
| MySQL won't connect | Check credentials, verify MySQL is running |
| Port in use | Change port or kill existing process |
| Module not found | Run `pip install -r requirements.txt` |
| Table not created | Run `mysql_schema.sql` manually |
| Docker won't start | Check Docker is installed and running |

## 📞 Quick Links

- **Dashboard:** http://localhost:8501
- **MySQL Docs:** https://dev.mysql.com/doc/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Docker Docs:** https://docs.docker.com/

## 📝 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop application/server |
| `Ctrl+D` | Exit Python shell |
| `Ctrl+L` | Clear terminal |
| `R` | Rerun Streamlit app |

---

**Last Updated:** 2024  
**Quick Reference v1.0**
