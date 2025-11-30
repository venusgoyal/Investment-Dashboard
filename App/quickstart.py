"""
Quick Start Guide - Investment Dashboard

This script demonstrates how to use the Investment Dashboard programmatically
"""

from dynamodb_service import (
    InvestmentService,
    calculate_current_value,
    calculate_profit_loss,
    calculate_return_percentage
)
from datetime import datetime, timedelta

def main():
    print("=" * 60)
    print("Investment Dashboard - Quick Start Guide")
    print("=" * 60)
    
    # Initialize service
    print("\n1. Initializing DynamoDB Service...")
    service = InvestmentService(table_name="Investment", region="ap-south-1")
    print("   ✓ Service initialized")
    
    # Create investments
    print("\n2. Creating sample investments...")
    
    investments_data = [
        {
            "amount": 50000,
            "date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "return": 5.0,
            "description": "1-year investment at 5% annual return"
        },
        {
            "amount": 100000,
            "date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "return": 7.5,
            "description": "6-month investment at 7.5% annual return"
        },
        {
            "amount": 25000,
            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "return": 3.0,
            "description": "1-month investment at 3% annual return"
        }
    ]
    
    created_ids = []
    for inv in investments_data:
        result = service.create_investment(
            investment_amount=inv["amount"],
            investment_date=inv["date"],
            annual_return_percentage=inv["return"]
        )
        created_ids.append(result['investment_id'])
        print(f"   ✓ Created: {inv['description']}")
        print(f"     ID: {result['investment_id']}")
    
    # Read all investments
    print("\n3. Reading all investments...")
    all_investments = service.read_all_investments()
    print(f"   ✓ Total investments: {len(all_investments)}")
    
    # Display investment details
    print("\n4. Investment Details:")
    print("-" * 120)
    print(f"{'Date':<12} {'Amount':>15} {'Annual %':>10} {'Days':>6} {'Current Value':>15} {'Profit/Loss':>15} {'Return %':>10}")
    print("-" * 120)
    
    total_invested = 0
    total_current = 0
    
    for inv in all_investments:
        amount = float(inv.get('investment_amount', 0))
        annual_return = float(inv.get('annual_return_percentage', 0))
        inv_date = inv.get('investment_date', '')
        
        current_val = calculate_current_value(amount, annual_return, inv_date)
        profit_loss = calculate_profit_loss(current_val, amount)
        return_pct = calculate_return_percentage(current_val, amount)
        
        # Calculate days
        inv_date_obj = datetime.strptime(inv_date, "%Y-%m-%d").date()
        days = (datetime.now().date() - inv_date_obj).days
        
        total_invested += amount
        total_current += current_val
        
        print(f"{inv_date:<12} ₹{amount:>14,.2f} {annual_return:>9.2f}% {days:>6} ₹{current_val:>14,.2f} ₹{profit_loss:>14,.2f} {return_pct:>9.2f}%")
    
    print("-" * 120)
    print(f"{'TOTAL':<12} ₹{total_invested:>14,.2f} {'':<10} {'':<6} ₹{total_current:>14,.2f} ₹{(total_current - total_invested):>14,.2f} {calculate_return_percentage(total_current, total_invested):>9.2f}%")
    print("-" * 120)
    
    # Update an investment
    if created_ids:
        print(f"\n5. Updating first investment...")
        investment_id = created_ids[0]
        updated = service.update_investment(
            investment_id=investment_id,
            investment_amount=75000,
            annual_return_percentage=6.0
        )
        print(f"   ✓ Investment updated:")
        print(f"     New Amount: ₹{float(updated['investment_amount']):,.2f}")
        print(f"     New Return %: {float(updated['annual_return_percentage']):.2f}%")
    
    # Delete an investment
    if len(created_ids) > 1:
        print(f"\n6. Deleting an investment...")
        investment_id = created_ids[-1]
        if service.delete_investment(investment_id):
            print(f"   ✓ Investment deleted successfully")
        else:
            print(f"   ✗ Investment not found")
    
    # Final statistics
    print("\n7. Final Statistics:")
    final_investments = service.read_all_investments()
    
    if final_investments:
        total_final_invested = sum(float(inv.get('investment_amount', 0)) for inv in final_investments)
        total_final_current = sum(
            calculate_current_value(
                float(inv.get('investment_amount', 0)),
                float(inv.get('annual_return_percentage', 0)),
                inv.get('investment_date', '')
            )
            for inv in final_investments
        )
        total_final_profit = total_final_current - total_final_invested
        
        print(f"   Total Investments: {len(final_investments)}")
        print(f"   Total Amount Invested: ₹{total_final_invested:,.2f}")
        print(f"   Total Current Value: ₹{total_final_current:,.2f}")
        print(f"   Total Profit/Loss: ₹{total_final_profit:,.2f}")
        print(f"   Overall Return: {calculate_return_percentage(total_final_current, total_final_invested):.2f}%")
    else:
        print("   No investments found")
    
    print("\n" + "=" * 60)
    print("Quick Start Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: streamlit run app.py")
    print("2. Open browser to: http://localhost:8501")
    print("3. Use the dashboard to manage your investments")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured")
        print("2. Ensure DynamoDB table 'Investment' exists in ap-south-1")
        print("3. Check AWS IAM permissions for DynamoDB")
        print("4. Run: aws sts get-caller-identity")
