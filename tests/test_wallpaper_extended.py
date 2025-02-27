import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from src.wallpaper import set_wallpaper, save_current_wallpaper, get_next_filename, get_current_wallpaper

class TestWallpaperExtended:
    def setup_method(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # Fix mock paths to use direct module references
    @patch('src.wallpaper.HAS_CTYPES', True)  # Mock that ctypes is available
    @patch('src.wallpaper.ctypes')  # Mock ctypes itself
    def test_set_wallpaper_windows(self, mock_ctypes):
        # Test setting wallpaper on Windows
        with patch('platform.system', return_value='Windows'):
            result = set_wallpaper('/path/to/image.jpg')
            assert result is True
            mock_ctypes.windll.user32.SystemParametersInfoW.assert_called_once()
    
    @patch('platform.system')
    @patch('subprocess.run')  # Use direct module path
    def test_set_wallpaper_linux(self, mock_run, mock_system):
        # Test setting wallpaper on Linux
        mock_system.return_value = 'Linux'
        
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'GNOME'}):
            set_wallpaper('/path/to/image.jpg')
            mock_run.assert_called_once()
    
    @patch('platform.system')
    @patch('subprocess.run')  # Use direct module path
    def test_set_wallpaper_macos(self, mock_run, mock_system):
        # Test setting wallpaper on macOS
        mock_system.return_value = 'Darwin'  # macOS
        
        set_wallpaper('/path/to/image.jpg')
        
        mock_run.assert_called_once()
    
    @patch('src.wallpaper.os.path.exists')
    @patch('src.wallpaper.os.listdir')
    def test_get_next_filename_empty_dir(self, mock_listdir, mock_exists):
        # Test get next filename for empty directory
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        result = get_next_filename(self.temp_dir)
        
        # Updated expectation to match the actual format used
        expected = os.path.join(self.temp_dir, 'wallpaper-001.jpg')
        assert result == expected
    
    @patch('src.wallpaper.os.path.exists')
    @patch('src.wallpaper.os.listdir')
    def test_get_next_filename_with_files(self, mock_listdir, mock_exists):
        # Test get next filename with existing files
        mock_exists.return_value = True
        # Update the mock to return filenames in the correct format
        mock_listdir.return_value = ['wallpaper-001.jpg', 'wallpaper-002.jpg']
        
        result = get_next_filename(self.temp_dir)
        
        # Updated expectation to match the actual format used
        expected = os.path.join(self.temp_dir, 'wallpaper-003.jpg')
        assert result == expected
    
    def test_save_current_wallpaper(self):
        # Create a mock file to save
        test_file = os.path.join(self.temp_dir, 'test_wallpaper.jpg')
        with open(test_file, 'w') as f:
            f.write('test content')
            
        # Test saving wallpaper directly with a path
        with patch('src.wallpaper.config.SAVED_DIR', self.temp_dir):
            result = save_current_wallpaper(test_file)
            
        # Should have created a saved file
        assert result is not None
        assert os.path.exists(result)
