"""
Quick start script with sample data for MySQL Investment Dashboard
"""
import sys
from datetime import date, timedelta
from mysql_service import InvestmentService

def main():
    """Add sample investments to the database"""
    
    print("=" * 60)
    print("Investment Dashboard - MySQL Sample Data Loader")
    print("=" * 60)
    
    try:
        # Connect to MySQL
        print("\n📊 Connecting to MySQL...")
        service = InvestmentService(
            host="localhost",
            port=3306,
            user="root",
            password="password",
            database="investment_db"
        )
        print("✅ Connected to MySQL successfully!")
        
        # Sample investments
        sample_investments = [
            {
                "amount": 50000,
                "date": (date.today() - timedelta(days=365)).strftime("%Y-%m-%d"),
                "return": 12.5,
                "description": "Real Estate Investment (1 year old)"
            },
            {
                "amount": 30000,
                "date": (date.today() - timedelta(days=180)).strftime("%Y-%m-%d"),
                "return": 8.0,
                "description": "Stock Portfolio (6 months old)"
            },
            {
                "amount": 20000,
                "date": (date.today() - timedelta(days=90)).strftime("%Y-%m-%d"),
                "return": 5.5,
                "description": "Bonds (3 months old)"
            },
            {
                "amount": 25000,
                "date": (date.today() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "return": 10.0,
                "description": "Mutual Fund (1 month old)"
            },
            {
                "amount": 15000,
                "date": date.today().strftime("%Y-%m-%d"),
                "return": 7.0,
                "description": "Fixed Deposit (Today)"
            },
        ]
        
        # Add sample investments
        print("\n📝 Adding sample investments...")
        for idx, inv in enumerate(sample_investments, 1):
            result = service.create_investment(
                investment_amount=inv["amount"],
                investment_date=inv["date"],
                annual_return_percentage=inv["return"]
            )
            print(f"  {idx}. ✅ {inv['description']}")
            print(f"     ID: {result['investment_id'][:8]}...")
            print(f"     Amount: ₹{inv['amount']:,}")
            print(f"     Return: {inv['return']}%\n")
        
        # Display summary
        print("\n" + "=" * 60)
        print("📊 SAMPLE DATA SUMMARY")
        print("=" * 60)
        
        all_investments = service.read_all_investments()
        print(f"\nTotal investments: {len(all_investments)}")
        print(f"Total invested: ₹{sum([float(inv['investment_amount']) for inv in all_investments]):,.2f}")
        
        # Show all investments
        print("\n📈 All Investments:")
        for inv in all_investments:
            amount = float(inv['investment_amount'])
            annual_return = float(inv['annual_return_percentage'])
            inv_date = inv['investment_date']
            if hasattr(inv_date, 'strftime'):
                inv_date = inv_date.strftime('%Y-%m-%d')
            
            print(f"\n  ID: {inv['investment_id'][:8]}...")
            print(f"  Amount: ₹{amount:,.2f}")
            print(f"  Date: {inv_date}")
            print(f"  Annual Return: {annual_return}%")
        
        service.close()
        
        print("\n" + "=" * 60)
        print("✅ Sample data loaded successfully!")
        print("🚀 Run 'streamlit run app.py' to view the dashboard")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n⚠️  Make sure:")
        print("   1. MySQL is running")
        print("   2. Database 'investment_db' exists")
        print("   3. Credentials are correct")
        print("   4. Dependencies installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
