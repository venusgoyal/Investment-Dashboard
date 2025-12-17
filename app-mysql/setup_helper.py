"""
Setup verification script for MySQL Investment Dashboard
"""
import sys
import mysql.connector
from mysql.connector import Error
import os

def check_mysql_connection():
    """Check if MySQL is accessible"""
    print("🔍 Checking MySQL connection...")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="password",
            database="investment_db"
        )
        if connection.is_connected():
            print("   ✅ MySQL connection successful")
            
            # Check if table exists
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'investment' AND table_schema = 'investment_db'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result[0] > 0:
                print("   ✅ Investment table exists")
            else:
                print("   ⚠️  Investment table not found (will be auto-created)")
            
            connection.close()
            return True
    except Error as e:
        print(f"   ❌ MySQL error: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = {
        'mysql.connector': 'mysql-connector-python',
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'streamlit_option_menu': 'streamlit-option-menu',
    }
    
    all_installed = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - Install with: pip install {package_name}")
            all_installed = False
    
    return all_installed

def check_python_version():
    """Check Python version"""
    print("\n🔍 Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version.split()[0]}")
        return True
    else:
        print(f"   ❌ Python {sys.version.split()[0]} (3.8+ required)")
        return False

def check_app_files():
    """Check if required app files exist"""
    print("\n🔍 Checking app files...")
    
    required_files = [
        'app.py',
        'mysql_service.py',
        'requirements.txt',
        '.streamlit/config.toml',
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Not found")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Investment Dashboard - MySQL Setup Verification")
    print("=" * 60 + "\n")
    
    checks = {
        "Python Version": check_python_version(),
        "Python Packages": check_python_packages(),
        "App Files": check_app_files(),
        "MySQL Connection": check_mysql_connection(),
    }
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_pass = True
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_pass = False
    
    print("=" * 60)
    
    if all_pass:
        print("\n✅ All checks passed!")
        print("\n🚀 You can now run:")
        print("   python quickstart.py     # Load sample data")
        print("   streamlit run app.py      # Start the application")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\n📝 Setup instructions:")
        print("   1. Install Python 3.8+")
        print("   2. Install MySQL Server")
        print("   3. Create database: CREATE DATABASE investment_db;")
        print("   4. Install packages: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
