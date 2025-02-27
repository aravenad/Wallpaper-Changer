"""
Configuration module for Wallpaper Changer
Handles reading, writing and validating configuration.
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

class Config:
    """Configuration handler for the wallpaper changer app"""
    
    DEFAULT_CONFIG = {
        "interval": 30,  # minutes
        "source": "wallpapers",  # local directory
        "random": True,
        "save_downloaded": True,
        "download_folder": "wallpapers",
        "fit_mode": "fill"  # options: fill, fit, stretch, center, tile
    }
    
    def __init__(self, config_file='settings.json'):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
        
        # If the file doesn't exist or couldn't be loaded properly, save the default config
        if not os.path.exists(self.config_file):
            self.save()
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file) and os.path.getsize(self.config_file) > 0:
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    loaded_config = json.load(file)
                    self.config.update(loaded_config)
                    logger.info(f"Configuration loaded from {self.config_file}")
            else:
                if os.path.exists(self.config_file):
                    logger.info(f"Configuration file {self.config_file} exists but is empty. Using defaults.")
                else:
                    logger.info(f"No configuration file found at {self.config_file}. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure the directory exists
            directory = os.path.dirname(os.path.abspath(self.config_file))
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=4)
                file.flush()
                os.fsync(file.fileno())  # Force write to disk
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        self.save()
