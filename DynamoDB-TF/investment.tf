# Configure the AWS Provider
terraform {
  backend "s3" {
    key    = "dynamodb-investment-tf/terraform.tfstate"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# You can set your AWS region via the provider block or environment variables (e.g., AWS_REGION)
provider "aws" {
  region = "ap-south-1" # Replace with your desired AWS region
}

# Define the DynamoDB Table resource
resource "aws_dynamodb_table" "investment_table" {
  name           = "Investment"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "investment_id"

  # Define the attribute for the primary key
  attribute {
    name = "investment_id"
    type = "S" # 'S' for String, 'N' for Number, or 'B' for Binary
  }

  # Optional: Add tags for better resource management
  tags = {
    Name        = "InvestmentTable"
    Environment = "Development"
  }
}
