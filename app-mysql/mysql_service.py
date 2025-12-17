"""
MySQL service module for Investment table operations
"""
import mysql.connector
from mysql.connector import Error
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class InvestmentService:
    def __init__(self, host="localhost", port=3306, user="root", password="password", database="investment_db"):
        """Initialize MySQL service"""
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
        self.connection = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                logger.info("MySQL connection successful")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def create_table(self):
        """Create investment table if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS investment (
                investment_id VARCHAR(36) PRIMARY KEY,
                investment_amount DECIMAL(15, 2) NOT NULL,
                investment_date DATE NOT NULL,
                annual_return_percentage DECIMAL(5, 2) NOT NULL,
                investment_comments TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
                INDEX idx_investment_date (investment_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            
            # Add comments column to existing table if it doesn't exist
            try:
                alter_table_query = "ALTER TABLE investment ADD COLUMN investment_comments TEXT"
                cursor.execute(alter_table_query)
                self.connection.commit()
            except Error as e:
                # Column might already exist, which is fine
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add comments column: {e}")
            
            cursor.close()
            logger.info("Investment table created or already exists")
        except Error as e:
            logger.error(f"Error creating table: {e}")
            raise
    
    def create_investment(self, investment_amount: float, investment_date: str, 
                         annual_return_percentage: float, investment_comments: str = "") -> Dict:
        """
        Create a new investment record
        
        Args:
            investment_amount: Amount invested
            investment_date: Date of investment (YYYY-MM-DD format)
            annual_return_percentage: Annual return percentage
            investment_comments: Comments about the investment
            
        Returns:
            Created investment record with investment_id
        """
        investment_id = str(uuid.uuid4())
        
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO investment 
            (investment_id, investment_amount, investment_date, annual_return_percentage, investment_comments)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (investment_id, investment_amount, investment_date, annual_return_percentage, investment_comments))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Investment created: {investment_id}")
            return {
                'investment_id': investment_id,
                'investment_amount': investment_amount,
                'investment_date': investment_date,
                'annual_return_percentage': annual_return_percentage,
                'investment_comments': investment_comments,
                'created_at': datetime.now().isoformat()
            }
        except Error as e:
            logger.error(f"Error creating investment: {e}")
            raise
    
    def read_investment(self, investment_id: str) -> Optional[Dict]:
        """
        Read a specific investment record
        
        Args:
            investment_id: Investment ID to retrieve
            
        Returns:
            Investment record or None if not found
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM investment WHERE investment_id = %s"
            cursor.execute(select_query, (investment_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Error reading investment: {e}")
            raise
    
    def read_all_investments(self) -> List[Dict]:
        """
        Read all investment records
        
        Returns:
            List of all investment records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM investment ORDER BY investment_date DESC"
            cursor.execute(select_query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Error reading investments: {e}")
            raise
    
    def update_investment(self, investment_id: str, investment_amount: Optional[float] = None,
                         investment_date: Optional[str] = None, 
                         annual_return_percentage: Optional[float] = None,
                         investment_comments: Optional[str] = None) -> Optional[Dict]:
        """
        Update an investment record
        
        Args:
            investment_id: Investment ID to update
            investment_amount: New investment amount (optional)
            investment_date: New investment date (optional)
            annual_return_percentage: New annual return percentage (optional)
            investment_comments: New comments (optional)
            
        Returns:
            Updated investment record or None if not found
        """
        # Check if investment exists
        existing = self.read_investment(investment_id)
        if not existing:
            return None
        
        try:
            cursor = self.connection.cursor()
            update_parts = []
            params = []
            
            if investment_amount is not None:
                update_parts.append("investment_amount = %s")
                params.append(investment_amount)
            
            if investment_date is not None:
                update_parts.append("investment_date = %s")
                params.append(investment_date)
            
            if annual_return_percentage is not None:
                update_parts.append("annual_return_percentage = %s")
                params.append(annual_return_percentage)
            
            if investment_comments is not None:
                update_parts.append("investment_comments = %s")
                params.append(investment_comments)
            
            if update_parts:
                update_query = f"UPDATE investment SET {', '.join(update_parts)} WHERE investment_id = %s"
                params.append(investment_id)
                cursor.execute(update_query, params)
                self.connection.commit()
            
            cursor.close()
            
            # Return updated record
            return self.read_investment(investment_id)
        except Error as e:
            logger.error(f"Error updating investment: {e}")
            raise
    
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
        
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM investment WHERE investment_id = %s"
            cursor.execute(delete_query, (investment_id,))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Investment deleted: {investment_id}")
            return True
        except Error as e:
            logger.error(f"Error deleting investment: {e}")
            raise
    
    def close(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")


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
