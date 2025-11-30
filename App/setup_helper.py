#!/usr/bin/env python3
"""
Setup Helper Script - Investment Dashboard
Helps with initial setup and verification
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_pip():
    """Check if pip is available"""
    print("\n🔍 Checking pip...")
    try:
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ pip not found: {e}")
        return False


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found at {requirements_file}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\n🔍 Checking AWS credentials...")
    
    # Check environment variables
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("✅ AWS credentials found in environment variables")
        return True
    
    # Check credentials file
    credentials_file = Path.home() / '.aws' / 'credentials'
    if credentials_file.exists():
        print("✅ AWS credentials file found")
        return True
    
    # Try AWS CLI
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ AWS CLI configured")
            return True
    except Exception:
        pass
    
    print("⚠️  AWS credentials not configured")
    print("   Run: aws configure")
    print("   Or set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION")
    return False


def check_dynamodb_table():
    """Check if DynamoDB Investment table exists"""
    print("\n🔍 Checking DynamoDB table...")
    
    try:
        result = subprocess.run(
            ['aws', 'dynamodb', 'list-tables', '--region', 'ap-south-1'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            if 'Investment' in result.stdout:
                print("✅ DynamoDB table 'Investment' found")
                return True
            else:
                print("⚠️  DynamoDB table 'Investment' not found")
                print("   Create via: terraform apply")
                return False
        else:
            print("⚠️  Could not verify DynamoDB table")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check DynamoDB: {e}")
        return False


def verify_imports():
    """Verify all required packages can be imported"""
    print("\n🔍 Verifying package imports...")
    
    packages = [
        ('streamlit', 'streamlit'),
        ('boto3', 'boto3'),
        ('pandas', 'pandas'),
        ('streamlit_option_menu', 'streamlit_option_menu'),
    ]
    
    all_ok = True
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} not installed")
            all_ok = False
    
    return all_ok


def get_aws_account_info():
    """Get AWS account information"""
    print("\n🔍 Getting AWS account info...")
    
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            print(f"✅ Account ID: {info.get('Account')}")
            print(f"✅ User ARN: {info.get('Arn')}")
            return True
        else:
            print(f"⚠️  Could not retrieve account info")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not retrieve account info: {e}")
        return False


def run_tests():
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    
    test_file = Path(__file__).parent / "test_investment_dashboard.py"
    
    if not test_file.exists():
        print(f"⚠️  Test file not found: {test_file}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_file), '-v'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed")
            print(result.stdout)
            return False
            
    except FileNotFoundError:
        print("⚠️  pytest not installed. Install with: pip install pytest")
        return False
    except Exception as e:
        print(f"⚠️  Error running tests: {e}")
        return False


def print_summary(results):
    """Print setup summary"""
    print("\n" + "=" * 60)
    print("SETUP VERIFICATION SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Python Version", results.get('python', False)),
        ("pip", results.get('pip', False)),
        ("Dependencies Installed", results.get('dependencies', False)),
        ("Package Imports", results.get('imports', False)),
        ("AWS Credentials", results.get('aws_creds', False)),
        ("DynamoDB Table", results.get('dynamodb', False)),
        ("Unit Tests", results.get('tests', False)),
    ]
    
    for check_name, status in checks:
        status_str = "✅" if status else "⚠️" if status is None else "❌"
        print(f"{status_str} {check_name}")
    
    all_critical_ok = all(results.get(key) for key in ['python', 'pip', 'imports'])
    
    print("\n" + "-" * 60)
    if all_critical_ok:
        print("✅ Basic setup is ready!")
        print("\nNext steps:")
        print("1. Ensure DynamoDB table exists (run: terraform apply)")
        print("2. Start the app: streamlit run app.py")
    else:
        print("❌ Setup incomplete. Fix issues above and try again.")
    
    print("=" * 60 + "\n")


def main():
    """Run all setup checks"""
    print("\n" + "=" * 60)
    print("INVESTMENT DASHBOARD - SETUP VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    # Run checks
    results['python'] = check_python_version()
    results['pip'] = check_pip()
    
    if results['pip']:
        results['dependencies'] = install_dependencies()
    
    results['imports'] = verify_imports()
    results['aws_creds'] = check_aws_credentials()
    
    if results['aws_creds']:
        results['dynamodb'] = check_dynamodb_table()
        get_aws_account_info()
    
    if results['imports']:
        results['tests'] = run_tests()
    
    # Print summary
    print_summary(results)
    
    return 0 if results.get('python') and results.get('imports') else 1


if __name__ == "__main__":
    sys.exit(main())
