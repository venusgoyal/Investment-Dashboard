"""
MySQL service module for Investment table operations
"""
import mysql.connector
from mysql.connector import Error
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Track if tables have been created to avoid running on every initialization
_tables_created = {
    'investment': False,
    'users': False
}

class InvestmentService:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        """Initialize MySQL service with credentials from secrets.toml or parameters"""
        # Use Streamlit secrets if available, otherwise use provided parameters
        if host is None:
            try:
                host = st.secrets["mysql"]["host"]
            except (KeyError, AttributeError):
                host = "localhost"
        
        if port is None:
            try:
                port = st.secrets["mysql"]["port"]
            except (KeyError, AttributeError):
                port = 3306
        
        if user is None:
            try:
                user = st.secrets["mysql"]["user"]
            except (KeyError, AttributeError):
                user = "root"
        
        if password is None:
            try:
                password = st.secrets["mysql"]["password"]
            except (KeyError, AttributeError):
                password = "password"
        
        if database is None:
            try:
                database = st.secrets["mysql"]["database"]
            except (KeyError, AttributeError):
                database = "investment_db"
        
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
        """Establish MySQL connection - reuse for efficiency"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.connection.autocommit = True
            if self.connection.is_connected():
                logger.info("MySQL connection successful")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def create_table(self):
        """Create investment table if it doesn't exist (only once per session)"""
        global _tables_created
        
        # Skip if already created in this session
        if _tables_created['investment']:
            logger.debug("Investment table already created this session")
            return
        
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
            _tables_created['investment'] = True
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


# ==================== USER AUTHENTICATION FUNCTIONS ====================

import hashlib


class AuthenticationService:
    """Service for user authentication and management"""
    
    def __init__(self, config: dict = None):
        """Initialize authentication service
        
        Args:
            config: Database config dict (optional). If not provided, uses secrets.toml
        """
        if config is None:
            # Load from secrets.toml
            try:
                config = {
                    "host": st.secrets["mysql"]["host"],
                    "port": st.secrets["mysql"]["port"],
                    "user": st.secrets["mysql"]["user"],
                    "password": st.secrets["mysql"]["password"],
                    "database": st.secrets["mysql"]["database"]
                }
            except (KeyError, AttributeError):
                # Fallback to defaults if secrets not available
                config = {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "investment_db"
                }
        
        self.config = config
        self.connection = None
        self.connect()
        self.create_users_table()
    
    def connect(self):
        """Establish MySQL connection - reuse for efficiency"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.connection.autocommit = True
            if self.connection.is_connected():
                logger.info("MySQL connection successful for auth service")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def create_users_table(self):
        """Create users table if it doesn't exist (only once per session)"""
        global _tables_created
        
        # Skip if already created in this session
        if _tables_created['users']:
            logger.debug("Users table already created this session")
            return
        
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
                KEY idx_username (username),
                KEY idx_email (email),
                KEY idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            _tables_created['users'] = True
            logger.info("Users table created or already exists")
        except Error as e:
            logger.error(f"Error creating users table: {e}")
            raise
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "", role: str = "user") -> Dict:
        """
        Register a new user
        New users are created with is_active=FALSE and must be activated by admin
        
        Args:
            username: Username
            email: Email address
            password: Password (will be hashed)
            full_name: Full name
            role: User role ('user' or 'admin')
            
        Returns:
            User data with user_id
        """
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO users 
            (user_id, username, email, password_hash, full_name, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
            """
            cursor.execute(insert_query, (user_id, username, email, password_hash, full_name, role))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"User registered (inactive): {username}")
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'role': role,
                'is_active': False
            }
        except Error as e:
            logger.error(f"Error registering user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with username and password
        Only allows active users to login
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User data if authenticated, None otherwise
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                password_hash = self.hash_password(password)
                if user['password_hash'] == password_hash:
                    # Check if user is active
                    if user['is_active']:
                        logger.info(f"User authenticated: {username}")
                        return user
                    else:
                        logger.warning(f"Inactive user tried to login: {username}")
                        return None
            
            return None
        except Error as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    def check_user_status(self, username: str, password: str) -> Dict:
        """
        Check user status (for login feedback)
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Dict with 'exists', 'password_correct', and 'is_active' status
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return {'exists': False, 'password_correct': False, 'is_active': False}
            
            password_hash = self.hash_password(password)
            password_correct = user['password_hash'] == password_hash
            
            return {
                'exists': True,
                'password_correct': password_correct,
                'is_active': user['is_active'],
                'user': user
            }
        except Error as e:
            logger.error(f"Error checking user status: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            logger.error(f"Error getting user: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            logger.error(f"Error getting user: {e}")
            raise
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = "SELECT user_id, username, email, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC"
            cursor.execute(select_query)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            logger.error(f"Error getting users: {e}")
            raise
    
    def update_user_role(self, user_id: str, role: str) -> Optional[Dict]:
        """Update user role"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE users SET role = %s WHERE user_id = %s"
            cursor.execute(update_query, (role, user_id))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"User role updated: {user_id}")
            return self.get_user_by_id(user_id)
        except Error as e:
            logger.error(f"Error updating user role: {e}")
            raise
    
    def toggle_user_status(self, user_id: str) -> Optional[Dict]:
        """Toggle user active status"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            new_status = not user['is_active']
            cursor = self.connection.cursor()
            update_query = "UPDATE users SET is_active = %s WHERE user_id = %s"
            cursor.execute(update_query, (new_status, user_id))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"User status toggled: {user_id}")
            return self.get_user_by_id(user_id)
        except Error as e:
            logger.error(f"Error toggling user status: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM users WHERE user_id = %s"
            cursor.execute(delete_query, (user_id,))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"User deleted: {user_id}")
            return True
        except Error as e:
            logger.error(f"Error deleting user: {e}")
            raise
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            old_password_hash = self.hash_password(old_password)
            if user['password_hash'] != old_password_hash:
                return False
            
            new_password_hash = self.hash_password(new_password)
            cursor = self.connection.cursor()
            update_query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
            cursor.execute(update_query, (new_password_hash, user_id))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Password changed for user: {user_id}")
            return True
        except Error as e:
            logger.error(f"Error changing password: {e}")
            raise

