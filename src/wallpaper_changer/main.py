#!/usr/bin/env python3
"""
Wallpaper Changer - Main Module
Automatically changes desktop wallpaper based on configured settings.
"""
import argparse
import logging
import os
import sys
import time
from datetime import datetime

from .config import Config
from .wallpaper_handler import WallpaperHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wallpaper_changer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Wallpaper Changer Application')
    parser.add_argument('--config', '-c', type=str, default='settings.json',
                        help='Path to the configuration file')
    parser.add_argument('--interval', '-i', type=int,
                        help='Interval in minutes between wallpaper changes')
    parser.add_argument('--source', '-s', type=str,
                        help='Source directory or URL for wallpapers')
    parser.add_argument('--once', action='store_true',
                        help='Change the wallpaper once and exit')
    return parser.parse_args()

def main():
    """Main function of the application"""
    try:
        args = parse_arguments()
        
        # Load configuration with command line overrides
        config = Config(args.config)
        if args.interval:
            config.set('interval', args.interval)
        if args.source:
            config.set('source', args.source)
            
        # Initialize the wallpaper handler
        handler = WallpaperHandler(config)
        
        logger.info("Wallpaper Changer started")
        
        if args.once:
            # Change wallpaper once and exit
            handler.change_wallpaper()
            logger.info("Wallpaper changed successfully. Exiting.")
            sys.exit(0)  # Explicitly call sys.exit instead of return
            
        # Start the main loop
        interval_minutes = config.get('interval', 30)  # Default 30 minutes
        interval_seconds = interval_minutes * 60
        
        while True:
            try:
                handler.change_wallpaper()
                logger.info(f"Next wallpaper change in {interval_minutes} minutes.")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("Received exit signal. Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        sys.exit(0)  # Explicitly call sys.exit instead of return
                
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)  # Explicitly call sys.exit instead of return

if __name__ == "__main__":
    sys.exit(main())
