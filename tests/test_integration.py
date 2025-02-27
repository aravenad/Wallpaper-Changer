import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock keyboard module before importing main
sys.modules['keyboard'] = MagicMock()

# Now it's safe to import modules that depend on keyboard
from src import main, config, unsplash_api, wallpaper

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Save original configs
        self.original_img_dir = config.IMG_DIR
        self.original_saved_dir = config.SAVED_DIR
        
        # Set test configs
        config.IMG_DIR = os.path.join(self.temp_dir, "img")
        config.SAVED_DIR = os.path.join(self.temp_dir, "saved")
        
        # Create the img directory
        os.makedirs(config.IMG_DIR, exist_ok=True)
        
        # Create a dummy wallpaper
        self.test_wallpaper = os.path.join(config.IMG_DIR, "wallpaper.jpg")
        with open(self.test_wallpaper, 'wb') as f:
            f.write(b'dummy test wallpaper')
    
    def tearDown(self):
        # Restore original configs
        config.IMG_DIR = self.original_img_dir
        config.SAVED_DIR = self.original_saved_dir
        
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)
    
    @patch('src.wallpaper.set_wallpaper')
    @patch('requests.get')
    def test_update_wallpaper_cmd(self, mock_get, mock_set_wallpaper):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Ratelimit-Remaining": "49"}
        mock_response.json.return_value = {
            "urls": {
                "raw": "https://example.com/image"
            }
        }
        
        # Mock image download response
        mock_img_response = MagicMock()
        mock_img_response.status_code = 200
        mock_img_response.iter_content.return_value = [b'new wallpaper data']
        
        # Configure the mock
        mock_get.side_effect = [mock_response, mock_img_response]
        
        # Call the main update function
        main.requests_remaining = 50
        main.hour_start = None
        main.update_wallpaper_cmd("test", "nature")
        
        # Check if wallpaper was set
        mock_set_wallpaper.assert_called_once()
        
        # Check if rate limit was updated
        self.assertEqual(main.requests_remaining, 49)
        self.assertIsNotNone(main.hour_start)
    
    def test_compute_auto_interval(self):
        # Test fresh start (no hour_start)
        main.hour_start = None
        interval = main.compute_auto_interval()
        self.assertEqual(interval, 90.0)
        
        # Test with limited requests
        main.hour_start = 100  # Some time value
        main.requests_remaining = config.RESERVED_FOR_MANUAL + 1
        interval = main.compute_auto_interval()
        self.assertGreaterEqual(interval, 30.0)
        
        # Test with no usable requests
        main.requests_remaining = config.RESERVED_FOR_MANUAL
        interval = main.compute_auto_interval()
        self.assertEqual(interval, 600.0)

if __name__ == '__main__':
    unittest.main()
