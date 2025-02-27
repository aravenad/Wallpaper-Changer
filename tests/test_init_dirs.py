import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from src.init_dirs import create_app_dirs, check_config_file

class TestInitDirs:
    def setup_method(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.init_dirs.os.path.expanduser')
    @patch('src.init_dirs.os.path.exists')
    @patch('src.init_dirs.os.makedirs')
    def test_create_app_dirs(self, mock_makedirs, mock_exists, mock_expanduser):
        # Test app directories creation
        mock_expanduser.return_value = os.path.join(self.temp_dir, '.wallpaper')
        mock_exists.return_value = False
        
        dirs = create_app_dirs()
        
        # Check if directories were created
        assert mock_makedirs.call_count >= 2
        assert 'config_dir' in dirs
        assert 'images_dir' in dirs
        assert isinstance(dirs['config_dir'], str)
        assert isinstance(dirs['images_dir'], str)
    
    @patch('src.init_dirs.os.path.isfile')
    def test_check_config_file_exists(self, mock_isfile):
        # Test when config file already exists
        mock_isfile.return_value = True
        
        m = mock_open()
        with patch('builtins.open', m):
            check_config_file('/fake/config/path')
            
            # File should not be opened for writing since it exists
            m.assert_not_called()
    
    @patch('src.init_dirs.os.path.exists')
    def test_check_config_file_not_exists(self, mock_exists):
        # Test when config file needs to be created
        mock_exists.return_value = False
        
        m = mock_open()
        with patch('builtins.open', m):
            check_config_file('/fake/config/path')
            
            # File should be opened for writing
            m.assert_called_once_with('/fake/config/path', 'w')
            # Check that some content is written to the file
            handle = m()
            handle.write.assert_called()
