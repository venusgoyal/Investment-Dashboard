"""
Sample data script for Investment Dashboard - Oracle Edition
Generates sample investment records for testing
"""
import os
from oracle_service import InvestmentService
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample investment data"""
    try:
        # Connect to database
        service = InvestmentService(
            db_user=os.getenv('ORACLE_USER', 'system'),
            db_password=os.getenv('ORACLE_PASSWORD', 'oracle'),
            db_host=os.getenv('ORACLE_HOST', 'localhost'),
            db_port=int(os.getenv('ORACLE_PORT', '1521')),
            db_service=os.getenv('ORACLE_SERVICE', 'XEPDB1')
        )
        
        print("Generating sample investment data...\n")
        
        # Sample data
        sample_investments = [
            {
                'amount': 50000,
                'date': (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                'return': 8.5
            },
            {
                'amount': 100000,
                'date': (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                'return': 7.2
            },
            {
                'amount': 75000,
                'date': (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                'return': 9.5
            },
            {
                'amount': 125000,
                'date': (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                'return': 6.8
            },
            {
                'amount': 200000,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'return': 8.0
            },
        ]
        
        # Create investments
        for i, inv in enumerate(sample_investments, 1):
            result = service.create_investment(
                investment_amount=inv['amount'],
                investment_date=inv['date'],
                annual_return_percentage=inv['return']
            )
            print(f"✅ Investment {i} created:")
            print(f"   ID: {result['investment_id']}")
            print(f"   Amount: ₹{inv['amount']:,.2f}")
            print(f"   Date: {inv['date']}")
            print(f"   Annual Return: {inv['return']}%\n")
        
        # Display all investments
        print("\n" + "="*60)
        print("All Sample Investments:")
        print("="*60 + "\n")
        
        all_investments = service.read_all_investments()
        for inv in all_investments:
            from oracle_service import calculate_current_value, calculate_profit_loss
            
            current_val = calculate_current_value(
                inv['investment_amount'],
                inv['annual_return_percentage'],
                inv['investment_date']
            )
            profit_loss = calculate_profit_loss(current_val, inv['investment_amount'])
            
            print(f"Investment ID: {inv['investment_id']}")
            print(f"  Amount: ₹{inv['investment_amount']:,.2f}")
            print(f"  Date: {inv['investment_date']}")
            print(f"  Annual Return: {inv['annual_return_percentage']}%")
            print(f"  Current Value: ₹{current_val:,.2f}")
            print(f"  Profit/Loss: ₹{profit_loss:,.2f}")
            print()
        
        service.close()
        print("✅ Sample data generation completed!")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")

if __name__ == "__main__":
    generate_sample_data()
