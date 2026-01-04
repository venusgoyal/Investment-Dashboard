# CockroachDB Investment Dashboard - Quick Start Guide

Get the Investment Dashboard running in 5 minutes!

## Prerequisites

- Python 3.8+
- pip
- CockroachDB connection string from cockroachlabs.cloud

## Quick Start (5 Minutes)

### 1. Install Dependencies (1 min)

```bash
cd app-cockroach-db
pip install -r requirements.txt
```

### 2. Configure Secrets (1 min)

Create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
```

Add your CockroachDB connection string:

```toml
[cockroachdb]
database_url = "postgresql://?sslmode=verify-full"
```

### 3. Run the App (1 min)

```bash
streamlit run app.py
```

**App opens at**: http://localhost:8501

### 4. Create Your First Account (1 min)

1. Click "Register" on the login page
2. Fill in your details:
   - Username: `admin`
   - Email: `admin@example.com`
   - Full Name: `Administrator`
   - Password: (choose a strong password)
3. Click "Register"

Note: Your account will be created but needs admin approval. Since this is your first account, it becomes admin automatically.

### 5. Start Using (1 min)

1. Login with your credentials
2. Click "Dashboard" to see the overview
3. Click "Create" to add your first investment
4. Explore other features!

---

## Connection String Components

Your CockroachDB connection string has this format:

```
postgresql://username:password@host:port/database?sslmode=verify-full
```

**Get your connection string from**:
1. CockroachDB Cloud Console
2. Your cluster page
3. Click "Connect"
4. Copy the PostgreSQL connection string

---

## First Investment Setup

Once logged in, create your first investment:

1. **Navigate to Create**
   - Click "➕ Create" in the sidebar

2. **Enter Investment Details**
   - Amount: `₹10,000` (example)
   - Date: Today's date
   - Annual Return: `7.5` (%)
   - Comments: "My first investment" (optional)

3. **Create Investment**
   - Click "✅ Create Investment"
   - You'll see a success message with balloons! 🎉

4. **View Dashboard**
   - Click "📊 Dashboard"
   - See your investment in the metrics and charts
   - Current value is calculated based on compound interest

---

## Common Tasks

### Add Multiple Investments

1. Click "➕ Create"
2. Repeat the process for each investment
3. Click "Dashboard" to see the complete portfolio

### Update an Investment

1. Click "✏️ Update"
2. Select the investment from dropdown
3. Modify the details
4. Click "✅ Update Investment"

### Delete an Investment

1. Click "🗑️ Delete"
2. Select the investment
3. Review and confirm the deletion

### Manage Users (Admin Only)

1. Click "👨‍💼 Admin Panel"
2. Go to "User Management" tab
3. View all users
4. Toggle user activation status
5. Modify user roles

### Change Your Password

1. Click "👤 Profile"
2. Scroll to "🔐 Security"
3. Enter current and new passwords
4. Click "✅ Change Password"

---

## Understanding the Dashboard

The **Dashboard** page shows:

### Metrics (Top Row)
- **💰 Total Invested**: Sum of all investment amounts
- **📈 Current Value**: Calculated value after growth
- **📊 P/L Amount**: Profit or Loss in rupees
- **📉 ROI %**: Return on Investment percentage

### Charts (Middle Section)
- **Portfolio Composition**: Pie chart showing investment distribution
- **Investment Comparison**: Bar chart of amounts
- **Profit/Loss Distribution**: Shows P/L per investment
- **Annual Return Percentage**: Return rates comparison

### Investment Table (Bottom)
Complete details of all investments with all metrics

---

## Calculation Formula

The app calculates investment growth using compound interest:

```
Current Value = Principal × (1 + Annual Rate)^(Years Passed)
ROI % = ((Current Value - Principal) / Principal) × 100
P/L = Current Value - Principal
```

For example:
- Investment: ₹10,000
- Annual Return: 7.5%
- Time Period: 1 year
- Current Value: ₹10,000 × (1.075)^1 = ₹10,750
- P/L: ₹10,750 - ₹10,000 = ₹750
- ROI: (₹750 / ₹10,000) × 100 = 7.5%

---

## Troubleshooting

### "Connection failed" Error

**Check**:
1. Connection string is correct
2. CockroachDB cluster is active
3. `.streamlit/secrets.toml` exists and has correct content
4. `root.crt` file is in the app-cockroach-db directory

**Solution**:
```bash
# Test your connection
python test_connection.py
```

### "No investments found"

This is normal for new accounts. Click "Create" to add your first investment.

### "Secrets not found"

Ensure `.streamlit/secrets.toml` exists with proper content:
```bash
cat .streamlit/secrets.toml
```

### "Module not found" Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## File Structure

```
app-cockroach-db/
├── app.py                  # Main application
├── cockroach_service.py    # Database layer
├── auth_pages.py           # Login & admin pages
├── requirements.txt        # Python packages
├── root.crt               # SSL certificate
├── .streamlit/
│   └── secrets.toml       # Your config (create this)
├── README.md              # Full documentation
├── DEPLOYMENT.md          # Deployment guide
└── QUICKSTART.md          # This file
```

---

## Next Steps

1. **Explore Features**
   - Test all CRUD operations
   - Check out the analytics
   - Review admin features

2. **Customize**
   - Modify the CSS styling in `app.py`
   - Add new investment categories
   - Create custom reports

3. **Deploy**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
   - Deploy to Streamlit Cloud (free!)
   - Or use Docker for complete control

4. **Scale**
   - Add more users
   - Create investment portfolios
   - Build reporting dashboards

---

## Key Features Checklist

- [ ] ✅ User Registration & Login
- [ ] ✅ User Authentication with password hashing
- [ ] ✅ Admin approval system for new users
- [ ] ✅ Create, Read, Update, Delete investments
- [ ] ✅ Real-time dashboard with metrics
- [ ] ✅ Interactive charts and visualizations
- [ ] ✅ Compound interest calculations
- [ ] ✅ Admin panel with user management
- [ ] ✅ Profile management
- [ ] ✅ Secure CockroachDB connection
- [ ] ✅ Modern, responsive UI
- [ ] ✅ Mobile-friendly design

---

## Support

- **Full Documentation**: See [README.md](README.md)
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **GitHub Issues**: Report bugs and request features
- **CockroachDB Docs**: https://www.cockroachlabs.com/docs/
- **Streamlit Docs**: https://docs.streamlit.io/

---

## Tips & Tricks

**💡 Pro Tips**:

1. **Keyboard Shortcuts**: Press `R` to rerun the app
2. **Keyboard Shortcuts**: Press `?` for Streamlit help
3. **Data Export**: Use your browser's "Save as PDF" for reports
4. **Browser DevTools**: Press F12 to inspect and customize styling
5. **Sidebar**: Click the ">" arrow to collapse sidebar for more space

**🎨 Customization**:

Edit the CSS in `app.py` starting at line ~100 to customize colors, fonts, and styling.

**⚡ Performance**:

For large datasets (1000+ investments):
- Implement pagination
- Use database queries with LIMIT/OFFSET
- Cache dashboard data for 5-10 minutes

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Platform**: CockroachDB with PostgreSQL Driver  
**Status**: ✅ Ready to Use
