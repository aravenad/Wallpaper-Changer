import os
import sys
import unittest
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create mock for keyboard and win32gui modules
sys.modules['keyboard'] = MagicMock()
sys.modules['win32gui'] = MagicMock()

from src import main, config

class TestMain(unittest.TestCase):
    
    @patch('time.time')
    def test_compute_auto_interval_fresh_start(self, mock_time):
        # Setup
        mock_time.return_value = 1000
        main.hour_start = None
        main.requests_remaining = config.RATE_LIMIT_PER_HOUR
        
        # Execute
        interval = main.compute_auto_interval()
        
        # Assert
        self.assertEqual(interval, 90.0)
    
    @patch('time.time')
    def test_compute_auto_interval_hour_reset(self, mock_time):
        # Setup
        mock_time.return_value = 5000
        main.hour_start = 1000  # 4000 seconds ago
        main.requests_remaining = 5
        
        # Execute
        interval = main.compute_auto_interval()
        
        # Assert
        self.assertEqual(interval, 90.0)
        self.assertEqual(main.hour_start, 5000)
        self.assertEqual(main.requests_remaining, config.RATE_LIMIT_PER_HOUR)
    
    @patch('time.time')
    def test_compute_auto_interval_no_usable_requests(self, mock_time):
        # Setup
        mock_time.return_value = 1500
        main.hour_start = 1000
        main.requests_remaining = config.RESERVED_FOR_MANUAL
        
        # Execute
        interval = main.compute_auto_interval()
        
        # Assert
        self.assertEqual(interval, 600.0)
    
    @patch('time.time')
    def test_compute_auto_interval_normal(self, mock_time):
        # Setup
        mock_time.return_value = 1500
        main.hour_start = 1000
        usable_requests = 10
        main.requests_remaining = config.RESERVED_FOR_MANUAL + usable_requests
        
        # Execute
        interval = main.compute_auto_interval()
        
        # Assert
        expected_interval = (3600 - 500) / usable_requests
        self.assertEqual(interval, expected_interval)

if __name__ == '__main__':
    unittest.main()
