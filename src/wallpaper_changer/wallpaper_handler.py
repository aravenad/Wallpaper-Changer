"""
Wallpaper Handler Module
Handles downloading, selecting, and setting desktop wallpapers.
"""
import os
import random
import logging
import platform
import ctypes
import shutil
import subprocess
from datetime import datetime
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)

class WallpaperHandler:
    """Handler for wallpaper operations"""
    
    def __init__(self, config):
        self.config = config
        self.system = platform.system()
        
        # Ensure wallpaper directory exists
        self.wallpaper_dir = config.get('download_folder', 'wallpapers')
        if not os.path.exists(self.wallpaper_dir):
            os.makedirs(self.wallpaper_dir)
            logger.info(f"Created wallpaper directory: {self.wallpaper_dir}")

    def get_wallpaper_path(self):
        """Get a path to the next wallpaper"""
        source = self.config.get('source', 'wallpapers')
        
        # If source is a URL, download a new wallpaper
        if source.startswith(('http://', 'https://')):
            return self.download_wallpaper(source)
        
        # If source is a local directory, select a file
        if os.path.isdir(source):
            return self.select_wallpaper_from_directory(source)
        
        # If source is a specific file, return it
        if os.path.isfile(source):
            return source
            
        logger.error(f"Invalid source configuration: {source}")
        return None
    
    def select_wallpaper_from_directory(self, directory):
        """Select a wallpaper from the given directory"""
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        wallpapers = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and
            f.lower().endswith(valid_extensions)
        ]
        
        if not wallpapers:
            logger.error(f"No valid wallpapers found in directory: {directory}")
            return None
            
        if self.config.get('random', True):
            return random.choice(wallpapers)
        else:
            # Return the most recently added file
            return max(wallpapers, key=os.path.getctime)
    
    def download_wallpaper(self, url):
        """Download a wallpaper from the given URL"""
        try:
            # If URL is a specific image
            if urlparse(url).path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    # Save with timestamp to avoid duplicates
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"wallpaper_{timestamp}{os.path.splitext(urlparse(url).path)[1]}"
                    filepath = os.path.join(self.wallpaper_dir, filename)
                    
                    with open(filepath, 'wb') as file:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, file)
                    
                    logger.info(f"Downloaded wallpaper to {filepath}")
                    return filepath
            
            # If URL is an API or service (should implement specific APIs here)
            logger.error(f"URL does not point to a direct image: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading wallpaper from {url}: {e}")
            return None
            
    def set_wallpaper(self, wallpaper_path):
        """Set the desktop wallpaper based on the operating system"""
        if not wallpaper_path or not os.path.isfile(wallpaper_path):
            logger.error(f"Invalid wallpaper path: {wallpaper_path}")
            return False
            
        try:
            if self.system == "Windows":
                ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
            
            elif self.system == "Darwin":  # macOS
                script = f"""
                osascript -e 'tell application "Finder" to set desktop picture to POSIX file "{wallpaper_path}"'
                """
                subprocess.run(script, shell=True, check=True)
                
            elif self.system == "Linux":
                # Try common Linux desktop environments
                # For GNOME
                subprocess.run(
                    ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{wallpaper_path}"],
                    check=False
                )
                # For KDE Plasma
                if shutil.which("plasma-apply-wallpaperimage"):
                    subprocess.run(["plasma-apply-wallpaperimage", wallpaper_path], check=False)
                    
            else:
                logger.error(f"Unsupported operating system: {self.system}")
                return False
                
            logger.info(f"Wallpaper set to {wallpaper_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting wallpaper: {e}")
            return False
    
    def change_wallpaper(self):
        """Main function to change the wallpaper"""
        wallpaper_path = self.get_wallpaper_path()
        if wallpaper_path:
            return self.set_wallpaper(wallpaper_path)
        return False
