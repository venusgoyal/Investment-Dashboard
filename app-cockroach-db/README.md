# Investment Dashboard - CockroachDB Edition

## Overview

This is the CockroachDB (PostgreSQL) version of the Investment Dashboard - a secure, full-featured Streamlit application for managing and tracking investments with user authentication, role-based access control, and real-time analytics.

## Features

### User Management
- **User Registration & Authentication**: Secure login system with password hashing
- **Role-Based Access Control**: Admin and User roles with different permissions
- **Account Activation**: New users require admin approval before accessing investment features
- **Profile Management**: Users can view and update their profiles, change passwords
- **Admin Panel**: Manage users, toggle activation status, assign roles

### Investment Management
- **Create**: Add new investments with amount, date, expected return percentage
- **Read**: View all investments with detailed analytics
- **Update**: Modify investment details
- **Delete**: Remove investments with confirmation

### Analytics & Visualization
- **Dashboard**: Real-time metrics including total invested, current value, P/L, ROI%
- **Charts**: 
  - Portfolio composition (pie chart)
  - Investment comparison (bar charts)
  - Profit/Loss distribution
  - Return percentage analysis
- **Detailed Reports**: Comprehensive investment table with all metrics

### Security
- **SSL/TLS Support**: Secure connection to CockroachDB using verified SSL certificates
- **PostgreSQL Compatibility**: Uses psycopg2 for robust database connectivity
- **Password Hashing**: SHA-256 hashing for user passwords
- **Session Management**: Streamlit session state for secure user tracking

## Architecture

### Directory Structure
```
app-cockroach-db/
├── app.py                  # Main Streamlit application
├── cockroach_service.py    # Database service layer (PostgreSQL/CockroachDB)
├── auth_pages.py           # Authentication and admin pages
├── requirements.txt        # Python dependencies
├── root.crt               # SSL certificate for CockroachDB connection
├── .streamlit/
│   └── secrets.toml       # Configuration (create locally, don't commit)
└── README.md              # This file
```

### Technology Stack
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with psycopg2 PostgreSQL driver
- **Database**: CockroachDB (PostgreSQL compatible)
- **Visualization**: Plotly for interactive charts
- **UI Components**: streamlit-option-menu for navigation

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- CockroachDB cloud account (cockroachlabs.cloud)
- An active CockroachDB cluster with connection credentials

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd Investment-Dashboard/app-cockroach-db
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create Streamlit secrets configuration**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   [cockroachdb]
   database_url = "postgresql://?sslmode=verify-full"
   ```
   
   **OR** use individual parameters:
   ```toml
   [cockroachdb]
   host = ""
   port = 26257
   user = ""
   password = ""
   database = ""
   sslmode = "verify-full"
   ```

5. **Verify SSL certificate**
   - The `root.crt` file is included in the repository
   - It's required for secure connection to CockroachDB
   - Place it in the `app-cockroach-db` directory (already there)

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## Configuration

### Streamlit Cloud Deployment

1. **Push your code to GitHub**

2. **Create Streamlit Cloud app**
   - Go to [https://share.streamlit.io](https://share.streamlit.io)
   - Create a new app from your GitHub repository
   - Point to `app-cockroach-db/app.py`

3. **Add secrets in Streamlit Cloud**
   - In app settings, go to "Secrets"
   - Add your CockroachDB connection string:
   ```toml
   [cockroachdb]
   database_url = "postgresql://?sslmode=verify-full"
   ```

### Environment Variables (Alternative)

Instead of `secrets.toml`, you can set environment variables:
```bash
export STREAMLIT_COCKROACHDB_DATABASE_URL="postgresql://..."
```

## Database Schema

### Tables

#### users
```sql
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### investment
```sql
CREATE TABLE IF NOT EXISTS investment (
    investment_id UUID PRIMARY KEY,
    investment_amount DECIMAL(15, 2) NOT NULL,
    investment_date DATE NOT NULL,
    annual_return_percentage DECIMAL(5, 2) NOT NULL,
    investment_comments TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### First Time Setup

1. **Register a new account**
   - Click the "Register" tab on the login page
   - Fill in your details
   - Your account will be created but marked as inactive

2. **Admin activation**
   - First user created in the system is automatically made an admin
   - Admin users can activate/deactivate other users
   - Access Admin Panel through the sidebar menu

3. **Dashboard access**
   - Once activated, users can access all investment management features
   - Inactive users can only view their profile

### Daily Usage

**Dashboard**
- View your investment portfolio at a glance
- See total invested, current value, P/L, and ROI%
- View interactive charts and detailed investment table

**Create Investment**
- Click "Create" in the sidebar
- Enter investment amount, date, expected annual return percentage
- Add optional comments/notes
- Click "Create Investment"

**View All**
- See all your investments in expandable sections
- Each section shows detailed metrics for that investment
- Quick overview of amount, current value, P/L, ROI%, and comments

**Update Investment**
- Select an investment from the dropdown
- Modify any field
- Click "Update Investment"

**Delete Investment**
- Select an investment to delete
- Review the details
- Confirm deletion (irreversible action)

**Admin Panel**
- View all users in the system
- Manage user roles (promote to admin/demote to user)
- Toggle user activation status (approve new registrations)
- View system statistics and user breakdown

**Profile**
- View your account information
- Change your password (requires current password)
- See your account status and member since date

## API Reference

### InvestmentService

```python
# Initialize service
service = InvestmentService(database_url="postgresql://...")
# OR
service = InvestmentService(host="...", port=26257, user="...", password="...", database="...")

# CRUD Operations
investment = service.create_investment(amount, date, return_pct, comments)
investment = service.read_investment(investment_id)
investments = service.read_all_investments()
updated = service.update_investment(id, amount, date, return_pct, comments)
deleted = service.delete_investment(investment_id)
```

### AuthenticationService

```python
# Initialize service
auth_service = AuthenticationService(database_url="postgresql://...")

# User management
user = auth_service.register_user(username, email, password, full_name, role)
user = auth_service.authenticate_user(username, password)
status = auth_service.check_user_status(username, password)

# Admin functions
user = auth_service.get_user_by_id(user_id)
user = auth_service.get_user_by_username(username)
users = auth_service.get_all_users()
user = auth_service.update_user_role(user_id, role)
user = auth_service.toggle_user_status(user_id)
deleted = auth_service.delete_user(user_id)
success = auth_service.change_password(user_id, old_pwd, new_pwd)
```

### Calculation Functions

```python
# Calculate investment metrics
current_value = calculate_current_value(amount, annual_return_pct, date_str)
profit_loss = calculate_profit_loss(current_value, invested_amount)
roi_percent = calculate_return_percentage(current_value, invested_amount)
```

## Troubleshooting

### Connection Issues

**"Failed to connect to CockroachDB"**
- Verify your connection string is correct
- Check that your CockroachDB cluster is active
- Ensure root.crt file exists in the app-cockroach-db directory
- Verify SSL mode is set to `verify-full`

**"Certificate verification failed"**
- Ensure root.crt is in the correct location
- Verify file permissions allow reading

### Authentication Issues

**"MySQL credentials not found in secrets"**
- Create `.streamlit/secrets.toml` with proper configuration
- Check that the file is in the correct location: `.streamlit/secrets.toml`
- Restart the Streamlit app after creating secrets

**"User account is awaiting admin approval"**
- Contact an admin to activate your account
- First user in the system is automatically admin

### Data Issues

**"No investments found"**
- This is normal for new accounts
- Click "Create" to add your first investment

**"Error updating/deleting investment"**
- Ensure the investment still exists
- Check database connection is active
- Try refreshing the page

## Performance Tips

1. **Connection Pooling**: The service reuses connections for efficiency
2. **Indexing**: Indexes on common search fields (username, email, investment_date)
3. **Caching**: Streamlit's session state caches loaded data
4. **Lazy Loading**: Charts only render when dashboard is viewed

## Security Best Practices

1. **Never commit secrets.toml** to version control
2. **Use strong passwords** (at least 6 characters, preferably more)
3. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
4. **Enable 2FA** at your CockroachDB cloud account level
5. **Rotate credentials regularly** if sharing accounts
6. **Monitor admin access** - audit admin panel activity

## Differences from MySQL Edition

| Feature | MySQL | CockroachDB |
|---------|-------|------------|
| Driver | mysql-connector-python | psycopg2 |
| Connection | Host/Port based | PostgreSQL connection string |
| SSL/TLS | Optional | Verify-Full (recommended) |
| Data Types | MySQL specific | PostgreSQL standard |
| Scalability | Single instance | Distributed cluster |
| HA/Failover | Requires setup | Built-in |
| Geographic Distribution | N/A | Native multi-region |

## Support & Resources

- **CockroachDB Documentation**: https://www.cockroachlabs.com/docs/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **PostgreSQL psycopg2**: https://www.psycopg.org/
- **Plotly Documentation**: https://plotly.com/python/

## License

This project is provided as-is for educational and commercial use.

## Authors

- **Original MySQL Version**: Investment Dashboard Team
- **CockroachDB Port**: Enhanced with PostgreSQL compatibility and distributed database support

---

**Version**: 1.0
**Last Updated**: January 2026
**Database**: CockroachDB (PostgreSQL Compatible)
