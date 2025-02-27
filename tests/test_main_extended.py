import json
import time
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
from src.main import update_wallpaper, handle_auto_mode, display_categories, read_requests_log, write_requests_log, fetch_wallpaper

class TestMainExtended:
    @patch('src.main.fetch_wallpaper')
    @patch('src.main.set_wallpaper')
    @patch('src.main.save_current_wallpaper')
    def test_update_wallpaper_basic(self, mock_save, mock_set, mock_fetch):
        # Test basic wallpaper update without saving
        mock_fetch.return_value = {
            'file_path': '/path/to/image.jpg',
            'source_url': 'http://example.com/image.jpg'
        }
        
        result = update_wallpaper()
        
        mock_fetch.assert_called_once()
        mock_set.assert_called_once_with('/path/to/image.jpg')
        mock_save.assert_not_called()  # Should not be called unless save=True
        assert result == '/path/to/image.jpg'
    
    @patch('src.main.fetch_wallpaper')
    @patch('src.main.set_wallpaper')
    @patch('src.main.save_current_wallpaper')
    def test_update_wallpaper_with_save(self, mock_save, mock_set, mock_fetch):
        # Test wallpaper update with saving
        mock_fetch.return_value = {
            'file_path': '/path/to/image.jpg',
            'source_url': 'http://example.com/image.jpg'
        }
        
        result = update_wallpaper(save=True)
        
        mock_fetch.assert_called_once()
        mock_set.assert_called_once_with('/path/to/image.jpg')
        mock_save.assert_called_once()
        assert result == '/path/to/image.jpg'
    
    @patch('src.main.fetch_wallpaper')
    def test_update_wallpaper_failure(self, mock_fetch):
        # Test API failure case
        mock_fetch.return_value = None
        
        result = update_wallpaper()
        
        assert result is None
    
    @patch('src.main.fetch_wallpaper')
    @patch('src.main.set_wallpaper')
    def test_update_wallpaper_with_category(self, mock_set, mock_fetch):
        # Test updating wallpaper with a specific category
        mock_fetch.return_value = {
            'file_path': '/path/to/image.jpg',
            'source_url': 'http://example.com/image.jpg'
        }
        
        result = update_wallpaper(category='nature')
        
        # Updated assertion to match the modified function signature
        mock_fetch.assert_called_once_with('nature', featured=False)
        mock_set.assert_called_once()
        assert result == '/path/to/image.jpg'
    
    @patch('src.main.fetch_wallpaper')
    @patch('src.main.set_wallpaper')
    def test_update_wallpaper_with_search(self, mock_set, mock_fetch):
        # Test updating wallpaper with search terms
        mock_fetch.return_value = {
            'file_path': '/path/to/image.jpg',
            'source_url': 'http://example.com/image.jpg'
        }
        
        result = update_wallpaper(search='mountains,lake')
        
        # Updated assertion to match the modified function signature
        mock_fetch.assert_called_once_with('mountains,lake', featured=False)
        mock_set.assert_called_once()
        assert result == '/path/to/image.jpg'
    
    @patch('src.main.print')
    @patch('src.main.get_categories')
    def test_display_categories(self, mock_get_categories, mock_print):
        mock_get_categories.return_value = ['nature', 'architecture', 'travel']
        
        display_categories()
        
        mock_get_categories.assert_called_once()
        assert mock_print.call_count >= 3  # Should print each category
    
    @patch('os.path.exists')  # Change to direct module path instead of src.main.os
    @patch('builtins.open', new_callable=mock_open, read_data='{"requests": []}')
    def test_read_requests_log_exists(self, mock_file, mock_exists):
        mock_exists.return_value = True
        
        result = read_requests_log('/path/to/logfile')
        
        mock_file.assert_called_once_with('/path/to/logfile', 'r')
        assert result == {'requests': []}
    
    @patch('os.path.exists')  # Change to direct module path
    def test_read_requests_log_not_exists(self, mock_exists):
        mock_exists.return_value = False
        
        result = read_requests_log('/path/to/logfile')
        
        assert result == {'requests': []}
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')  # Add this to mock json.dump directly
    def test_write_requests_log(self, mock_json_dump, mock_file):
        data = {'requests': [{'timestamp': '2023-01-01T12:00:00'}]}
        
        write_requests_log('/path/to/logfile', data)
        
        mock_file.assert_called_once_with('/path/to/logfile', 'w')
        mock_json_dump.assert_called_once()
    
    @patch('src.main.time.sleep')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.update_wallpaper')
    def test_handle_auto_mode(self, mock_update, mock_compute_interval, mock_sleep):
        # Make it run once by raising KeyboardInterrupt after first iteration
        mock_compute_interval.return_value = 60
        mock_sleep.side_effect = KeyboardInterrupt()
        
        handle_auto_mode(300)  # 5 minutes
        
        mock_update.assert_called_once()
        mock_compute_interval.assert_called_once()
        mock_sleep.assert_called_once_with(60)
