# AWS Configuration Guide for Investment Dashboard

## Prerequisites

- AWS Account
- AWS CLI installed (optional, for easier configuration)
- Python 3.8+

## AWS Credentials Setup

### Option 1: AWS CLI (Recommended)

Install AWS CLI if not already installed:
```bash
choco install awscli -y  # Windows with Chocolatey
# or
pip install awscliv2     # Using pip
```

Configure credentials:
```bash
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (use: `ap-south-1`)
- Default output format (use: `json`)

Verify configuration:
```bash
aws sts get-caller-identity
```

### Option 2: Environment Variables (Windows PowerShell)

```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
$env:AWS_REGION = "ap-south-1"
```

To make these persistent, add them to your system environment variables:
1. Search "Edit environment variables"
2. Click "Environment Variables"
3. Add new User variables with the values above

### Option 3: Credentials File

Create file: `C:\Users\YourUsername\.aws\credentials`

```ini
[default]
aws_access_key_id = your-access-key-id
aws_secret_access_key = your-secret-access-key

[production]
aws_access_key_id = your-production-key-id
aws_secret_access_key = your-production-secret-key
```

Create file: `C:\Users\YourUsername\.aws\config`

```ini
[default]
region = ap-south-1
output = json

[profile production]
region = us-east-1
output = json
```

### Option 4: IAM Role (AWS EC2/Lambda)

If running on AWS EC2, Lambda, or other services:
- Attach appropriate IAM role with DynamoDB permissions
- No credentials needed in the application

## Required IAM Permissions

The user/role needs these DynamoDB permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:ap-south-1:*:table/Investment"
        }
    ]
}
```

## Creating AWS Access Keys

1. Log in to [AWS Console](https://aws.amazon.com/console/)
2. Go to IAM → Users
3. Select your user
4. Go to "Security credentials" tab
5. Click "Create access key"
6. Choose "Other" as use case
7. Copy **Access Key ID** and **Secret Access Key**
8. Keep these secure - never commit to version control!

## Terraform Setup for DynamoDB

### Prerequisites
- Terraform installed (version >= 1.0)
- AWS credentials configured
- S3 bucket for Terraform state (optional but recommended)

### First Time Setup

```bash
cd DynamoDB-TF

# Initialize Terraform
terraform init -backend-config=backend-config.tfvars

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply
```

### Using Without Remote State

If you don't have an S3 backend configured:

1. Comment out the `backend "s3"` block in `investment.tf`
2. Initialize without backend config:
   ```bash
   terraform init
   ```

### Verify Table Creation

```bash
aws dynamodb list-tables --region ap-south-1
aws dynamodb describe-table --table-name Investment --region ap-south-1
```

### Cleanup

To delete the table (WARNING: This deletes all data):

```bash
terraform destroy
```

## Running the Application

After setup, run:

```bash
cd App
streamlit run app.py
```

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution**: Verify AWS credentials are set:
```bash
aws sts get-caller-identity
```

If no output, credentials aren't configured. Follow the setup steps above.

### Issue: "NoCredentialsError"

**Solution**: Check credential priority (in order):
1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. IAM role (if on AWS service)
3. ~/.aws/credentials file
4. ~/.aws/config file

### Issue: "UnauthorizedOperation" for DynamoDB

**Solution**: Verify IAM permissions include required DynamoDB actions

### Issue: "ResourceNotFoundException" - Table not found

**Solution**: Ensure DynamoDB table "Investment" exists in ap-south-1 region

### Issue: "ValidationException" - Invalid table name

**Solution**: Table name must be exactly "Investment" (case-sensitive)

## Security Best Practices

⚠️ **Never commit credentials to version control**

1. Add to `.gitignore`:
   ```
   .aws/
   *.env
   .env.local
   aws_credentials.txt
   ```

2. Use AWS Temporary Credentials when possible
3. Rotate access keys regularly
4. Use IAM roles instead of long-term credentials
5. Enable MFA for AWS Console access
6. Monitor credential usage in CloudTrail

## Regional Configuration

Default region: `ap-south-1` (Asia Pacific - Mumbai)

To use a different region:

1. **Update Terraform**:
   Edit `DynamoDB-TF/investment.tf`:
   ```terraform
   provider "aws" {
     region = "us-east-1"  # Change region
   }
   ```

2. **Update Application**:
   Edit `App/dynamodb_service.py`:
   ```python
   self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
   ```

3. **Update Environment Variable**:
   ```bash
   $env:AWS_REGION = "us-east-1"
   ```

## Available Regions

Popular regions:
- `us-east-1` - N. Virginia (most services available)
- `us-west-2` - Oregon
- `eu-west-1` - Ireland
- `ap-south-1` - Mumbai (default for this project)
- `ap-southeast-1` - Singapore

[Full region list](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)

## Multi-Environment Setup

### Development
```bash
$env:AWS_PROFILE = "dev"
$env:AWS_REGION = "ap-south-1"
```

### Production
```bash
$env:AWS_PROFILE = "prod"
$env:AWS_REGION = "ap-south-1"
```

## Advanced: MFA with AWS CLI

To require MFA:

```bash
aws configure set mfa_serial arn:aws:iam::123456789012:mfa/your-device-name
```

## Getting Help

- AWS Documentation: https://docs.aws.amazon.com/
- Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Streamlit Documentation: https://docs.streamlit.io/

---

**Last Updated**: November 2024
