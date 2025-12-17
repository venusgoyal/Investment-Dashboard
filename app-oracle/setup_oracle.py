"""
Oracle Database setup script for Investment table
Run this script to initialize the Oracle database schema
"""
import cx_Oracle
import os
import sys

def setup_oracle_database():
    """Create Investment table in Oracle database"""
    try:
        # Get connection parameters from environment
        db_user = os.getenv('ORACLE_USER', 'system')
        db_password = os.getenv('ORACLE_PASSWORD', 'oracle')
        db_host = os.getenv('ORACLE_HOST', 'localhost')
        db_port = int(os.getenv('ORACLE_PORT', '1521'))
        db_service = os.getenv('ORACLE_SERVICE', 'XEPDB1')
        
        print(f"Connecting to Oracle Database...")
        print(f"  Host: {db_host}:{db_port}")
        print(f"  Service: {db_service}")
        print(f"  User: {db_user}")
        
        # Create connection
        dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service)
        connection = cx_Oracle.connect(
            user=db_user,
            password=db_password,
            dsn=dsn,
            encoding="UTF-8"
        )
        
        cursor = connection.cursor()
        print("✅ Connected to Oracle Database")
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) FROM user_tables 
            WHERE table_name = 'INVESTMENT'
        """)
        
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            print("⚠️ Investment table already exists")
            
            # Ask if user wants to drop and recreate
            response = input("Do you want to drop and recreate the table? (yes/no): ")
            if response.lower() == 'yes':
                cursor.execute("DROP TABLE Investment")
                connection.commit()
                print("✅ Dropped existing Investment table")
            else:
                print("Skipping table creation")
                cursor.close()
                connection.close()
                return
        
        # Create table
        cursor.execute("""
            CREATE TABLE Investment (
                investment_id VARCHAR2(36) PRIMARY KEY,
                investment_amount NUMBER(15, 2) NOT NULL,
                investment_date VARCHAR2(10) NOT NULL,
                annual_return_percentage NUMBER(5, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT SYSDATE,
                updated_at TIMESTAMP DEFAULT SYSDATE
            )
        """)
        
        connection.commit()
        print("✅ Investment table created successfully")
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX idx_investment_date 
            ON Investment(investment_date)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_created_at 
            ON Investment(created_at)
        """)
        
        connection.commit()
        print("✅ Indexes created successfully")
        
        cursor.close()
        connection.close()
        print("\n✅ Database setup completed successfully!")
        
    except cx_Oracle.DatabaseError as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_oracle_database()
