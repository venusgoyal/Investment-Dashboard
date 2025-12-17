# Investment Dashboard - Oracle Edition

## Overview

This is the Oracle Database version of the Investment Dashboard. It provides the same Streamlit interface and functionality as the DynamoDB version, but uses Oracle Database as the backend for data persistence.

## Key Features

- ✅ **5-Page Streamlit Dashboard**: Dashboard, Create, View All, Update, Delete
- ✅ **Complete CRUD Operations**: Full database operations with Oracle
- ✅ **Compound Interest Calculations**: Real-time investment value calculations
- ✅ **Fractional Day Precision**: Accurate calculations using actual days passed
- ✅ **Oracle Database Support**: cx_Oracle driver for Oracle connectivity
- ✅ **Responsive UI**: Clean, modern Streamlit interface
- ✅ **Error Handling**: Comprehensive error management and logging

## Project Structure

```
app-oracle/
├── app.py                      # Main Streamlit application (5 pages)
├── oracle_service.py           # Oracle database service & calculations
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── setup_oracle.py            # Database schema setup script
├── sample_data.py             # Sample data generator
├── test_oracle_dashboard.py   # Unit tests
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Oracle Database (Express Edition 21c or higher)
- Oracle Instant Client (optional, for remote connections)

### Setup Steps

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```powershell
   # PowerShell
   $env:ORACLE_USER = "system"
   $env:ORACLE_PASSWORD = "your_password"
   $env:ORACLE_HOST = "localhost"
   $env:ORACLE_PORT = "1521"
   $env:ORACLE_SERVICE = "XEPDB1"
   ```

   Or create a `.env` file:
   ```
   ORACLE_USER=system
   ORACLE_PASSWORD=your_password
   ORACLE_HOST=localhost
   ORACLE_PORT=1521
   ORACLE_SERVICE=XEPDB1
   ```

3. **Initialize Database Schema**
   ```bash
   python setup_oracle.py
   ```

4. **(Optional) Load Sample Data**
   ```bash
   python sample_data.py
   ```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Database Schema

### Investment Table

```sql
CREATE TABLE Investment (
    investment_id VARCHAR2(36) PRIMARY KEY,
    investment_amount NUMBER(15, 2) NOT NULL,
    investment_date VARCHAR2(10) NOT NULL,
    annual_return_percentage NUMBER(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT SYSDATE,
    updated_at TIMESTAMP DEFAULT SYSDATE
)
```

**Columns:**
- `investment_id`: Unique identifier (UUID format)
- `investment_amount`: Investment amount in rupees
- `investment_date`: Investment date (YYYY-MM-DD format)
- `annual_return_percentage`: Annual return percentage (0-100)
- `created_at`: Record creation timestamp
- `updated_at`: Record last updated timestamp

## Application Pages

### 1. Dashboard (📊)
- **Overview metrics**: Total invested, current value, overall return %
- **Interactive table**: All investments with real-time calculations
- **Quick statistics**: Number of investments and profit/loss

### 2. Create (➕)
- **Input form**: Investment amount, date, annual return percentage
- **Auto-generated ID**: UUID created automatically
- **Instant feedback**: Real-time current value calculation
- **Success notification**: Confirmation with investment ID

### 3. View All (👁️)
- **Expandable cards**: Individual investment details
- **Detailed metrics**: Investment amount, current value, profit/loss, return %
- **Investment IDs**: Quick reference for update/delete operations

### 4. Update (✏️)
- **Investment selection**: Dropdown list of all investments
- **Partial updates**: Update only the fields you want to change
- **Validation**: Automatic data validation before update
- **Confirmation**: Success notification with updated values

### 5. Delete (🗑️)
- **Safe deletion**: Warning before deletion
- **Preview**: Display investment details before deletion
- **Confirmation**: Final confirmation required before deletion
- **Undo protection**: Warning that action cannot be undone

## Calculation Details

### Compound Interest Formula

```
Current Value = Principal × (1 + annual_rate)^(years_passed)
where: years_passed = actual_days_passed / 365.25
```

**Features:**
- Uses actual days passed (not integer approximation)
- Accounts for leap years (365.25 divisor)
- Fractional day precision using timedelta
- Accurate to the second

### Examples

**Example 1: 1-year investment with 10% annual return**
- Principal: ₹100,000
- Annual Return: 10%
- Days Passed: 365
- Current Value: ₹110,000

**Example 2: 6-month investment with 8% annual return**
- Principal: ₹50,000
- Annual Return: 8%
- Days Passed: 182.5
- Current Value: ₹51,955

## Testing

Run the test suite:

```bash
pytest test_oracle_dashboard.py -v
```

**Test Coverage:**
- Calculation functions (current value, profit/loss, return %)
- CRUD operations (create, read, update, delete)
- Error handling
- Edge cases (zero return, zero investment, etc.)

## Troubleshooting

### Connection Issues

**Error: "Oracle connection error"**
- Check Oracle Database is running
- Verify credentials (ORACLE_USER, ORACLE_PASSWORD)
- Verify host and port (ORACLE_HOST, ORACLE_PORT)
- Verify service name (ORACLE_SERVICE)

**Error: "ORA-12514: TNS:listener does not currently know of service"**
- Check ORACLE_SERVICE name is correct
- Run: `SELECT name FROM v$database;` to find service name

### Installation Issues

**Error: "ModuleNotFoundError: No module named 'cx_Oracle'"**
```bash
pip install cx-Oracle
```

**Error: "unable to locate oracle client libraries"**
- Install Oracle Instant Client
- Set LD_LIBRARY_PATH (Linux) or PATH (Windows)
- See: https://cx-oracle.readthedocs.io/

### Database Issues

**Error: "Table already exists"**
- Run setup_oracle.py and choose "yes" when prompted to drop table

**Error: "No investments found"**
- Run sample_data.py to generate test data

## Configuration

### Streamlit Settings (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

### Oracle Connection Parameters

Environment variables can be overridden:
- `ORACLE_USER`: Database username (default: system)
- `ORACLE_PASSWORD`: Database password (default: oracle)
- `ORACLE_HOST`: Database host (default: localhost)
- `ORACLE_PORT`: Database port (default: 1521)
- `ORACLE_SERVICE`: Database service name (default: XEPDB1)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.28.0 | Web UI framework |
| cx-Oracle | >=8.3.0 | Oracle database driver |
| pandas | >=2.0.0 | Data processing |
| streamlit-option-menu | >=0.3.5 | Navigation component |
| python-dateutil | >=2.8.2 | Date utilities |

## Performance Considerations

1. **Indexes**: Table includes indexes on `investment_date` and `created_at`
2. **Connection Pooling**: cx_Oracle provides built-in connection pooling
3. **Query Optimization**: Uses efficient Oracle SQL queries
4. **Data Pagination**: Loads data as needed (not lazy loading for small datasets)

## Differences from DynamoDB Version

| Feature | DynamoDB | Oracle |
|---------|----------|--------|
| Database Type | NoSQL | Relational |
| Driver | boto3 | cx_Oracle |
| Transactions | Limited | Full ACID support |
| Scaling | Auto-scaling | Manual scaling |
| Cost Model | Pay-per-request | Licensing/On-premise |
| Connection | AWS SDK | Native Oracle |

## Migration from DynamoDB

If migrating from the DynamoDB version:

1. Export data from DynamoDB
2. Transform to CSV format
3. Create Oracle schema with `setup_oracle.py`
4. Load data using SQL*Loader or custom script
5. Verify data integrity
6. Update connection parameters

## Support & Documentation

For more information:
- Streamlit Docs: https://docs.streamlit.io/
- cx_Oracle Docs: https://cx-oracle.readthedocs.io/
- Oracle DB Docs: https://docs.oracle.com/
- Python Datetime: https://docs.python.org/3/library/datetime.html

## License

This project is provided as-is for educational and commercial use.

## Version History

- **v2.0** (Oracle Edition)
  - Oracle Database support
  - Same Streamlit UI as DynamoDB version
  - Enhanced documentation
  
- **v1.0** (DynamoDB Edition)
  - Original DynamoDB implementation
  - Full CRUD operations
  - Streamlit dashboard

---

**Last Updated**: 2024
**Database**: Oracle Database 21c+
**Python**: 3.8+
