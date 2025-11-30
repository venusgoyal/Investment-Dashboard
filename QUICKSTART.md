# Quick Start Guide - Investment Dashboard

## 🚀 Getting Started in 5 Minutes

### Step 1: Prerequisites
- Python 3.8+
- AWS Account
- AWS Credentials configured

### Step 2: Install Dependencies
```bash
cd Investment-Dashboard\App
pip install -r requirements.txt
```

### Step 3: Configure AWS
```bash
# Option 1: Using AWS CLI
aws configure
# Enter your credentials and set region to ap-south-1

# Option 2: Environment Variables (PowerShell)
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
$env:AWS_REGION = "ap-south-1"
```

### Step 4: Create DynamoDB Table
```bash
cd ..\DynamoDB-TF
terraform init
terraform apply
```

Or create manually on AWS Console:
- Table Name: `Investment`
- Primary Key: `investment_id` (String)
- Billing: On-demand

### Step 5: Run the Application
```bash
cd ..\App
streamlit run app.py
```

App opens at `http://localhost:8501`

## 📊 Using the Dashboard

### Dashboard Tab
- View all investments
- See total portfolio value
- Track overall returns

### Create Tab
- Add new investment
- Auto-generated ID (UUID)
- Enter: Amount, Date, Annual Return %

### View All Tab
- List all investments with details
- Expandable cards for each investment

### Update Tab
- Select investment
- Modify any field
- Real-time calculation update

### Delete Tab
- Select investment
- Confirm deletion
- Prevents accidental removal

## 💡 Example Investment

**Input:**
- Amount: ₹50,000
- Date: 2024-01-15 (started 365 days ago)
- Annual Return: 5%

**Calculation:**
- Current Value = 50,000 × (1.05)^1 = ₹52,500
- Profit = ₹2,500
- Return % = 5%

## 🔧 Testing with Sample Data

Run the quick start script to create sample investments:

```bash
python quickstart.py
```

This will:
- Create 3 sample investments
- Show calculations
- Update an investment
- Delete an investment
- Display statistics

## 📁 Project Structure

```
Investment-Dashboard/
├── App/
│   ├── app.py                    # Main Streamlit app
│   ├── dynamodb_service.py       # DynamoDB operations
│   ├── quickstart.py             # Sample script
│   ├── requirements.txt          # Dependencies
│   └── .streamlit/
│       └── config.toml           # Streamlit config
├── DynamoDB-TF/
│   ├── investment.tf             # Terraform config
│   └── backend-config.tfvars    # Backend config
├── README.md                     # Full documentation
├── AWS_SETUP_GUIDE.md           # AWS setup details
└── QUICKSTART.md                # This file
```

## 🐛 Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### AWS Credentials Error
```bash
aws sts get-caller-identity
```

If no output, credentials aren't set. See AWS_SETUP_GUIDE.md

### "Table not found" Error
```bash
aws dynamodb list-tables --region ap-south-1
```

If Investment table not shown, create it via Terraform or AWS Console

### Port 8501 Already in Use
```bash
streamlit run app.py --server.port 8502
```

## 📚 Key Features

✅ **CRUD Operations** - Full Create, Read, Update, Delete  
✅ **Auto Calculations** - Compound interest formula  
✅ **Real-time Updates** - Instant value recalculation  
✅ **Serverless** - No infrastructure management  
✅ **Scalable** - DynamoDB grows with your data  
✅ **Beautiful UI** - Streamlit dashboard  
✅ **Error Handling** - Comprehensive error messages  

## 🔐 Security Notes

⚠️ Never commit AWS credentials  
✅ Use IAM roles when possible  
✅ Rotate access keys regularly  
✅ Use environment variables for secrets  

## 📞 Need Help?

1. Check README.md for detailed documentation
2. See AWS_SETUP_GUIDE.md for AWS configuration
3. Run quickstart.py to test the system
4. Check CloudWatch logs for errors

## 📈 Next Steps

After setup:
1. Add your investments
2. Monitor returns in dashboard
3. Update investments as needed
4. Export data to CSV (see README)

---

**Happy Investing! 📊💰**
