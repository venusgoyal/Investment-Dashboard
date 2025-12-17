#!/bin/bash
# Health check script for Investment Dashboard

STREAMLIT_PORT=8501
MYSQL_HOST="localhost"
MYSQL_PORT=3306

echo "=================================="
echo "Investment Dashboard - Health Check"
echo "=================================="

# Check Streamlit service
echo ""
echo "🔍 Checking Streamlit service on port $STREAMLIT_PORT..."
if curl -s http://localhost:$STREAMLIT_PORT/_stcore/health > /dev/null; then
    echo "✅ Streamlit is healthy"
else
    echo "❌ Streamlit is not responding"
    exit 1
fi

# Check MySQL service
echo ""
echo "🔍 Checking MySQL service on $MYSQL_HOST:$MYSQL_PORT..."
if mysql -h $MYSQL_HOST -u root -ppassword -e "SELECT 1" > /dev/null 2>&1; then
    echo "✅ MySQL is healthy"
else
    echo "❌ MySQL is not responding"
    exit 1
fi

# Check database
echo ""
echo "🔍 Checking investment_db database..."
if mysql -h $MYSQL_HOST -u root -ppassword -e "USE investment_db; SHOW TABLES;" > /dev/null 2>&1; then
    echo "✅ Database is accessible"
else
    echo "❌ Database is not accessible"
    exit 1
fi

# Check investment table
echo ""
echo "🔍 Checking investment table..."
count=$(mysql -h $MYSQL_HOST -u root -ppassword -se "SELECT COUNT(*) FROM investment_db.investment;")
echo "✅ Investment table exists with $count records"

echo ""
echo "=================================="
echo "✅ All health checks passed!"
echo "=================================="
