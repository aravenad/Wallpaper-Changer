"""
Directory Initialization Module

This module creates any necessary directories for the application
"""

import os
import json
from .logger import logger
from . import config

def ensure_directories():
    """
    Ensure all required directories exist
    """
    directories = [
        config.IMG_DIR,      # Directory for current wallpaper
        config.SAVED_DIR     # Directory for saved wallpapers (now a subdirectory of IMG_DIR)
    ]
    
    created = False
    for directory in directories:
        if not os.path.exists(directory):
            try:
                # Create directory with all intermediate directories
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                created = True
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
                
    return created

def create_app_dirs(base_dir=None):
    """
    Create application directories if they don't exist.
    
    Args:
        base_dir (str, optional): Base directory for app folders. Defaults to ~/.wallpaper.
    
    Returns:
        dict: Dictionary with keys 'config_dir' and 'images_dir' containing paths
    """
    # Define base directory in user's home folder if not provided
    if base_dir is None:
        base_dir = os.path.expanduser("~/.wallpaper")
    
    # Define specific directories
    config_dir = os.path.join(base_dir, "config")
    images_dir = os.path.join(base_dir, "images")
    saved_dir = os.path.join(base_dir, "saved")
    
    # Create directories if they don't exist
    for directory in [config_dir, images_dir, saved_dir]:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
    
    # Return directory paths in a dictionary
    return {
        "config_dir": config_dir,
        "images_dir": images_dir,
        "saved_dir": saved_dir
    }

def check_config_file_exists(config_file_path):
    """
    Check if config file exists.
    
    Args:
        config_file_path (str): Path to the config file
        
    Returns:
        bool: True if the config file exists, False otherwise
    """
    return os.path.isfile(config_file_path)

def create_default_config_file(config_file_path):
    """
    Create a config file with default content.
    
    Args:
        config_file_path (str): Path where the config file should be created
        
    Returns:
        bool: True if the file was created successfully, False otherwise
    """
    try:
        # Create default config content
        default_config = {
            "api_key": "",
            "categories": ["nature", "architecture", "travel"],
            "auto_interval": "auto",
            "save_favorites": True,
            "notifications": True
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        
        # Write default config to file
        with open(config_file_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        logger.info(f"Default config file created at: {config_file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create config file: {str(e)}")
        return False

def check_config_file(config_file_path):
    """
    Check if config file exists and create it with default content if it doesn't.
    
    Args:
        config_file_path (str): Path to the config file
    
    Returns:
        bool: True if the config file exists or was created successfully, False otherwise
    """
    if not check_config_file_exists(config_file_path):
        logger.info(f"Config file not found. Creating default: {config_file_path}")
        return create_default_config_file(config_file_path)
    return True

if __name__ == "__main__":
    # When run as a script, create all directories and ensure config file exists
    dirs = create_app_dirs()
    check_config_file(os.path.join(dirs["config_dir"], "config.json"))
