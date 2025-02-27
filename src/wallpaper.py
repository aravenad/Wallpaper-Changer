# src/wallpaper.py

import os
import shutil
import glob
import time
import logging
import platform
import subprocess
import re
from .logger import logger
from . import config

# Try to import the custom logger, fall back to standard logging if it fails
try:
    from .logger import logger
    if logger is None:
        # Create a default logger if import succeeded but logger is None
        logger = logging.getLogger('wallpaper_changer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
except ImportError:
    # Create a default logger if import failed
    logger = logging.getLogger('wallpaper_changer')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

# Try to import ctypes for Windows wallpaper setting
try:
    import ctypes
    HAS_CTYPES = True
except ImportError:
    HAS_CTYPES = False
    logger.warning("Could not import ctypes. Wallpaper setting will not work.")

def set_wallpaper(image_path):
    """
    Set the desktop wallpaper across platforms.
    """
    abs_path = os.path.abspath(image_path)
    system = platform.system()
    try:
        if system == 'Windows':
            # Try using ctypes first
            if HAS_CTYPES:
                ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0x01 | 0x02)
                return True
            else:
                # Fallback to PowerShell
                cmd = ['powershell', '-Command', 
                       "$code = @'\n" +
                       "[DllImport('user32.dll')] public static extern bool " +
                       "SystemParametersInfo(uint uiAction, uint uiParam, " +
                       "string pvParam, uint fWinIni);\n" +
                       "@'\n" +
                       "$SPI_SETDESKWALLPAPER = 0x14\n" +
                       "$SPIF_UPDATEINIFILE = 0x01\n" +
                       "$SPIF_SENDWININICHANGE = 0x02\n" +
                       "$fWinIni = $SPIF_UPDATEINIFILE -bor $SPIF_SENDWININICHANGE\n" +
                       "$CSharp = Add-Type -MemberDefinition $code -Name Win32Utils " +
                       "-Namespace SystemParametersInfo -PassThru\n" +
                       "$CSharp::SystemParametersInfo($SPI_SETDESKWALLPAPER, 0, " +
                       f"'{abs_path}', $fWinIni)"]
                subprocess.run(cmd, check=True)
                return True
        elif system == 'Linux':
            # Try to detect the desktop environment
            desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if 'gnome' in desktop or 'unity' in desktop:
                subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 
                               'picture-uri', f'file://{abs_path}'], check=True)
            elif 'kde' in desktop:
                # KDE Plasma
                subprocess.run(['plasma-apply-wallpaperimage', abs_path], check=True)
            elif 'xfce' in desktop:
                # XFCE
                subprocess.run(['xfconf-query', '-c', 'xfce4-desktop', '-p', 
                               '/backdrop/screen0/monitor0/workspace0/last-image', 
                               '-s', abs_path], check=True)
            else:
                # Generic method, try feh
                subprocess.run(['feh', '--bg-scale', abs_path], check=True)
            return True
        elif system == 'Darwin':  # macOS
            script = f'''
            tell application "System Events"
                tell every desktop
                    set picture to "{abs_path}"
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        else:
            logger.error(f"Unsupported platform: {system}")
            return False
    except Exception as e:
        logger.error(f"Failed to set wallpaper: {str(e)}")
        return False

def save_current_wallpaper(file_path=None, source_url=None):
    """
    Save the current wallpaper to the saved directory with sequential naming.
    
    Args:
        file_path (str, optional): Path to the file to save. If None, tries to detect current wallpaper.
        source_url (str, optional): Source URL of the wallpaper, for metadata.
        
    Returns:
        str: Path to the saved file if successful, None otherwise.
    """
    # Make sure the saved directory exists
    if not os.path.exists(config.SAVED_DIR):
        os.makedirs(config.SAVED_DIR, exist_ok=True)
    
    # Use provided file_path or try to find the current wallpaper
    source_file = file_path
    if source_file is None:
        source_file = get_current_wallpaper()
        
    if not source_file or not os.path.exists(source_file):
        logger.error("No current wallpaper found to save.")
        return None
    
    # Generate the next available filename for saved wallpapers
    next_filename = get_next_filename(config.SAVED_DIR)
    
    try:
        # Copy the file
        shutil.copy2(source_file, next_filename)
        logger.info(f"[✓] Wallpaper saved as '{os.path.basename(next_filename)}'")
        
        # Optionally save metadata if source_url is provided
        if source_url:
            name_parts = os.path.splitext(next_filename)
            metadata_path = f"{name_parts[0]}.txt"
            with open(metadata_path, 'w') as f:
                f.write(f"Source URL: {source_url}\n")
                f.write(f"Saved on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        return next_filename
    except Exception as e:
        logger.error(f"Failed to save wallpaper: {str(e)}")
        return None

def get_next_filename(save_dir):
    """
    Generate the next sequential filename for saved wallpapers.
    
    Args:
        save_dir: Directory where wallpapers are saved
        
    Returns:
        str: Path to the next filename to use (e.g., "wallpaper-001.jpg")
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    # List all files in the directory
    existing_files = os.listdir(save_dir)
    
    # Find the highest number used in existing wallpaper files
    highest_num = 0
    pattern = re.compile(r'wallpaper-(\d+)\.jpg')
    
    for filename in existing_files:
        match = pattern.match(filename)
        if match:
            num = int(match.group(1))
            highest_num = max(highest_num, num)
    
    # Create next filename with leading zeros (3 digits)
    next_num = highest_num + 1
    next_filename = f"wallpaper-{next_num:03d}.jpg"
    
    return os.path.join(save_dir, next_filename)

def get_current_wallpaper():
    """
    Get the path to the current wallpaper.
    
    Returns:
        str: Path to the current wallpaper file, or None if not found
    """
    from . import config
    
    # Check the default wallpaper location
    current_wallpaper = os.path.join(config.IMG_DIR, "wallpaper.jpg")
    if os.path.exists(current_wallpaper):
        return current_wallpaper
    
    # If not found, try to get it from the system (platform specific)
    import platform
    
    system = platform.system()
    
    if system == 'Windows':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Control Panel\\Desktop") as key:
                wallpaper_path = winreg.QueryValueEx(key, "WallPaper")[0]
                if os.path.exists(wallpaper_path):
                    return wallpaper_path
        except Exception as e:
            logger.error(f"Error getting wallpaper from registry: {str(e)}")
    
    # For other platforms or if we couldn't get it
    logger.warning("Could not determine current wallpaper path")
    return None
