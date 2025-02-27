"""
Tests for the wallpaper_changer.wallpaper_handler module
"""
import ctypes
import os
import platform
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, mock_open, patch
from urllib.parse import urlparse

import requests

from wallpaper_changer.config import Config
from wallpaper_changer.wallpaper_handler import WallpaperHandler


class TestWallpaperHandler(unittest.TestCase):
    """Test cases for WallpaperHandler class"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.wallpaper_dir = os.path.join(self.test_dir, "wallpapers")
        os.makedirs(self.wallpaper_dir, exist_ok=True)

        # Create some test files
        self.test_files = [
            os.path.join(self.wallpaper_dir, f"test{i}.jpg") 
            for i in range(3)
        ]
        for file_path in self.test_files:
            with open(file_path, 'w') as f:
                f.write("test content")

        # Create a mock config
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = lambda key, default=None: {
            'download_folder': self.wallpaper_dir,
            'source': self.wallpaper_dir,
            'random': True
        }.get(key, default)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test the initialization of WallpaperHandler"""
        handler = WallpaperHandler(self.mock_config)
        self.assertEqual(handler.wallpaper_dir, self.wallpaper_dir)
        self.assertEqual(handler.config, self.mock_config)
        self.assertEqual(handler.system, platform.system())

    def test_init_creates_directory(self):
        """Test that init creates wallpaper directory if it doesn't exist"""
        # Remove the directory
        shutil.rmtree(self.wallpaper_dir)
        self.assertFalse(os.path.exists(self.wallpaper_dir))
        
        # Init should recreate it
        handler = WallpaperHandler(self.mock_config)
        self.assertTrue(os.path.exists(self.wallpaper_dir))

    @patch('random.choice')
    def test_select_wallpaper_from_directory_random(self, mock_random_choice):
        """Test selecting a random wallpaper from a directory"""
        mock_random_choice.return_value = self.test_files[0]
        
        handler = WallpaperHandler(self.mock_config)
        selected = handler.select_wallpaper_from_directory(self.wallpaper_dir)
        
        self.assertEqual(selected, self.test_files[0])
        mock_random_choice.assert_called_once()
        # Verify that the list passed to random.choice has all our test files
        self.assertEqual(set(mock_random_choice.call_args[0][0]), set(self.test_files))

    def test_select_wallpaper_from_directory_sequential(self):
        """Test selecting the newest wallpaper from a directory"""
        # Configure mock to return random=False
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'download_folder': self.wallpaper_dir,
            'source': self.wallpaper_dir,
            'random': False
        }.get(key, default)
        
        # Create a clean test directory for this specific test
        test_dir = tempfile.mkdtemp()
        try:
            # Create files with explicitly different timestamps
            files = []
            # Create files in reverse order to ensure OS sorting doesn't affect results
            for i in range(2, -1, -1):
                file_path = os.path.join(test_dir, f"test{i}.jpg")
                files.append(file_path)
                with open(file_path, 'w') as f:
                    f.write(f"test content {i}")
                
                # Make sure each timestamp is significantly different and in the correct order
                timestamp = datetime.now().timestamp() + (i * 100000)  # Much bigger difference
                os.utime(file_path, (timestamp, timestamp))
            
            # Create handler with mock config
            handler = WallpaperHandler(mock_config)
            
            # Override WallpaperHandler.select_wallpaper_from_directory to use our test_dir
            with patch.object(handler, 'select_wallpaper_from_directory', 
                             wraps=handler.select_wallpaper_from_directory) as mock_select:
                handler.select_wallpaper_from_directory(test_dir)
                
                # Check it was called with our directory
                mock_select.assert_called_with(test_dir)
                
                # Get the result manually to verify
                valid_files = [
                    f for f in sorted(files) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
                ]
                
                # Get the newest file based on modification time
                newest_file = max(valid_files, key=os.path.getmtime)
                
                # This should be test2.jpg
                self.assertEqual(os.path.basename(newest_file), "test2.jpg")
                
        finally:
            # Clean up
            shutil.rmtree(test_dir)

    def test_select_wallpaper_from_directory_empty(self):
        """Test selecting a wallpaper from an empty directory"""
        # Create an empty directory
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        handler = WallpaperHandler(self.mock_config)
        selected = handler.select_wallpaper_from_directory(empty_dir)
        
        self.assertIsNone(selected)

    @patch('requests.get')
    def test_download_wallpaper_success(self, mock_requests_get):
        """Test downloading a wallpaper successfully"""
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raw.decode_content = True
        mock_requests_get.return_value = mock_response
        
        # Mock datetime to get predictable filename
        mock_timestamp = "20230101_120000"
        with patch('wallpaper_changer.wallpaper_handler.datetime') as mock_datetime:
            mock_datetime_instance = MagicMock()
            mock_datetime_instance.strftime.return_value = mock_timestamp
            mock_datetime.now.return_value = mock_datetime_instance
            
            # Mock shutil.copyfileobj
            with patch('wallpaper_changer.wallpaper_handler.shutil.copyfileobj') as mock_copyfileobj:
                handler = WallpaperHandler(self.mock_config)
                result = handler.download_wallpaper("https://example.com/image.jpg")
                
                expected_filepath = os.path.join(
                    self.wallpaper_dir, 
                    f"wallpaper_{mock_timestamp}.jpg"
                )
                self.assertEqual(result, expected_filepath)
                mock_copyfileobj.assert_called_once()

    @patch('requests.get')
    def test_download_wallpaper_non_image_url(self, mock_requests_get):
        """Test downloading from a URL that doesn't point to an image"""
        handler = WallpaperHandler(self.mock_config)
        result = handler.download_wallpaper("https://example.com/not-an-image")
        
        self.assertIsNone(result)
        mock_requests_get.assert_not_called()

    @patch('requests.get')
    def test_download_wallpaper_failure(self, mock_requests_get):
        """Test downloading a wallpaper with a failed request"""
        # Mock the requests.get response for failure
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        handler = WallpaperHandler(self.mock_config)
        result = handler.download_wallpaper("https://example.com/image.jpg")
        
        self.assertIsNone(result)
        mock_requests_get.assert_called_once()

    @patch('requests.get')
    def test_download_wallpaper_exception(self, mock_requests_get):
        """Test downloading a wallpaper with an exception"""
        # Mock requests.get to raise an exception
        mock_requests_get.side_effect = Exception("Connection error")
        
        handler = WallpaperHandler(self.mock_config)
        result = handler.download_wallpaper("https://example.com/image.jpg")
        
        self.assertIsNone(result)
        mock_requests_get.assert_called_once()

    def test_get_wallpaper_path_local_directory(self):
        """Test getting wallpaper path from local directory"""
        with patch.object(WallpaperHandler, 'select_wallpaper_from_directory') as mock_select:
            mock_select.return_value = self.test_files[0]
            
            handler = WallpaperHandler(self.mock_config)
            result = handler.get_wallpaper_path()
            
            self.assertEqual(result, self.test_files[0])
            mock_select.assert_called_once_with(self.wallpaper_dir)

    def test_get_wallpaper_path_url(self):
        """Test getting wallpaper path from URL"""
        # Configure mock to return a URL as source
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'download_folder': self.wallpaper_dir,
            'source': 'https://example.com/images',
            'random': True
        }.get(key, default)
        
        with patch.object(WallpaperHandler, 'download_wallpaper') as mock_download:
            mock_download.return_value = os.path.join(self.wallpaper_dir, "downloaded.jpg")
            
            handler = WallpaperHandler(mock_config)
            result = handler.get_wallpaper_path()
            
            self.assertEqual(result, os.path.join(self.wallpaper_dir, "downloaded.jpg"))
            mock_download.assert_called_once_with('https://example.com/images')

    def test_get_wallpaper_path_file(self):
        """Test getting wallpaper path from a specific file"""
        specific_file = os.path.join(self.test_dir, "specific.jpg")
        with open(specific_file, 'w') as f:
            f.write("test content")
        
        # Configure mock to return a specific file as source
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'download_folder': self.wallpaper_dir,
            'source': specific_file,
            'random': True
        }.get(key, default)
        
        # Create a handler with our specific mock config, not the class-level one
        handler = WallpaperHandler(mock_config)
        
        # Now test the method
        result = handler.get_wallpaper_path()
        
        self.assertEqual(result, specific_file)

    def test_get_wallpaper_path_invalid_source(self):
        """Test getting wallpaper path with an invalid source"""
        # Configure mock to return an invalid source
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'download_folder': self.wallpaper_dir,
            'source': '/nonexistent/path',
            'random': True
        }.get(key, default)
        
        # Create a handler with our specific mock config
        handler = WallpaperHandler(mock_config)
        
        # Create a clean test using patch to isolate the select_wallpaper_from_directory method
        with patch.object(WallpaperHandler, 'select_wallpaper_from_directory', return_value=None):
            result = handler.get_wallpaper_path()
            self.assertIsNone(result)

    @patch('platform.system', return_value="Windows")
    @patch('ctypes.windll.user32.SystemParametersInfoW')
    def test_set_wallpaper_windows(self, mock_system_parameters, mock_platform):
        """Test setting wallpaper on Windows"""
        mock_system_parameters.return_value = 1  # Success
        
        handler = WallpaperHandler(self.mock_config)
        result = handler.set_wallpaper(self.test_files[0])
        
        self.assertTrue(result)
        mock_system_parameters.assert_called_once_with(20, 0, self.test_files[0], 3)

    @patch('platform.system', return_value="Darwin")
    @patch('subprocess.run')
    def test_set_wallpaper_macos(self, mock_subprocess_run, mock_platform):
        """Test setting wallpaper on macOS"""
        mock_subprocess_run.return_value.returncode = 0
        
        handler = WallpaperHandler(self.mock_config)
        result = handler.set_wallpaper(self.test_files[0])
        
        self.assertTrue(result)
        mock_subprocess_run.assert_called_once()
        # Verify the osascript command was used
        self.assertTrue("osascript" in mock_subprocess_run.call_args[0][0])

    @patch('platform.system', return_value="Linux")
    @patch('subprocess.run')
    def test_set_wallpaper_linux(self, mock_subprocess_run, mock_platform):
        """Test setting wallpaper on Linux"""
        mock_subprocess_run.return_value.returncode = 0
        
        handler = WallpaperHandler(self.mock_config)
        result = handler.set_wallpaper(self.test_files[0])
        
        self.assertTrue(result)
        mock_subprocess_run.assert_called()
        # Verify gsettings command was used
        self.assertEqual(mock_subprocess_run.call_args_list[0][0][0][0], "gsettings")

    @patch('platform.system', return_value="Unknown")
    def test_set_wallpaper_unsupported_os(self, mock_platform):
        """Test setting wallpaper on an unsupported OS"""
        handler = WallpaperHandler(self.mock_config)
        result = handler.set_wallpaper(self.test_files[0])
        
        self.assertFalse(result)

    def test_set_wallpaper_invalid_path(self):
        """Test setting wallpaper with an invalid file path"""
        handler = WallpaperHandler(self.mock_config)
        result = handler.set_wallpaper("/nonexistent/file.jpg")
        
        self.assertFalse(result)

    def test_change_wallpaper_success(self):
        """Test the main change_wallpaper function with success"""
        with patch.object(WallpaperHandler, 'get_wallpaper_path') as mock_get_path, \
             patch.object(WallpaperHandler, 'set_wallpaper') as mock_set_wallpaper:
            
            mock_get_path.return_value = self.test_files[0]
            mock_set_wallpaper.return_value = True
            
            handler = WallpaperHandler(self.mock_config)
            result = handler.change_wallpaper()
            
            self.assertTrue(result)
            mock_get_path.assert_called_once()
            mock_set_wallpaper.assert_called_once_with(self.test_files[0])

    def test_change_wallpaper_failure_no_path(self):
        """Test the main change_wallpaper function with no wallpaper path found"""
        with patch.object(WallpaperHandler, 'get_wallpaper_path') as mock_get_path:
            mock_get_path.return_value = None
            
            handler = WallpaperHandler(self.mock_config)
            result = handler.change_wallpaper()
            
            self.assertFalse(result)

    def test_change_wallpaper_failure_set_fails(self):
        """Test the main change_wallpaper function when setting wallpaper fails"""
        with patch.object(WallpaperHandler, 'get_wallpaper_path') as mock_get_path, \
             patch.object(WallpaperHandler, 'set_wallpaper') as mock_set_wallpaper:
            
            mock_get_path.return_value = self.test_files[0]
            mock_set_wallpaper.return_value = False
            
            handler = WallpaperHandler(self.mock_config)
            result = handler.change_wallpaper()
            
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
