# tests/test_wallpaper.py

import os
import sys
import shutil
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import pytest

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import wallpaper, config

class TestWallpaper(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.original_img_dir = config.IMG_DIR
        self.original_saved_dir = config.SAVED_DIR
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_img_dir = os.path.join(self.temp_dir, "img")
        self.test_saved_dir = os.path.join(self.temp_dir, "saved")
        
        os.makedirs(self.test_img_dir, exist_ok=True)
        
        # Create a dummy wallpaper file
        self.test_wallpaper_path = os.path.join(self.test_img_dir, "wallpaper.jpg")
        with open(self.test_wallpaper_path, 'wb') as f:
            f.write(b'test image data')
        
        # Override config directories
        config.IMG_DIR = self.test_img_dir
        config.SAVED_DIR = self.test_saved_dir
    
    def tearDown(self):
        # Restore original config
        config.IMG_DIR = self.original_img_dir
        config.SAVED_DIR = self.original_saved_dir
        
        # Remove temp directories
        shutil.rmtree(self.temp_dir)
    
    @patch('ctypes.windll.user32.SystemParametersInfoW')
    def test_set_wallpaper(self, mock_set_wallpaper):
        wallpaper.set_wallpaper(self.test_wallpaper_path)
        mock_set_wallpaper.assert_called_once()
    
    def test_save_current_wallpaper_first_file(self):
        # Test saving the first wallpaper
        saved_path = wallpaper.save_current_wallpaper()
        
        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path) if saved_path else False)
        # Only check basename if saved_path is not None
        if saved_path:
            self.assertEqual(os.path.basename(saved_path), "wallpaper-001.jpg")
            
            # Check content was copied correctly
            with open(saved_path, 'rb') as f:
                content = f.read()
            self.assertEqual(content, b'test image data')
    
    def test_save_current_wallpaper_sequential_naming(self):
        # Create existing files to test sequential naming
        os.makedirs(self.test_saved_dir, exist_ok=True)
        for i in range(1, 4):
            with open(os.path.join(self.test_saved_dir, f"wallpaper-{i:03d}.jpg"), 'wb') as f:
                f.write(b'existing file')
        
        # Save new wallpaper
        saved_path = wallpaper.save_current_wallpaper()
        
        self.assertIsNotNone(saved_path)
        if saved_path:  # Make sure saved_path is not None before calling basename
            self.assertEqual(os.path.basename(saved_path), "wallpaper-004.jpg")
    
    def test_save_current_wallpaper_noncontiguous_naming(self):
        # Create existing files with gaps in numbering
        os.makedirs(self.test_saved_dir, exist_ok=True)
        with open(os.path.join(self.test_saved_dir, "wallpaper-001.jpg"), 'wb') as f:
            f.write(b'existing file')
        with open(os.path.join(self.test_saved_dir, "wallpaper-005.jpg"), 'wb') as f:
            f.write(b'existing file')
        with open(os.path.join(self.test_saved_dir, "wallpaper-010.jpg"), 'wb') as f:
            f.write(b'existing file')
        
        # Save new wallpaper - should be one more than the highest existing number
        saved_path = wallpaper.save_current_wallpaper()
        
        self.assertIsNotNone(saved_path)
        if saved_path:  # Make sure saved_path is not None before using basename
            self.assertEqual(os.path.basename(saved_path), "wallpaper-011.jpg")
    
    def test_save_current_wallpaper_no_source_file(self):
        # Patch the get_current_wallpaper function to return None
        with patch('src.wallpaper.get_current_wallpaper', return_value=None):
            # Try to save (should fail gracefully)
            saved_path = wallpaper.save_current_wallpaper()
        
            self.assertIsNone(saved_path)

if __name__ == '__main__':
    unittest.main()
