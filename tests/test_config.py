"""
Tests for the config module
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch

from src.wallpaper_changer.config import Config

class TestConfig(unittest.TestCase):
    """Test cases for the Config class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_name = temp.name
            
        try:
            # Use a temporary file path that doesn't exist
            config = Config(temp_name)
            
            # Check default values
            self.assertEqual(config.get('interval'), 30)
            self.assertEqual(config.get('source'), 'wallpapers')
            self.assertTrue(config.get('random'))
            
            # Check the file was created
            self.assertTrue(os.path.exists(temp_name))
            
            # Check file contents
            with open(temp_name, 'r') as f:
                saved_config = json.load(f)
                self.assertEqual(saved_config['interval'], 30)
        finally:
            # Clean up
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    
    def test_custom_config(self):
        """Test loading custom configuration"""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            # Create a custom config
            custom_config = {
                'interval': 60,
                'source': 'custom_dir',
                'random': False
            }
            json.dump(custom_config, temp)
            temp_name = temp.name
            
        try:
            # Load the custom config
            config = Config(temp_name)
            
            # Check custom values are loaded
            self.assertEqual(config.get('interval'), 60)
            self.assertEqual(config.get('source'), 'custom_dir')
            self.assertFalse(config.get('random'))
            
            # Check defaults for missing values
            self.assertEqual(config.get('fit_mode'), 'fill')
        finally:
            # Clean up
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    
    def test_set_value(self):
        """Test setting configuration values"""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_name = temp.name
            
        try:
            config = Config(temp_name)
            
            # Set a value
            config.set('interval', 120)
            
            # Check it was updated in memory
            self.assertEqual(config.get('interval'), 120)
            
            # Check it was saved to file
            with open(temp_name, 'r') as f:
                saved_config = json.load(f)
                self.assertEqual(saved_config['interval'], 120)
                
            # Create a new config instance to check loading
            config2 = Config(temp_name)
            self.assertEqual(config2.get('interval'), 120)
        finally:
            # Clean up
            if os.path.exists(temp_name):
                os.unlink(temp_name)

if __name__ == '__main__':
    unittest.main()
