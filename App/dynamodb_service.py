"""
DynamoDB service module for Investment table operations
"""
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional

class InvestmentService:
    def __init__(self, table_name: str = "Investment", region: str = "ap-south-1"):
        """Initialize DynamoDB service"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def create_investment(self, investment_amount: float, investment_date: str, 
                         annual_return_percentage: float) -> Dict:
        """
        Create a new investment record
        
        Args:
            investment_amount: Amount invested
            investment_date: Date of investment (YYYY-MM-DD format)
            annual_return_percentage: Annual return percentage
            
        Returns:
            Created investment record with investment_id
        """
        investment_id = str(uuid.uuid4())
        
        item = {
            'investment_id': investment_id,
            'investment_amount': Decimal(str(investment_amount)),
            'investment_date': investment_date,
            'annual_return_percentage': Decimal(str(annual_return_percentage)),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return item
    
    def read_investment(self, investment_id: str) -> Optional[Dict]:
        """
        Read a specific investment record
        
        Args:
            investment_id: Investment ID to retrieve
            
        Returns:
            Investment record or None if not found
        """
        response = self.table.get_item(Key={'investment_id': investment_id})
        return response.get('Item')
    
    def read_all_investments(self) -> List[Dict]:
        """
        Read all investment records
        
        Returns:
            List of all investment records
        """
        response = self.table.scan()
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return items
    
    def update_investment(self, investment_id: str, investment_amount: Optional[float] = None,
                         investment_date: Optional[str] = None, 
                         annual_return_percentage: Optional[float] = None) -> Optional[Dict]:
        """
        Update an investment record
        
        Args:
            investment_id: Investment ID to update
            investment_amount: New investment amount (optional)
            investment_date: New investment date (optional)
            annual_return_percentage: New annual return percentage (optional)
            
        Returns:
            Updated investment record or None if not found
        """
        # Check if investment exists
        existing = self.read_investment(investment_id)
        if not existing:
            return None
        
        update_expression = "SET updated_at = :updated_at"
        expression_values = {":updated_at": datetime.now().isoformat()}
        
        if investment_amount is not None:
            update_expression += ", investment_amount = :amount"
            expression_values[":amount"] = Decimal(str(investment_amount))
        
        if investment_date is not None:
            update_expression += ", investment_date = :date"
            expression_values[":date"] = investment_date
        
        if annual_return_percentage is not None:
            update_expression += ", annual_return_percentage = :return"
            expression_values[":return"] = Decimal(str(annual_return_percentage))
        
        response = self.table.update_item(
            Key={'investment_id': investment_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        return response.get('Attributes')
    
    def delete_investment(self, investment_id: str) -> bool:
        """
        Delete an investment record
        
        Args:
            investment_id: Investment ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Check if investment exists
        existing = self.read_investment(investment_id)
        if not existing:
            return False
        
        self.table.delete_item(Key={'investment_id': investment_id})
        return True


def calculate_current_value(investment_amount: float, annual_return_percentage: float, 
                           investment_date: str) -> float:
    """
    Calculate current value of investment based on compound interest
    
    Formula: Current Value = Principal * (1 + annual_rate)^(years_passed)
    Where years_passed is calculated using actual days passed / 365.25
    
    Args:
        investment_amount: Initial investment amount
        annual_return_percentage: Annual return percentage (e.g., 5 for 5%)
        investment_date: Investment date (YYYY-MM-DD format)
        
    Returns:
        Current value of investment
    """
    from datetime import datetime
    
    # Parse investment date
    inv_date = datetime.strptime(investment_date, "%Y-%m-%d").date()
    today = datetime.now().date()
    
    # Calculate actual days passed (as a timedelta object for precision)
    time_delta = today - inv_date
    
    if time_delta.days < 0:
        # Investment date is in the future
        return investment_amount
    
    # Calculate actual days passed with fractional precision
    actual_days_passed = time_delta.total_seconds() / (24 * 3600)
    
    # Calculate current value using compound interest formula
    # Using 365.25 to account for leap years
    annual_rate = annual_return_percentage / 100
    years_passed = actual_days_passed / 365.25
    
    current_value = investment_amount * ((1 + annual_rate) ** years_passed)
    
    return round(current_value, 2)


def calculate_profit_loss(current_value: float, investment_amount: float) -> float:
    """
    Calculate profit or loss
    
    Args:
        current_value: Current value of investment
        investment_amount: Initial investment amount
        
    Returns:
        Profit/Loss amount
    """
    return round(current_value - investment_amount, 2)


def calculate_return_percentage(current_value: float, investment_amount: float) -> float:
    """
    Calculate return percentage
    
    Args:
        current_value: Current value of investment
        investment_amount: Initial investment amount
        
    Returns:
        Return percentage
    """
    if investment_amount == 0:
        return 0.0
    
    return round(((current_value - investment_amount) / investment_amount) * 100, 2)
