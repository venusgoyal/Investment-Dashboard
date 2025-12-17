"""
Oracle Database service module for Investment table operations
"""
import cx_Oracle
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class InvestmentService:
    def __init__(self, db_user: str, db_password: str, db_host: str, 
                 db_port: int = 1521, db_service: str = "XEPDB1"):
        """
        Initialize Oracle database service
        
        Args:
            db_user: Database username
            db_password: Database password
            db_host: Database host/IP address
            db_port: Database port (default: 1521)
            db_service: Database service name (default: XEPDB1)
        """
        try:
            # Create connection string
            dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service)
            self.connection = cx_Oracle.connect(
                user=db_user,
                password=db_password,
                dsn=dsn,
                encoding="UTF-8"
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            
            # Initialize table
            self._create_table()
            logger.info("Oracle database connection established")
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Oracle connection error: {e}")
            raise
    
    def _create_table(self):
        """Create investment table if it doesn't exist"""
        try:
            # Check if table exists
            self.cursor.execute("""
                SELECT COUNT(*) FROM user_tables 
                WHERE table_name = 'INVESTMENT'
            """)
            
            if self.cursor.fetchone()[0] == 0:
                # Create table if it doesn't exist
                self.cursor.execute("""
                    CREATE TABLE Investment (
                        investment_id VARCHAR2(36) PRIMARY KEY,
                        investment_amount NUMBER(15, 2) NOT NULL,
                        investment_date VARCHAR2(10) NOT NULL,
                        annual_return_percentage NUMBER(5, 2) NOT NULL,
                        created_at TIMESTAMP DEFAULT SYSDATE,
                        updated_at TIMESTAMP DEFAULT SYSDATE
                    )
                """)
                logger.info("Investment table created successfully")
            else:
                logger.info("Investment table already exists")
                
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error creating table: {e}")
            raise
    
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
        
        try:
            self.cursor.execute("""
                INSERT INTO Investment 
                (investment_id, investment_amount, investment_date, 
                 annual_return_percentage, created_at, updated_at)
                VALUES (:1, :2, :3, :4, SYSDATE, SYSDATE)
            """, [investment_id, float(investment_amount), investment_date, 
                  float(annual_return_percentage)])
            
            self.connection.commit()
            
            return {
                'investment_id': investment_id,
                'investment_amount': investment_amount,
                'investment_date': investment_date,
                'annual_return_percentage': annual_return_percentage,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error creating investment: {e}")
            self.connection.rollback()
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
            self.cursor.execute("""
                SELECT investment_id, investment_amount, investment_date,
                       annual_return_percentage, created_at, updated_at
                FROM Investment
                WHERE investment_id = :1
            """, [investment_id])
            
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'investment_id': row[0],
                    'investment_amount': float(row[1]),
                    'investment_date': row[2],
                    'annual_return_percentage': float(row[3]),
                    'created_at': str(row[4]),
                    'updated_at': str(row[5])
                }
            return None
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error reading investment: {e}")
            raise
    
    def read_all_investments(self) -> List[Dict]:
        """
        Read all investment records
        
        Returns:
            List of all investment records
        """
        try:
            self.cursor.execute("""
                SELECT investment_id, investment_amount, investment_date,
                       annual_return_percentage, created_at, updated_at
                FROM Investment
                ORDER BY investment_date DESC
            """)
            
            rows = self.cursor.fetchall()
            investments = []
            
            for row in rows:
                investments.append({
                    'investment_id': row[0],
                    'investment_amount': float(row[1]),
                    'investment_date': row[2],
                    'annual_return_percentage': float(row[3]),
                    'created_at': str(row[4]),
                    'updated_at': str(row[5])
                })
            
            return investments
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error reading all investments: {e}")
            raise
    
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
        
        try:
            # Build dynamic UPDATE statement
            update_fields = ["updated_at = SYSDATE"]
            params = []
            
            if investment_amount is not None:
                update_fields.append("investment_amount = :1")
                params.append(float(investment_amount))
            
            if investment_date is not None:
                update_fields.append(f"investment_date = :{len(params) + 1}")
                params.append(investment_date)
            
            if annual_return_percentage is not None:
                update_fields.append(f"annual_return_percentage = :{len(params) + 1}")
                params.append(float(annual_return_percentage))
            
            params.append(investment_id)
            
            update_sql = f"""
                UPDATE Investment
                SET {', '.join(update_fields)}
                WHERE investment_id = :{len(params)}
            """
            
            self.cursor.execute(update_sql, params)
            self.connection.commit()
            
            # Return updated record
            return self.read_investment(investment_id)
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error updating investment: {e}")
            self.connection.rollback()
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
            self.cursor.execute("""
                DELETE FROM Investment
                WHERE investment_id = :1
            """, [investment_id])
            
            self.connection.commit()
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error deleting investment: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        """Close database connection"""
        try:
            self.cursor.close()
            self.connection.close()
            logger.info("Database connection closed")
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Error closing connection: {e}")


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
