# Investment Dashboard

A comprehensive Streamlit web application for managing investments with AWS DynamoDB backend. The app provides complete CRUD operations and automatically calculates investment returns based on compound interest.

## Features

✨ **Complete CRUD Operations**
- **Create**: Add new investments with automatic UUID generation
- **Read**: View individual investments or all investments
- **Update**: Modify investment details
- **Delete**: Remove investments with confirmation

📊 **Dashboard Analytics**
- Total invested amount
- Current portfolio value
- Overall profit/loss calculation
- Return percentage calculations
- Real-time metrics

💰 **Investment Calculations**
- Automatic current value calculation based on compound interest
- Formula: `Current Value = Principal × (1 + annual_rate)^(days_passed/365)`
- Days-based return calculation
- Profit/loss analysis
- Return percentage metrics

🗄️ **DynamoDB Integration**
- Serverless database with pay-per-request billing
- Auto-generated investment IDs (UUID)
- Scalable data storage

## Project Structure

```
Investment-Dashboard/
├── App/
│   ├── app.py                 # Main Streamlit application
│   ├── dynamodb_service.py    # DynamoDB operations service
│   ├── requirements.txt       # Python dependencies
│   └── .streamlit/
│       └── config.toml        # Streamlit configuration
├── DynamoDB-TF/
│   ├── investment.tf          # Terraform DynamoDB table definition
│   └── backend-config.tfvars  # Terraform configuration
└── README.md                  # This file
```

## Prerequisites

- Python 3.8+
- AWS Account with credentials configured
- AWS Region set (default: ap-south-1)
- DynamoDB table created (see Deployment section)

## Installation

### 1. Install Python Dependencies

```bash
cd App
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Set up AWS credentials using one of these methods:

**Option A: Environment Variables**
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_REGION = "ap-south-1"
```

**Option B: AWS CLI Configuration**
```bash
aws configure
```

**Option C: Credentials File**
Create `~/.aws/credentials`:
```
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

### 3. Deploy DynamoDB Table

Using Terraform:

```bash
cd DynamoDB-TF
terraform init -backend-config=backend-config.tfvars
terraform plan
terraform apply
```

Or create table manually via AWS Console:
- Table Name: `Investment`
- Primary Key: `investment_id` (String)
- Billing Mode: Pay-per-request

## Running the Application

### Start the Streamlit App

```bash
cd App
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Application Pages

### 📊 Dashboard
- Overview of all investments
- Key metrics: total invested, current value, overall return
- Investment summary table with all details
- Real-time calculations

### ➕ Create
- Add new investment with:
  - Investment amount
  - Investment date
  - Annual return percentage
- Auto-generates unique investment ID
- Shows calculated current value immediately

### 👁️ View All
- List all investments with expandable details
- Shows for each investment:
  - Investment amount
  - Current value
  - Profit/loss
  - Annual return percentage
  - Overall return percentage
  - Investment date
- Investment ID reference

### ✏️ Update
- Select investment to modify
- Update any field:
  - Investment amount
  - Investment date
  - Annual return percentage
- Real-time recalculation

### 🗑️ Delete
- Select investment to delete
- Preview investment details before deletion
- Confirmation to prevent accidental deletion

## Investment Calculation

The app uses the **Compound Interest Formula**:

```
Current Value = Investment Amount × (1 + Annual Rate)^(Years Passed)
```

Where:
- `Annual Rate` = `Annual Return Percentage / 100`
- `Years Passed` = `Days Passed / 365`

### Example
- Investment: ₹10,000
- Annual Return: 5% per year
- Days Passed: 365 (1 year)
- Current Value = 10,000 × (1.05)^1 = ₹10,500
- Profit/Loss = ₹500
- Return % = 5%

## Database Schema

### Investment Table

| Field | Type | Description |
|-------|------|-------------|
| investment_id | String (PK) | Unique identifier (UUID) |
| investment_amount | Number | Amount invested in rupees |
| investment_date | String | Date of investment (YYYY-MM-DD) |
| annual_return_percentage | Number | Annual return percentage |
| created_at | String | Creation timestamp (ISO format) |
| updated_at | String | Last update timestamp (ISO format) |

## Configuration

### Streamlit Configuration
Edit `.streamlit/config.toml` to customize:
- Theme (light/dark)
- Page layout
- Sidebar state
- Font size

Example:
```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[client]
showErrorDetails = true
```

### DynamoDB Region
Default region is `ap-south-1`. To change:

In `dynamodb_service.py`:
```python
self.dynamodb = boto3.resource('dynamodb', region_name='your-region')
```

## Error Handling

The application includes comprehensive error handling:
- AWS credential validation
- DynamoDB connectivity checks
- Input validation
- Transaction error handling
- User-friendly error messages

## Performance Considerations

- **Scanning**: For large datasets (>1MB), implement pagination
- **Indexing**: Consider adding GSI for filtering by date
- **Caching**: Session state reduces repeated queries
- **Pagination**: Implemented in `read_all_investments()` method

## Security Best Practices

✅ Use AWS IAM roles instead of hardcoded credentials  
✅ Enable DynamoDB encryption at rest  
✅ Use VPC endpoints for DynamoDB  
✅ Enable CloudTrail for audit logging  
✅ Set appropriate DynamoDB table permissions  
✅ Never commit credentials to version control  

## Troubleshooting

### Issue: "Import 'boto3' could not be resolved"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: AWS Credentials Error
**Solution**: Verify credentials are configured
```bash
aws sts get-caller-identity
```

### Issue: DynamoDB Connection Error
**Solution**: Check table exists and region is correct
```bash
aws dynamodb list-tables --region ap-south-1
```

### Issue: Import Error for streamlit_option_menu
**Solution**: Install the specific package
```bash
pip install streamlit-option-menu
```

## API Reference

### InvestmentService Class

```python
# Initialize service
service = InvestmentService(table_name="Investment", region="ap-south-1")

# Create investment
investment = service.create_investment(
    investment_amount=10000,
    investment_date="2024-01-15",
    annual_return_percentage=5.5
)

# Read single investment
investment = service.read_investment(investment_id)

# Read all investments
investments = service.read_all_investments()

# Update investment
updated = service.update_investment(
    investment_id,
    investment_amount=12000,
    investment_date="2024-01-20",
    annual_return_percentage=6.0
)

# Delete investment
success = service.delete_investment(investment_id)
```

### Calculation Functions

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
profit = calculate_profit_loss(current_value=10500, investment_amount=10000)

# Calculate return percentage
return_pct = calculate_return_percentage(current_value=10500, investment_amount=10000)
```

## Advanced Features

### Bulk Operations
To import multiple investments:
```python
investments_data = [
    {"amount": 5000, "date": "2024-01-01", "return": 4.5},
    {"amount": 10000, "date": "2024-02-01", "return": 5.5},
]

for inv in investments_data:
    service.create_investment(
        investment_amount=inv["amount"],
        investment_date=inv["date"],
        annual_return_percentage=inv["return"]
    )
```

### Export to CSV
```python
import pandas as pd

investments = service.read_all_investments()
df = pd.DataFrame(investments)
df.to_csv('investments_export.csv', index=False)
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please:
- Check the Troubleshooting section
- Review AWS documentation
- Check Streamlit documentation
- Submit an issue with details

## Future Enhancements

- [ ] Multi-currency support
- [ ] Portfolio visualization charts
- [ ] Goal-based investment tracking
- [ ] Recurring investment support
- [ ] Risk analysis and recommendations
- [ ] Email notifications
- [ ] Mobile app version
- [ ] Advanced filtering and sorting

---

**Last Updated**: November 2024  
**Version**: 1.0  
**Status**: Production Ready
