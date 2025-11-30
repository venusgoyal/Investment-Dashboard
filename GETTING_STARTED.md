# 🚀 Investment Dashboard - Complete Getting Started Guide

## Project Overview

A production-ready Streamlit web application with full CRUD operations for managing investments using AWS DynamoDB. The app calculates investment returns using compound interest formula with day-by-day precision.

## ⚡ Quick Start (5 Minutes)

### 1. Verify Prerequisites
```powershell
python --version              # Should be 3.8+
aws --version                 # AWS CLI installed
aws configure                 # AWS credentials set (region: ap-south-1)
```

### 2. Install & Setup
```powershell
cd Investment-Dashboard
cd App

# Install dependencies
pip install -r requirements.txt

# Run setup verification
python setup_helper.py
```

### 3. Create DynamoDB Table
```powershell
cd ..\DynamoDB-TF
terraform init
terraform apply
# Type 'yes' when prompted
```

### 4. Start Application
```powershell
cd ..\App
streamlit run app.py
```

**App opens at: `http://localhost:8501`**

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | Complete documentation (500+ lines) |
| **QUICKSTART.md** | 5-minute quick start |
| **AWS_SETUP_GUIDE.md** | AWS configuration details |
| **IMPLEMENTATION_SUMMARY.md** | Technical implementation |
| **This File** | Getting started guide |

---

## 🎯 Features at a Glance

✅ **Full CRUD Operations**
- Create investments (auto-generated UUID)
- Read single or all investments
- Update investment details
- Delete with confirmation

✅ **Smart Calculations**
- Compound interest formula
- Day-based precision
- Real-time updates
- Profit/loss analysis

✅ **Beautiful Dashboard**
- Portfolio overview
- Investment metrics
- Expandable cards
- Real-time data

✅ **Enterprise-Ready**
- AWS DynamoDB backend
- Serverless architecture
- Error handling
- Security best practices

---

## 📁 Project Structure

```
Investment-Dashboard/
├── App/
│   ├── app.py                    # Main Streamlit app (900+ lines)
│   ├── dynamodb_service.py       # DynamoDB service (250+ lines)
│   ├── setup_helper.py           # Setup verification script
│   ├── quickstart.py             # Sample data script
│   ├── test_investment_dashboard.py  # Unit tests
│   ├── requirements.txt          # Python dependencies
│   └── .streamlit/
│       └── config.toml           # Streamlit settings
│
├── DynamoDB-TF/
│   ├── investment.tf             # Terraform config
│   └── backend-config.tfvars    # Backend settings
│
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
├── AWS_SETUP_GUIDE.md           # AWS setup guide
├── IMPLEMENTATION_SUMMARY.md    # Technical details
├── GETTING_STARTED.md           # This file
└── .gitignore                   # Git ignore rules
```

---

## 🔧 Setup Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] AWS Account created
- [ ] AWS CLI installed
- [ ] Git (optional, for version control)

### Installation
- [ ] Clone/download project
- [ ] Run `pip install -r requirements.txt`
- [ ] Configure AWS credentials: `aws configure`
- [ ] Run `python setup_helper.py` to verify setup

### Infrastructure
- [ ] Create DynamoDB table via Terraform
  ```powershell
  cd DynamoDB-TF
  terraform init
  terraform apply
  ```
- [ ] Verify table exists: `aws dynamodb list-tables --region ap-south-1`

### Testing
- [ ] Run tests: `pytest test_investment_dashboard.py -v`
- [ ] Run sample script: `python quickstart.py`
- [ ] Start app: `streamlit run app.py`

---

## 💻 Application Pages

### 📊 Dashboard
**Purpose**: View portfolio overview
- Total invested amount
- Current portfolio value
- Overall profit/loss
- Return percentage
- Investment summary table

### ➕ Create
**Purpose**: Add new investments
- Enter amount
- Select investment date
- Specify annual return %
- Auto-generated investment ID

### 👁️ View All
**Purpose**: Browse all investments
- Expandable investment cards
- Detailed metrics for each
- Investment date, amount, returns
- Current value calculations

### ✏️ Update
**Purpose**: Modify existing investments
- Select investment from dropdown
- Update any field
- Real-time calculations
- Instant feedback

### 🗑️ Delete
**Purpose**: Remove investments
- Select investment
- Review before delete
- Confirmation dialog
- Prevents accidents

---

## 🧮 How Calculations Work

### Compound Interest Formula
```
Current Value = Principal × (1 + Annual Rate)^(Years Passed)

Where:
- Annual Rate = Annual Return % / 100
- Years Passed = Days Passed / 365
```

### Example Calculation
```
Investment: ₹10,000
Annual Return: 5%
Days Passed: 365 (1 year)

Current Value = 10,000 × (1.05)^(365/365)
              = 10,000 × 1.05
              = ₹10,500

Profit = ₹10,500 - ₹10,000 = ₹500
Return % = (500 / 10,000) × 100 = 5%
```

### Real-World Portfolio Example
```
Investment 1: ₹50,000 → ₹52,500 (5%, 365 days) = +₹2,500
Investment 2: ₹100,000 → ₹103,750 (7.5%, 180 days) = +₹3,750
Investment 3: ₹25,000 → ₹25,062 (3%, 30 days) = +₹62

Portfolio Summary:
Total Invested: ₹175,000
Total Value: ₹181,312
Total Profit: ₹6,312
Overall Return: 3.61%
```

---

## 🗄️ Database Schema

### Investment Table
| Field | Type | Description |
|-------|------|-------------|
| investment_id | String (PK) | UUID auto-generated |
| investment_amount | Number | Amount in rupees |
| investment_date | String | YYYY-MM-DD format |
| annual_return_percentage | Number | Annual return % |
| created_at | String | ISO timestamp |
| updated_at | String | ISO timestamp |

---

## 🔐 Security Setup

### AWS Credentials (Choose One)

**Option 1: AWS CLI (Recommended)**
```powershell
aws configure
# Enter: Access Key ID
# Enter: Secret Access Key
# Enter: Region (ap-south-1)
# Enter: Output format (json)
```

**Option 2: Environment Variables**
```powershell
$env:AWS_ACCESS_KEY_ID = "your-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_REGION = "ap-south-1"
```

**Option 3: Credentials File**
Create: `~/.aws/credentials`
```
[default]
aws_access_key_id = your-key-id
aws_secret_access_key = your-secret-key
```

### Verify Credentials
```powershell
aws sts get-caller-identity
# Should show your AWS account info
```

---

## 🚀 Running the App

### Command Line
```powershell
cd Investment-Dashboard\App
streamlit run app.py
```

### With Custom Port
```powershell
streamlit run app.py --server.port 8502
```

### With Custom Config
```powershell
streamlit run app.py --logger.level=debug
```

### Using Setup Helper (Recommended)
```powershell
python setup_helper.py      # Verify setup
streamlit run app.py        # Start app
```

---

## 🧪 Testing

### Run All Tests
```powershell
cd App
pytest test_investment_dashboard.py -v
```

### Run Specific Test
```powershell
pytest test_investment_dashboard.py::TestCalculations -v
```

### Generate Sample Data
```powershell
python quickstart.py
```

### Run Setup Verification
```powershell
python setup_helper.py
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution**:
```powershell
pip install -r requirements.txt
```

### Issue: "NoCredentialsError"
**Solution**:
```powershell
aws configure
# or
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
```

### Issue: "ResourceNotFoundException: Table not found"
**Solution**:
```powershell
cd DynamoDB-TF
terraform apply
```

### Issue: "Port 8501 already in use"
**Solution**:
```powershell
streamlit run app.py --server.port 8502
```

### Issue: AWS region mismatch
**Solution**: Ensure DynamoDB table is in ap-south-1
```powershell
aws dynamodb describe-table --table-name Investment --region ap-south-1
```

---

## 📝 Common Tasks

### Add New Investment
1. Go to **Create** tab
2. Enter amount
3. Select date
4. Enter annual return %
5. Click "Create Investment"

### View Investment Details
1. Go to **View All** tab
2. Click on investment card
3. See expanded details

### Update Investment
1. Go to **Update** tab
2. Select investment from dropdown
3. Modify fields
4. Click "Update Investment"

### Delete Investment
1. Go to **Delete** tab
2. Select investment from dropdown
3. Review details
4. Click "Delete Investment"
5. Confirm deletion

### Export Data
```python
import pandas as pd
from dynamodb_service import InvestmentService

service = InvestmentService()
investments = service.read_all_investments()
df = pd.DataFrame(investments)
df.to_csv('investments.csv', index=False)
```

---

## 🔄 CRUD Operations API

### Import Service
```python
from dynamodb_service import InvestmentService
service = InvestmentService()
```

### Create
```python
result = service.create_investment(
    investment_amount=50000,
    investment_date="2024-01-15",
    annual_return_percentage=5.5
)
print(result['investment_id'])
```

### Read
```python
# Single investment
investment = service.read_investment('investment-id')

# All investments
all_investments = service.read_all_investments()
```

### Update
```python
updated = service.update_investment(
    investment_id='investment-id',
    investment_amount=75000
)
```

### Delete
```python
deleted = service.delete_investment('investment-id')
```

---

## 📊 Calculation Functions

```python
from dynamodb_service import (
    calculate_current_value,
    calculate_profit_loss,
    calculate_return_percentage
)

# Calculate current value
current = calculate_current_value(
    investment_amount=10000,
    annual_return_percentage=5,
    investment_date="2024-01-15"
)

# Calculate profit/loss
profit = calculate_profit_loss(
    current_value=10500,
    investment_amount=10000
)

# Calculate return percentage
return_pct = calculate_return_percentage(
    current_value=10500,
    investment_amount=10000
)
```

---

## 🎨 Customization

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
```

### Change DynamoDB Region
Edit `dynamodb_service.py`:
```python
self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
```

### Change Page Layout
Edit `app.py`:
```python
st.set_page_config(layout="centered")  # or "wide"
```

---

## 📈 Performance Tips

- **Large Datasets**: Use filtering and pagination
- **Slow Loads**: Check AWS network latency
- **Memory Issues**: Process data in batches
- **Real-time Updates**: Use session state

---

## 🔒 Best Practices

✅ Never commit credentials  
✅ Use IAM roles when possible  
✅ Enable DynamoDB encryption  
✅ Rotate access keys regularly  
✅ Monitor CloudTrail logs  
✅ Use VPC endpoints  
✅ Enable MFA for AWS account  

---

## 📞 Need Help?

1. **Quick Issues**: Check Troubleshooting section
2. **Setup Issues**: See AWS_SETUP_GUIDE.md
3. **Detailed Docs**: See README.md
4. **Technical Details**: See IMPLEMENTATION_SUMMARY.md
5. **AWS Docs**: https://docs.aws.amazon.com/
6. **Streamlit Docs**: https://docs.streamlit.io/

---

## 📊 File Summary

| File | Purpose | Size |
|------|---------|------|
| app.py | Main application | 900+ lines |
| dynamodb_service.py | Backend service | 250+ lines |
| requirements.txt | Dependencies | 5 packages |
| test_investment_dashboard.py | Unit tests | 15+ tests |
| investment.tf | Infrastructure | Terraform |
| setup_helper.py | Setup verification | 300+ lines |
| quickstart.py | Sample script | 150+ lines |
| README.md | Full docs | 500+ lines |

---

## ✨ Key Features Recap

- ✅ Full CRUD operations
- ✅ Auto-generated investment IDs (UUID)
- ✅ Compound interest calculations
- ✅ Day-based precision
- ✅ Real-time updates
- ✅ Beautiful Streamlit dashboard
- ✅ AWS DynamoDB integration
- ✅ Serverless architecture
- ✅ Comprehensive error handling
- ✅ Complete documentation
- ✅ Unit tests included
- ✅ Production-ready code

---

## 🎯 Next Steps

1. ✅ Complete setup checklist
2. ✅ Run `python setup_helper.py`
3. ✅ Create DynamoDB table (Terraform)
4. ✅ Run `python quickstart.py` (optional)
5. ✅ Start app: `streamlit run app.py`
6. ✅ Add your investments
7. ✅ Monitor returns in dashboard

---

## 📄 License & Credits

**Investment Dashboard v1.0**  
Open Source - MIT License  
Created: November 2024  
Status: Production Ready

---

**Congratulations! You're ready to use the Investment Dashboard! 🎉**

For detailed information, refer to the documentation files or start the app with:
```powershell
cd App
streamlit run app.py
```

Happy investing! 📊💰

