"""
Unit tests for MySQL-based Investment Dashboard
"""
import unittest
from datetime import datetime, date
from mysql_service import (
    calculate_current_value,
    calculate_profit_loss,
    calculate_return_percentage
)


class TestCalculations(unittest.TestCase):
    """Test calculation functions"""
    
    def test_calculate_current_value_zero_days(self):
        """Test current value with zero days passed"""
        amount = 1000
        annual_return = 10  # 10%
        today = date.today().strftime("%Y-%m-%d")
        
        # At t=0, value should be approximately equal to principal
        current_val = calculate_current_value(amount, annual_return, today)
        self.assertGreater(current_val, amount * 0.99)  # Allow small variance
        self.assertLess(current_val, amount * 1.01)
    
    def test_calculate_current_value_with_positive_return(self):
        """Test current value increases with positive return"""
        amount = 1000
        annual_return = 10  # 10%
        old_date = "2024-12-14"
        
        current_val = calculate_current_value(amount, annual_return, old_date)
        self.assertGreater(current_val, amount)
    
    def test_calculate_current_value_future_date(self):
        """Test current value with future date returns principal"""
        amount = 1000
        annual_return = 10
        future_date = "2099-12-31"
        
        current_val = calculate_current_value(amount, annual_return, future_date)
        self.assertEqual(current_val, amount)
    
    def test_calculate_profit_loss_positive(self):
        """Test profit calculation"""
        current_val = 1100
        amount = 1000
        
        profit = calculate_profit_loss(current_val, amount)
        self.assertEqual(profit, 100)
    
    def test_calculate_profit_loss_negative(self):
        """Test loss calculation"""
        current_val = 900
        amount = 1000
        
        loss = calculate_profit_loss(current_val, amount)
        self.assertEqual(loss, -100)
    
    def test_calculate_return_percentage_positive(self):
        """Test positive return percentage"""
        current_val = 1100
        amount = 1000
        
        return_pct = calculate_return_percentage(current_val, amount)
        self.assertEqual(return_pct, 10.0)
    
    def test_calculate_return_percentage_zero(self):
        """Test return percentage when no change"""
        current_val = 1000
        amount = 1000
        
        return_pct = calculate_return_percentage(current_val, amount)
        self.assertEqual(return_pct, 0.0)
    
    def test_calculate_return_percentage_zero_investment(self):
        """Test return percentage with zero investment"""
        current_val = 100
        amount = 0
        
        return_pct = calculate_return_percentage(current_val, amount)
        self.assertEqual(return_pct, 0.0)
    
    def test_compound_interest_formula(self):
        """Test compound interest calculation"""
        amount = 1000
        annual_return = 10  # 10% annual
        
        # Test 1 year of returns
        old_date = "2023-12-14"
        current_val = calculate_current_value(amount, annual_return, old_date)
        
        # Should be approximately 1100 (1000 * 1.1)
        self.assertGreater(current_val, 1090)
        self.assertLess(current_val, 1110)
    
    def test_multiple_returns(self):
        """Test multiple investments with different returns"""
        investments = [
            (1000, 5, "2024-12-14"),
            (2000, 10, "2024-12-14"),
            (1500, 7, "2024-12-14"),
        ]
        
        total_current = sum([calculate_current_value(*inv) for inv in investments])
        total_invested = sum([inv[0] for inv in investments])
        
        # Total current should be greater than total invested
        self.assertGreater(total_current, total_invested)


class TestDataTypes(unittest.TestCase):
    """Test data type handling"""
    
    def test_float_amounts(self):
        """Test float amounts are handled correctly"""
        amount = 1500.75
        annual_return = 8.5
        
        current_val = calculate_current_value(amount, annual_return, "2024-12-14")
        self.assertIsInstance(current_val, float)
    
    def test_date_string_format(self):
        """Test date string parsing"""
        amount = 1000
        annual_return = 5
        date_str = "2024-06-15"
        
        current_val = calculate_current_value(amount, annual_return, date_str)
        self.assertIsInstance(current_val, float)
        self.assertGreater(current_val, amount)
    
    def test_return_percentage_format(self):
        """Test return percentage is properly formatted"""
        current_val = 1250
        amount = 1000
        
        return_pct = calculate_return_percentage(current_val, amount)
        # Should have 2 decimal places
        self.assertEqual(return_pct, 25.0)


if __name__ == '__main__':
    unittest.main()
