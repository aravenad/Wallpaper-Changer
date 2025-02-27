# tests/test_unsplash_api.py

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import unsplash_api, config

class TestUnsplashAPI(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for testing
        self.original_img_dir = config.IMG_DIR
        self.temp_dir = tempfile.mkdtemp()
        self.test_img_dir = os.path.join(self.temp_dir, "img")
        config.IMG_DIR = self.test_img_dir
        
    def tearDown(self):
        # Restore original config
        config.IMG_DIR = self.original_img_dir
        # Remove temp directories
        shutil.rmtree(self.temp_dir)
    
    @patch('requests.get')
    def test_fetch_wallpaper_success(self, mock_get):
        # Mock API response
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
        mock_img_response.iter_content.return_value = [b'test image data']
        
        # Configure the mock to return the responses
        mock_get.side_effect = [mock_response, mock_img_response]
        
        # Call the function
        result, rl = unsplash_api.fetch_wallpaper("nature")
        
        # Assertions
        self.assertEqual(rl, "49")
        self.assertIsNotNone(result)
        self.assertTrue(result and os.path.exists(result))
        if result:  # Check if result is not None before using basename
            self.assertEqual(os.path.basename(result), "wallpaper.jpg")
    
    @patch('requests.get')
    def test_fetch_wallpaper_api_error(self, mock_get):
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        # Call the function - it should gracefully handle the exception
        result, rl = unsplash_api.fetch_wallpaper("nature")
        
        # Assert that error was handled correctly
        self.assertIsNone(result)
        self.assertIsNone(rl)
        
        # Verify the mock was called as expected
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_wallpaper_random_category(self, mock_get):
        # Mock API response
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
        mock_img_response.iter_content.return_value = [b'test image data']
        
        # Configure the mock to return the responses
        mock_get.side_effect = [mock_response, mock_img_response]
        
        # Call the function with "random" category
        result, rl = unsplash_api.fetch_wallpaper("random")
        
        # Assert that we didn't set a query parameter
        args, kwargs = mock_get.call_args_list[0]
        self.assertNotIn('query', kwargs['params'])
    
    @patch('random.choice')
    @patch('requests.get')
    def test_fetch_wallpaper_multiple_categories(self, mock_get, mock_choice):
        # Mock random choice to select "nature"
        mock_choice.return_value = "nature"
        
        # Mock API response
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
        mock_img_response.iter_content.return_value = [b'test image data']
        
        # Configure the mock to return the responses
        mock_get.side_effect = [mock_response, mock_img_response]
        
        # Call the function with multiple categories
        categories = ["nature", "space", "architecture"]
        result, rl = unsplash_api.fetch_wallpaper(categories)
        
        # Assert that random.choice was called with the list of categories
        mock_choice.assert_called_once_with(categories)
        
        # Assert that the API was called with the selected category
        args, kwargs = mock_get.call_args_list[0]
        self.assertEqual(kwargs['params']['query'], "nature")

if __name__ == '__main__':
    unittest.main()
