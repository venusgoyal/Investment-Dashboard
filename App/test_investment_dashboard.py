"""
Unit Tests for Investment Dashboard
Run with: pytest test_investment_dashboard.py -v
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from dynamodb_service import (
    InvestmentService,
    calculate_current_value,
    calculate_profit_loss,
    calculate_return_percentage
)


# ==================== Calculation Tests ====================

class TestCalculations:
    """Test investment calculation functions"""
    
    def test_calculate_current_value_one_year(self):
        """Test current value calculation for exactly 1 year"""
        # Investment: 10,000, Return: 5% for 1 year
        amount = 10000
        annual_return = 5
        
        # Create date exactly 365 days ago
        inv_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        current_value = calculate_current_value(amount, annual_return, inv_date)
        expected = 10000 * (1.05 ** 1)
        
        assert abs(current_value - expected) < 1, f"Expected ~{expected}, got {current_value}"
    
    def test_calculate_current_value_no_days_passed(self):
        """Test current value when no days have passed"""
        amount = 10000
        annual_return = 5
        inv_date = date.today().strftime("%Y-%m-%d")
        
        current_value = calculate_current_value(amount, annual_return, inv_date)
        
        # Should equal investment amount when no time has passed
        assert abs(current_value - amount) < 0.01
    
    def test_calculate_current_value_six_months(self):
        """Test current value calculation for 6 months"""
        amount = 10000
        annual_return = 12  # 12% annual
        
        inv_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        current_value = calculate_current_value(amount, annual_return, inv_date)
        
        # 180 days = 0.493 years (180/365)
        expected = 10000 * (1.12 ** (180/365))
        
        assert abs(current_value - expected) < 100
    
    def test_calculate_current_value_future_date(self):
        """Test current value when investment date is in future"""
        amount = 10000
        annual_return = 5
        inv_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        current_value = calculate_current_value(amount, annual_return, inv_date)
        
        # Should return initial amount for future dates
        assert current_value == amount
    
    def test_calculate_profit_loss_positive(self):
        """Test profit calculation"""
        current_value = 11000
        investment_amount = 10000
        
        profit = calculate_profit_loss(current_value, investment_amount)
        
        assert profit == 1000
    
    def test_calculate_profit_loss_negative(self):
        """Test loss calculation"""
        current_value = 9500
        investment_amount = 10000
        
        loss = calculate_profit_loss(current_value, investment_amount)
        
        assert loss == -500
    
    def test_calculate_return_percentage(self):
        """Test return percentage calculation"""
        current_value = 11000
        investment_amount = 10000
        
        return_pct = calculate_return_percentage(current_value, investment_amount)
        
        assert return_pct == 10.0
    
    def test_calculate_return_percentage_zero_investment(self):
        """Test return percentage with zero investment"""
        current_value = 100
        investment_amount = 0
        
        return_pct = calculate_return_percentage(current_value, investment_amount)
        
        assert return_pct == 0.0
    
    def test_calculate_return_percentage_zero_return(self):
        """Test return percentage when no return"""
        current_value = 10000
        investment_amount = 10000
        
        return_pct = calculate_return_percentage(current_value, investment_amount)
        
        assert return_pct == 0.0


# ==================== Service Tests ====================

class TestInvestmentService:
    """Test DynamoDB service operations"""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock service"""
        with patch('dynamodb_service.boto3'):
            service = InvestmentService()
            service.table = MagicMock()
            return service
    
    def test_create_investment(self, mock_service):
        """Test creating a new investment"""
        amount = 10000
        date_str = "2024-01-15"
        annual_return = 5.5
        
        result = mock_service.create_investment(
            investment_amount=amount,
            investment_date=date_str,
            annual_return_percentage=annual_return
        )
        
        # Verify put_item was called
        mock_service.table.put_item.assert_called_once()
        
        # Verify returned item has correct structure
        assert 'investment_id' in result
        assert result['investment_amount'] == Decimal(str(amount))
        assert result['investment_date'] == date_str
        assert result['annual_return_percentage'] == Decimal(str(annual_return))
    
    def test_read_investment_found(self, mock_service):
        """Test reading an existing investment"""
        investment_id = "test-id-123"
        mock_investment = {
            'investment_id': investment_id,
            'investment_amount': Decimal('10000'),
            'investment_date': '2024-01-15',
            'annual_return_percentage': Decimal('5.5')
        }
        
        mock_service.table.get_item.return_value = {'Item': mock_investment}
        
        result = mock_service.read_investment(investment_id)
        
        assert result == mock_investment
        mock_service.table.get_item.assert_called_once_with(
            Key={'investment_id': investment_id}
        )
    
    def test_read_investment_not_found(self, mock_service):
        """Test reading non-existent investment"""
        mock_service.table.get_item.return_value = {}
        
        result = mock_service.read_investment("non-existent")
        
        assert result is None
    
    def test_read_all_investments(self, mock_service):
        """Test reading all investments"""
        mock_investments = [
            {'investment_id': 'id1', 'investment_amount': Decimal('10000')},
            {'investment_id': 'id2', 'investment_amount': Decimal('20000')}
        ]
        
        mock_service.table.scan.return_value = {'Items': mock_investments}
        
        result = mock_service.read_all_investments()
        
        assert len(result) == 2
        assert result == mock_investments
    
    def test_read_all_investments_with_pagination(self, mock_service):
        """Test reading all investments with pagination"""
        page1 = {'Items': [{'investment_id': 'id1'}], 'LastEvaluatedKey': 'key1'}
        page2 = {'Items': [{'investment_id': 'id2'}]}
        
        mock_service.table.scan.side_effect = [page1, page2]
        
        result = mock_service.read_all_investments()
        
        assert len(result) == 2
        assert mock_service.table.scan.call_count == 2
    
    def test_update_investment_found(self, mock_service):
        """Test updating an existing investment"""
        investment_id = "test-id"
        new_amount = 15000
        
        # Mock existing investment
        mock_service.table.get_item.return_value = {'Item': {'investment_id': investment_id}}
        
        # Mock update return
        updated_item = {
            'investment_id': investment_id,
            'investment_amount': Decimal(str(new_amount))
        }
        mock_service.table.update_item.return_value = {'Attributes': updated_item}
        
        result = mock_service.update_investment(
            investment_id=investment_id,
            investment_amount=new_amount
        )
        
        assert result is not None
        assert result['investment_amount'] == Decimal(str(new_amount))
        mock_service.table.update_item.assert_called_once()
    
    def test_update_investment_not_found(self, mock_service):
        """Test updating non-existent investment"""
        mock_service.table.get_item.return_value = {}
        
        result = mock_service.update_investment(
            investment_id="non-existent",
            investment_amount=15000
        )
        
        assert result is None
        mock_service.table.update_item.assert_not_called()
    
    def test_delete_investment_found(self, mock_service):
        """Test deleting an existing investment"""
        investment_id = "test-id"
        mock_service.table.get_item.return_value = {'Item': {'investment_id': investment_id}}
        
        result = mock_service.delete_investment(investment_id)
        
        assert result is True
        mock_service.table.delete_item.assert_called_once()
    
    def test_delete_investment_not_found(self, mock_service):
        """Test deleting non-existent investment"""
        mock_service.table.get_item.return_value = {}
        
        result = mock_service.delete_investment("non-existent")
        
        assert result is False
        mock_service.table.delete_item.assert_not_called()


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests (these require actual DynamoDB setup)"""
    
    @pytest.mark.skip(reason="Requires actual DynamoDB connection")
    def test_full_crud_cycle(self):
        """Test complete CRUD cycle"""
        service = InvestmentService()
        
        # Create
        result = service.create_investment(10000, "2024-01-15", 5.0)
        investment_id = result['investment_id']
        assert investment_id is not None
        
        # Read
        read_result = service.read_investment(investment_id)
        assert read_result is not None
        assert read_result['investment_id'] == investment_id
        
        # Update
        updated = service.update_investment(investment_id, investment_amount=12000)
        assert updated['investment_amount'] == Decimal('12000')
        
        # Delete
        deleted = service.delete_investment(investment_id)
        assert deleted is True


# ==================== Test Running ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
