#!/usr/bin/env python3
"""
Integrated Main Module for Wallpaper Changer
Combines features from both src/main.py and src/wallpaper_changer/main.py
"""
# First, ensure we have dotenv loaded before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables at the very beginning
except ImportError:
    # If dotenv is not available, we'll handle it later
    pass

import argparse
import json
import logging
import os
import random
import shutil
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests

# Import our special version of unsplash_api
import src.unsplash_api as unsplash_api

# Import our modules after environment is set up
from src.categories import CATEGORIES
from src.wallpaper import save_current_wallpaper, set_wallpaper

# Fix the import to use the correct Config class
try:
    # First try to import from wallpaper_changer package
    from wallpaper_changer.config import Config
except ImportError:
    # If that fails, try importing from src.wallpaper_changer 
    try:
        from src.wallpaper_changer.config import Config
    except ImportError:
        # Finally try importing the config module directly
        from src.wallpaper_changer.config import Config

# Add color support for logs
import colorama

colorama.init()

# Configure colored logging
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{colorama.Style.RESET_ALL}"
        return super().format(record)

# Configure logging with colors
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter("%(asctime)s -> %(levelname)s: %(message)s", 
                                    datefmt="%H:%M:%S"))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = [handler]  # Replace any existing handlers

# Global variables
current_wallpaper_url = None  # Track the current wallpaper URL
last_manual_update = datetime.now() - timedelta(minutes=5)
requests_log_file = os.path.join(os.path.expanduser("~"), ".wallpaper_requests.json")
saved_wallpapers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img", "saved")

# Create saved wallpapers directory if it doesn't exist
if not os.path.exists(saved_wallpapers_dir):
    try:
        os.makedirs(saved_wallpapers_dir, exist_ok=True)
        print(f"{colorama.Fore.GREEN}Created directory for saved wallpapers: {saved_wallpapers_dir}{colorama.Style.RESET_ALL}")
    except Exception as e:
        print(f"{colorama.Fore.RED}Failed to create saved wallpapers directory: {e}{colorama.Style.RESET_ALL}")

# Default category if none specified
DEFAULT_CATEGORY = "summer"

# Try to import keyboard module with automatic installation
try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    try:
        logger.info("Keyboard module not found. Attempting to install...")
        from subprocess import run
        run([sys.executable, "-m", "pip", "install", "keyboard"], check=True)
        import keyboard
        HAS_KEYBOARD = True
        logger.info("Keyboard module installed successfully.")
    except Exception:
        logger.warning("⚠️ Keyboard module not available. Using mock implementation.")
        HAS_KEYBOARD = False
        
        # Mock keyboard module
        class MockKeyboard:
            """Mock implementation of keyboard module"""
            
            @staticmethod
            def is_pressed(key):
                """Always return False for is_pressed"""
                return False
                
            @staticmethod
            def add_hotkey(key, callback, args=None):
                """Do nothing for add_hotkey"""
                pass
            
            @staticmethod
            def on_press(callback):
                """Do nothing for on_press"""
                pass
        
        keyboard = MockKeyboard()

# Try to import win32gui for desktop focus detection
try:
    import win32gui
    HAS_WIN32GUI = True
except ImportError:
    try:
        logger.info("win32gui module not found. Attempting to install pywin32...")
        from subprocess import run
        run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
        import win32gui
        HAS_WIN32GUI = True
        logger.info("pywin32 installed successfully.")
    except Exception:
        logger.warning("⚠️ win32gui module not available. Key shortcuts will work in any window.")
        HAS_WIN32GUI = False

# Constants
MIN_REQUESTS_LEFT = 5  # Minimum number of requests to leave available
REQUEST_COOLDOWN = 5  # Seconds to wait between manual requests


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Wallpaper Changer Application')
    parser.add_argument('--config', '-c', type=str, default='settings.json',
                        help='Path to the configuration file')
    parser.add_argument('--interval', '-i', type=int,
                        help='Interval in minutes between wallpaper changes')
    parser.add_argument('--category', '-cat', type=str,
                        help=f'Category for wallpapers (default: {DEFAULT_CATEGORY})')
    parser.add_argument('--source', '-s', type=str,
                        help='Source directory or URL for wallpapers')
    parser.add_argument('--auto', '-a', action='store_true',
                        help='Auto-adjust interval based on API limits')
    parser.add_argument('--once', action='store_true',
                        help='Change the wallpaper once and exit')
    parser.add_argument('--list-categories', '-l', action='store_true',
                        help='List available categories and exit')
    parser.add_argument('--search', type=str,
                        help='Search term for wallpapers')
    parser.add_argument('--save', action='store_true',
                        help='Save downloaded wallpaper')
    return parser.parse_args()


def is_desktop_foreground() -> bool:
    """Check if desktop is the foreground window"""
    if not HAS_WIN32GUI:
        return True
        
    try:
        foreground_window = win32gui.GetForegroundWindow()
        window_text = win32gui.GetWindowText(foreground_window)
        # Desktop window typically has empty title or "Program Manager"
        return window_text in ["", "Program Manager"]
    except Exception:
        logger.warning("Failed to check foreground window. Assuming desktop is not active.")
        return False


def read_requests_log() -> Tuple[int, datetime]:
    """Read the requests log file to get the number of requests made and timestamp"""
    try:
        if not os.path.exists(requests_log_file):
            return 0, datetime.now() - timedelta(hours=1)
            
        with open(requests_log_file, 'r') as f:
            data = json.load(f)
            timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01T00:00:00'))
            count = data.get('count', 0)
            return count, timestamp
    except Exception as e:
        logger.error(f"Error reading requests log: {e}")
        return 0, datetime.now() - timedelta(hours=1)


def write_requests_log(count: int, timestamp: Optional[datetime] = None) -> None:
    """Write the requests log to file"""
    if timestamp is None:
        timestamp = datetime.now()
        
    try:
        data = {
            'count': count,
            'timestamp': timestamp.isoformat()
        }
        
        with open(requests_log_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error writing requests log: {e}")


def update_rate_limits(headers: Dict) -> Tuple[int, int, int]:
    """Update rate limits from response headers"""
    try:
        requests_limit = int(headers.get('X-Ratelimit-Limit', '50'))
        requests_remaining = int(headers.get('X-Ratelimit-Remaining', '50'))
        reset_timestamp = int(headers.get('X-Ratelimit-Reset', '0'))
        
        return requests_limit, requests_remaining, reset_timestamp
    except (ValueError, TypeError):
        logger.warning("Invalid rate limit headers. Using defaults.")
        return 50, 45, int(time.time() + 3600)


def compute_auto_interval(max_interval: int = 60) -> int:
    """Compute auto interval based on API rate limits"""
    requests_count, timestamp = read_requests_log()
    
    # If it's been more than an hour since last request, reset counter
    if datetime.now() - timestamp > timedelta(hours=1):
        requests_count = 0
        write_requests_log(requests_count)
    
    total_requests = 50  # Default Unsplash API limit
    remaining_requests = total_requests - requests_count
    
    # Ensure we leave some minimum number of requests available
    usable_requests = max(0, remaining_requests - MIN_REQUESTS_LEFT)
    
    if usable_requests <= 0:
        # Not enough requests left, use maximum interval
        return max_interval
    
    # Calculate time remaining in the hour
    seconds_remaining = 3600 - (datetime.now() - timestamp).total_seconds() % 3600
    minutes_remaining = max(1, int(seconds_remaining / 60))
    
    # Calculate interval: divide remaining time by usable requests
    interval = max(1, int(minutes_remaining / usable_requests))
    
    # Cap at max_interval
    return min(interval, max_interval)


def update_wallpaper(category: Optional[str] = None, save: bool = False, search: Optional[str] = None) -> bool:
    """Update the wallpaper with optional category and search term"""
    global current_wallpaper_url  # Use global to update the variable
    
    try:
        # Fix the fetch_wallpaper call to handle both category and search parameters
        if search:
            # If search is provided, use it instead of category
            image_url, headers = unsplash_api.fetch_wallpaper(search_term=search)
        else:
            # Otherwise use category (which can be None for random)
            image_url, headers = unsplash_api.fetch_wallpaper(category=category)
        
        if not image_url:
            logger.error("Failed to fetch wallpaper. No image URL received.")
            return False
        
        logger.debug(f"Setting wallpaper from URL: {image_url}")
        
        # Set the wallpaper
        status = set_wallpaper(image_url)
        
        # Update rate limits
        requests_limit, requests_remaining, _ = update_rate_limits(headers)
        
        # Update request log
        requests_count, timestamp = read_requests_log()
        if datetime.now() - timestamp > timedelta(hours=1):
            requests_count = 0
        requests_count += 1
        write_requests_log(requests_count)
        
        # Store the current wallpaper URL
        if status:
            current_wallpaper_url = image_url  # Update the URL 
            logger.debug(f"Stored current wallpaper URL: {current_wallpaper_url}")
        
        # Save the wallpaper if requested
        if save and current_wallpaper_url:
            saved_path = save_wallpaper(current_wallpaper_url)
            if saved_path:
                logger.info(f"✅ Wallpaper saved to {saved_path}")
            else:
                logger.error("❌ Failed to save wallpaper")
        
        type_str = search if search else (category if category else 'random')
        logger.info(f"✅ Wallpaper updated ('{type_str}'). Requests left: {requests_remaining}")
        return status
    except Exception as e:
        logger.error(f"❌ Error updating wallpaper: {e}")
        return False

def save_wallpaper(url: str) -> Optional[str]:
    """Save wallpaper to the saved directory with sequential naming"""
    if not url:
        logger.error("No URL provided to save")
        return None
    
    # Create saved directory if it doesn't exist
    if not os.path.exists(saved_wallpapers_dir):
        try:
            os.makedirs(saved_wallpapers_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating saved directory: {e}")
            return None
    
    try:
        # Get next sequential number
        existing_files = [f for f in os.listdir(saved_wallpapers_dir) 
                         if f.startswith('wallpaper-') and f.endswith(('.jpg', '.jpeg', '.png'))]
        
        next_number = 1
        if existing_files:
            # Extract numbers from existing files
            numbers = []
            for filename in existing_files:
                try:
                    num_part = filename.split('-')[1].split('.')[0]
                    if num_part.isdigit():
                        numbers.append(int(num_part))
                except (IndexError, ValueError):
                    continue
            
            if numbers:
                next_number = max(numbers) + 1
        
        # Format the filename with leading zeros
        filename = f"wallpaper-{next_number:03d}.jpg"
        filepath = os.path.join(saved_wallpapers_dir, filename)
        
        # Download and save the image
        logger.info(f"Saving wallpaper to {filepath}...")
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to download image: HTTP {response.status_code}")
            return None
            
        with open(filepath, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
            
        logger.info(f"Wallpaper saved as {filename}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving wallpaper: {e}")
        return None

def process_key_press(e):
    """Process a key press event"""
    global last_manual_update, current_wallpaper_url
    
    # Extract key name properly
    key_name = None
    if isinstance(e, dict) and 'name' in e:
        key_name = e['name']
    elif hasattr(e, 'name'):
        key_name = e.name
    else:
        logger.debug(f"Unknown event type received: {type(e)}")
        return
    
    logger.debug(f"Key press detected: {key_name}")
    
    # Only process if desktop is in foreground
    if not is_desktop_foreground():
        logger.debug(f"Key press '{key_name}' ignored - desktop not in foreground")
        return
    
    # Get current time for cooldown check
    now = datetime.now()
    cooldown_elapsed = (now - last_manual_update).total_seconds() >= REQUEST_COOLDOWN
    
    if key_name == 'n' and cooldown_elapsed:
        # Update requests log to check if we have enough requests left
        requests_count, _ = read_requests_log()
        if requests_count >= 45:  # Leave some buffer
            logger.warning("⚠️ Rate limit approaching. Manual update denied.")
            return
        
        logger.info("🔄 Manual wallpaper change requested")
        if update_wallpaper(category=None, save=False, search=None):  # Use random category
            last_manual_update = now
    
    elif key_name == 's':
        if current_wallpaper_url:
            logger.debug(f"Saving current wallpaper: {current_wallpaper_url}")
            save_path = save_wallpaper(current_wallpaper_url)
            if save_path:
                logger.info(f"💾 Current wallpaper saved to {save_path}")
            else:
                logger.error("❌ Failed to save wallpaper")
        else:
            logger.warning("⚠️ No current wallpaper found to save.")
    
    elif key_name == 'q':
        logger.info("👋 Manual exit requested")
        print(f"{colorama.Fore.YELLOW}Exiting by user request...{colorama.Style.RESET_ALL}")
        sys.exit(0)  # Use sys.exit instead of os._exit for cleaner exit

def manual_override_listener():
    """Set up a keyboard listener for manual overrides"""
    if not HAS_KEYBOARD:
        logger.warning("⚠️ Keyboard module not available - hotkeys will not work.")
        return
    
    try:
        # Direct method using on_press
        def on_key_press(key):
            if hasattr(key, 'name') and key.name in ['n', 's', 'q']:
                process_key_press({'name': key.name})
                
        keyboard.on_press(on_key_press)
        logger.info("🔑 Keyboard shortcuts registered: 'n' (new), 's' (save), 'q' (quit)")
    except Exception as e:
        logger.error(f"❌ Failed to register keyboard shortcuts: {e}")
        logger.warning("⚠️ Manual controls will not be available")


def display_categories(interactive: bool = False) -> Optional[str]:
    """Display all available categories, optionally interactively"""
    print(f"{colorama.Fore.CYAN}Available categories:{colorama.Style.RESET_ALL}")
    all_categories = sorted(CATEGORIES)
    cols = 3
    
    # Assign numbers for interactive mode
    numbered_categories = {}
    if interactive:
        for i, cat in enumerate(all_categories, 1):
            numbered_categories[str(i)] = cat
    
    # Display categories in columns
    for i in range(0, len(all_categories), cols):
        row = all_categories[i:i+cols]
        if interactive:
            indices = range(i+1, i+len(row)+1)
            row_with_nums = [f"{j}. {cat}" for j, cat in zip(indices, row)]
            print("  ".join(row_with_nums))
        else:
            print("  ".join(row))
    
    # Interactive selection
    if interactive:
        print(f"\n{colorama.Fore.YELLOW}Enter a number to select a category (or 0 for random):{colorama.Style.RESET_ALL}")
        choice = input("> ").strip()
        if choice == "0":
            return None  # Random
        elif choice in numbered_categories:
            return numbered_categories[choice]
        else:
            print(f"{colorama.Fore.RED}Invalid selection. Using default.{colorama.Style.RESET_ALL}")
            return DEFAULT_CATEGORY
    
    return None


def main_loop(interval: int, category: Optional[str] = None, auto_mode: bool = False, 
              search: Optional[str] = None, save: bool = False):
    """Main program loop that changes wallpaper at specified interval"""
    # Default interval if not provided
    if interval is None:
        interval = 15  # Default to 15 minutes
    
    max_interval = interval if interval else 60  # Default max interval is 60 minutes
    current_interval = interval  # Initialize current_interval here
    
    # Start keyboard listener in a separate thread
    override_thread = threading.Thread(target=manual_override_listener)
    override_thread.daemon = True
    override_thread.start()
    
    # Change wallpaper immediately at startup
    success = update_wallpaper(category, save, search)
    if not success:
        logger.error("❌ Failed to update wallpaper on startup.")
        return 1  # Exit with error
    
    last_update = datetime.now()
    
    try:
        while True:
            # Compute interval if in auto mode
            if auto_mode:
                current_interval = compute_auto_interval(max_interval)
                logger.info(f"⏱️ Auto interval: {current_interval} minute(s)")
            else:
                current_interval = interval  # Use fixed interval
                
            # Wait until next update
            seconds = current_interval * 60
            time.sleep(seconds)
            
            # Check if it's time to update again (in case of sleep interruptions)
            now = datetime.now()
            if (now - last_update).total_seconds() >= seconds:
                update_wallpaper(category, save, search)
                last_update = now
                
    except KeyboardInterrupt:
        logger.info("👋 Keyboard interrupt detected. Exiting...")
        return 0
    except Exception as e:
        logger.error(f"❌ Error in main loop: {e}")
        return 1


def main():
    """Main entry point for the application"""
    try:
        # Check for API key
        api_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
        if api_key and api_key != "-nQCvLoZDU_1rvFtaeokiDSbo3miLHKJVnVPUWx6iBQ":
            logger.info("🔑 Using configured Unsplash API key")
        else:
            logger.info("💡 Tip: Configure your Unsplash API key in .env for more image variety")
        
        # Parse command line arguments
        args = parse_arguments()
        
        # Load configuration from file if specified
        config = None
        try:
            config = Config(args.config) if hasattr(args, 'config') else None
        except Exception as e:
            logger.warning(f"⚠️ Failed to load config: {e}. Using defaults.")
        
        # If list_categories flag is set, display categories interactively
        chosen_category = None
        if args.list_categories:
            chosen_category = display_categories(interactive=True)
            # If user chose to exit, return
            if chosen_category == "exit":
                return 0
        
        # Determine category to use (prioritize command line, then interactive choice, then default)
        category = None
        if hasattr(args, 'category') and args.category:
            category = args.category
        elif chosen_category:
            category = chosen_category
        else:
            category = DEFAULT_CATEGORY
        
        # Check if we're using search term instead of category
        search = args.search if hasattr(args, 'search') else None
        if search:
            category = None  # If search is provided, override category
        
        # Log startup message with emojis
        if category:
            logger.info(f"🚀 Starting wallpaper changer. Category='{category}'")
        elif search:
            logger.info(f"🚀 Starting wallpaper changer. Search='{search}'")
        else:
            logger.info("🚀 Starting wallpaper changer with random images.")
            
        # Determine interval - make sure it's never None
        interval = 15  # Default to 15 minutes
        if hasattr(args, 'interval') and args.interval is not None:
            interval = args.interval
        
        # Check if we're in automatic interval mode
        auto_mode = args.auto if hasattr(args, 'auto') else False
        
        # Should we save downloaded wallpapers
        save = args.save if hasattr(args, 'save') else False
        
        if auto_mode:
            logger.info("⏱️ Interval mode: auto-adjusting based on rate limits.")
        else:
            logger.info(f"⏱️ Interval mode: fixed {interval} minute(s).")
            
        # Display hotkey information
        logger.info("🔄 Press 'n' to manually change wallpaper (desktop only).")
        logger.info("💾 Press 's' to save the current wallpaper (desktop only).")
        logger.info("❌ Press 'q' to exit (desktop only).")
        
        # Check if we're in once mode (just change once and exit)
        if args.once:
            success = update_wallpaper(category, save, search)
            if success:
                logger.info("✅ Wallpaper changed. Exiting.")
                return 0
            else:
                logger.error("❌ Failed to change wallpaper.")
                return 1
            
        # Start the main loop
        return main_loop(interval, category, auto_mode, search, save)
        
    except KeyboardInterrupt:
        logger.info("👋 Keyboard interrupt detected. Exiting...")
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
