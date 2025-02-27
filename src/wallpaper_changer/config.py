"""
Configuration module for Wallpaper Changer
Handles reading, writing and validating configuration.
"""
import os
import json
import logging

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
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    loaded_config = json.load(file)
                    self.config.update(loaded_config)
                    logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info(f"No configuration file found at {self.config_file}. Using defaults.")
                self.save()  # Create default config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=4)
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
