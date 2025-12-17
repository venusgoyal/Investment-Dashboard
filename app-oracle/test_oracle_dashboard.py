"""
Unit tests for Investment Dashboard - Oracle Edition
"""
import pytest
import os
from datetime import datetime, timedelta
from oracle_service import (
    InvestmentService,
    calculate_current_value,
    calculate_profit_loss,
    calculate_return_percentage
)

@pytest.fixture
def service():
    """Create a test service instance"""
    try:
        svc = InvestmentService(
            db_user=os.getenv('ORACLE_USER', 'system'),
            db_password=os.getenv('ORACLE_PASSWORD', 'oracle'),
            db_host=os.getenv('ORACLE_HOST', 'localhost'),
            db_port=int(os.getenv('ORACLE_PORT', '1521')),
            db_service=os.getenv('ORACLE_SERVICE', 'XEPDB1')
        )
        yield svc
        svc.close()
    except Exception as e:
        pytest.skip(f"Oracle database not available: {e}")

class TestCalculations:
    """Test investment calculation functions"""
    
    def test_calculate_current_value_zero_return(self):
        """Test current value with 0% return"""
        result = calculate_current_value(
            investment_amount=100000,
            annual_return_percentage=0,
            investment_date=datetime.now().strftime("%Y-%m-%d")
        )
        assert result == 100000.0
    
    def test_calculate_current_value_positive_return(self):
        """Test current value with positive return"""
        past_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        result = calculate_current_value(
            investment_amount=100000,
            annual_return_percentage=10,
            investment_date=past_date
        )
        # Should be approximately 110000 after 1 year at 10%
        assert 109900 < result < 110100
    
    def test_calculate_profit_loss(self):
        """Test profit/loss calculation"""
        result = calculate_profit_loss(
            current_value=125000,
            investment_amount=100000
        )
        assert result == 25000.0
    
    def test_calculate_return_percentage(self):
        """Test return percentage calculation"""
        result = calculate_return_percentage(
            current_value=120000,
            investment_amount=100000
        )
        assert result == 20.0
    
    def test_calculate_return_percentage_zero_investment(self):
        """Test return percentage with zero investment"""
        result = calculate_return_percentage(
            current_value=100000,
            investment_amount=0
        )
        assert result == 0.0

class TestCRUDOperations:
    """Test CRUD operations"""
    
    def test_create_investment(self, service):
        """Test creating an investment"""
        result = service.create_investment(
            investment_amount=50000,
            investment_date=datetime.now().strftime("%Y-%m-%d"),
            annual_return_percentage=8.0
        )
        
        assert result is not None
        assert result['investment_amount'] == 50000
        assert result['annual_return_percentage'] == 8.0
        assert result['investment_id'] is not None
        
        # Clean up
        service.delete_investment(result['investment_id'])
    
    def test_read_investment(self, service):
        """Test reading an investment"""
        # Create test investment
        created = service.create_investment(
            investment_amount=75000,
            investment_date=datetime.now().strftime("%Y-%m-%d"),
            annual_return_percentage=7.5
        )
        
        # Read it back
        read_result = service.read_investment(created['investment_id'])
        
        assert read_result is not None
        assert read_result['investment_id'] == created['investment_id']
        assert read_result['investment_amount'] == 75000
        
        # Clean up
        service.delete_investment(created['investment_id'])
    
    def test_read_nonexistent_investment(self, service):
        """Test reading non-existent investment"""
        result = service.read_investment('nonexistent-id')
        assert result is None
    
    def test_update_investment(self, service):
        """Test updating an investment"""
        # Create test investment
        created = service.create_investment(
            investment_amount=50000,
            investment_date=datetime.now().strftime("%Y-%m-%d"),
            annual_return_percentage=8.0
        )
        
        # Update it
        updated = service.update_investment(
            investment_id=created['investment_id'],
            investment_amount=60000,
            annual_return_percentage=9.0
        )
        
        assert updated is not None
        assert updated['investment_amount'] == 60000
        assert updated['annual_return_percentage'] == 9.0
        
        # Clean up
        service.delete_investment(created['investment_id'])
    
    def test_delete_investment(self, service):
        """Test deleting an investment"""
        # Create test investment
        created = service.create_investment(
            investment_amount=50000,
            investment_date=datetime.now().strftime("%Y-%m-%d"),
            annual_return_percentage=8.0
        )
        
        # Delete it
        result = service.delete_investment(created['investment_id'])
        assert result is True
        
        # Verify it's deleted
        read_result = service.read_investment(created['investment_id'])
        assert read_result is None
    
    def test_read_all_investments(self, service):
        """Test reading all investments"""
        # Create multiple test investments
        ids = []
        for i in range(3):
            result = service.create_investment(
                investment_amount=50000 + (i * 10000),
                investment_date=datetime.now().strftime("%Y-%m-%d"),
                annual_return_percentage=8.0 + i
            )
            ids.append(result['investment_id'])
        
        # Read all
        all_investments = service.read_all_investments()
        assert len(all_investments) >= 3
        
        # Clean up
        for inv_id in ids:
            service.delete_investment(inv_id)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
