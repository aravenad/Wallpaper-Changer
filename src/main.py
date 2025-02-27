import time
import threading
import queue
import sys
import importlib
import os
import json

# Import logger first so it's available for all modules
from .logger import logger
from .wallpaper import set_wallpaper, save_current_wallpaper, get_current_wallpaper
from .categories import get_categories

# Better import handling with more robust keyboard mock
def import_optional(module_name):
    """Import a module if available, otherwise return None"""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Try to import keyboard with a more robust fallback
keyboard_module = import_optional('keyboard')
if keyboard_module is not None:
    keyboard = keyboard_module
else:
    # Create a more comprehensive mock for keyboard
    class MockKeyboard:
        @staticmethod
        def read_key(suppress=False):
            """Mock implementation of keyboard.read_key"""
            time.sleep(0.1)  # Prevent CPU spike in busy wait loops
            return ""
        
        @staticmethod
        def is_pressed(key):
            """Mock implementation of keyboard.is_pressed"""
            return False
        
        @staticmethod
        def on_press(callback):
            """Mock implementation of keyboard.on_press"""
            return lambda: None  # Return a dummy unregister function
            
        @staticmethod
        def on_release(callback):
            """Mock implementation of keyboard.on_release"""
            return lambda: None  # Return a dummy unregister function
            
        @staticmethod
        def wait(key=None):
            """Mock implementation of keyboard.wait"""
            while True:
                time.sleep(1)
    
    keyboard = MockKeyboard()
    logger.warning("Keyboard module not available. Using mock implementation.")

# Try to import win32gui with fallback
win32gui = import_optional('win32gui')

# Import remaining modules
from . import config, cli, unsplash_api, wallpaper
from . import init_dirs

# Global state variables
requests_remaining = config.RATE_LIMIT_PER_HOUR
hour_start = None
command_queue = queue.Queue()
exit_flag = threading.Event()

# -----------------------------------------------------------------------------
# Rate Limiting & Interval Management
# -----------------------------------------------------------------------------

def compute_auto_interval(remaining_requests=None, start_time=None, reserved_requests=None):
    """
    Compute the optimal interval between API calls based on rate limits.
    
    Args:
        remaining_requests (int, optional): Number of requests remaining in current hour
        start_time (float, optional): Timestamp when the hour started 
        reserved_requests (int, optional): Number of requests to reserve for manual actions
    
    Returns:
        float: Interval in seconds between wallpaper updates
    """
    # Use global state or provided parameters
    global hour_start, requests_remaining
    
    current_remaining = remaining_requests if remaining_requests is not None else requests_remaining
    current_hour_start = start_time if start_time is not None else hour_start
    reserved = reserved_requests if reserved_requests is not None else config.RESERVED_FOR_MANUAL
    
    # If hour hasn't started yet, use default interval
    if current_hour_start is None:
        return 90.0
        
    elapsed = time.time() - current_hour_start
    
    # If more than an hour has passed, reset the counter
    if elapsed >= 3600:
        if remaining_requests is None:  # Only update globals if not in test mode
            hour_start = time.time()
            requests_remaining = config.RATE_LIMIT_PER_HOUR
        return 90.0
        
    # Calculate time remaining in the current hour
    seconds_left = 3600 - elapsed
    
    # Calculate usable requests (total minus reserved)
    usable = current_remaining - reserved
    
    # If no usable requests remaining, wait 10 minutes
    if usable <= 0:
        logger.warning("No usable requests left. Sleeping 10 minutes.")
        return 600.0
        
    # Calculate interval to distribute remaining requests over the hour
    interval = seconds_left / float(usable)
    
    # Enforce minimum interval
    if interval < 30.0:
        interval = 30.0
        
    logger.info(f"[Auto Interval] Next update in ~{int(interval)} second(s). Requests left: {current_remaining}")
    return interval

def update_rate_limits(response_headers):
    """
    Update rate limit information based on API response headers.
    
    Args:
        response_headers (dict): Headers from API response
        
    Returns:
        int: Updated requests remaining count
    """
    global requests_remaining, hour_start
    
    # Get rate limit header
    rl = response_headers.get('X-Ratelimit-Remaining')
    
    if rl is not None:
        try:
            requests_remaining = int(rl)
        except ValueError:
            # Header exists but isn't a valid integer
            pass
        
        # Initialize hour start time if not set
        if hour_start is None:
            hour_start = time.time()
    
    return requests_remaining

# -----------------------------------------------------------------------------
# Wallpaper Operations 
# -----------------------------------------------------------------------------

def fetch_wallpaper(query=None, featured=False):
    """
    Fetch a wallpaper from Unsplash API
    
    Args:
        query (str, optional): Search term or category
        featured (bool, optional): Whether to use only featured images
    
    Returns:
        dict: Dictionary with file_path and source_url, or None if failed
    """
    try:
        # This is a wrapper around unsplash_api.get_random_photo
        from . import unsplash_api
        # Pass the query as the positional argument that's expected
        img_path, rl = unsplash_api.fetch_wallpaper(query)
        
        # Update rate limits
        if rl is not None:
            update_rate_limits({'X-Ratelimit-Remaining': rl})
        
        if img_path:
            # Return the expected dictionary format
            return {'file_path': img_path, 'source_url': ''}
        return None
    except Exception as e:
        logger.error(f"Error fetching wallpaper: {str(e)}")
        return None

def update_wallpaper(category=None, search=None, save=False, featured=False):
    """
    Update the wallpaper with options to filter by category, search terms, and other options.
    
    Args:
        category (str, optional): Category to filter wallpaper by
        search (str, optional): Search terms to find wallpaper
        save (bool, optional): Whether to save a copy of the wallpaper
        featured (bool, optional): Whether to use only featured images
        
    Returns:
        str: Path to the wallpaper that was set, or None if failed
    """
    # Call the API to fetch a new wallpaper
    query = search or category
    result = fetch_wallpaper(query, featured=featured)
    
    if not result:
        logger.error("Failed to fetch wallpaper")
        return None
    
    # Set the wallpaper
    set_wallpaper(result['file_path'])
    
    # Save it if requested
    if save:
        # Pass both file_path and source_url to save_current_wallpaper
        save_current_wallpaper(result['file_path'], result['source_url'])
    
    return result['file_path']

def update_wallpaper_cmd(trigger_type, category):
    """
    Update wallpaper and handle rate limiting based on trigger type.
    
    Args:
        trigger_type (str): Type of trigger (auto/manual)
        category (str): Category to use for wallpaper
    """
    global hour_start, requests_remaining
    
    # Call the API to fetch a new wallpaper
    img_path, rl = unsplash_api.fetch_wallpaper(category)
    
    # Update rate limits
    if rl is not None:
        try:
            requests_remaining = int(rl)
        except ValueError:
            pass
        if hour_start is None:
            hour_start = time.time()
    
    # Set the wallpaper if fetched successfully
    if img_path:
        wallpaper.set_wallpaper(img_path)
        logger.info(f"[✓] Wallpaper updated ({trigger_type}). Requests left: {requests_remaining}")
        
        # Reset hour start time for manual updates
        if trigger_type == "manual":
            hour_start = time.time()
    else:
        logger.error("Failed to update wallpaper.")

def display_categories():
    """
    Display available wallpaper categories
    """
    categories = get_categories()
    print("Available categories:")
    for cat in categories:
        print(f"- {cat}")

# -----------------------------------------------------------------------------
# User Interface & Input Handling
# -----------------------------------------------------------------------------

def is_desktop_foreground():
    """
    Check if Windows desktop is in foreground.
    
    Returns:
        bool: True if desktop is in foreground, False otherwise
    """
    if win32gui is None:
        # If win32gui is not available, assume desktop is in foreground (for testing)
        return True
        
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        cls = win32gui.GetClassName(hwnd)
        return cls in ("Progman", "WorkerW")
    return False

def process_key_press(key, last_manual_time=0.0, last_cooldown_print=0.0):
    """
    Process a keyboard key press event.
    
    Args:
        key (str): The key that was pressed
        last_manual_time (float): Time of last manual wallpaper change
        last_cooldown_print (float): Time of last cooldown message
        
    Returns:
        tuple: (command, trigger_type, updated_last_manual_time, updated_last_cooldown_print)
    """
    global requests_remaining
    
    # Default return values (no command)
    command = None
    trigger_type = None
    new_last_manual_time = last_manual_time
    new_last_cooldown_print = last_cooldown_print
    
    # Process different key commands
    if key == 'n':  # New wallpaper
        if not is_desktop_foreground():
            logger.warning("Ignoring manual override because you're not on the desktop.")
            return (None, None, last_manual_time, last_cooldown_print)
            
        now = time.time()
        # Check cooldown period
        if now - last_manual_time < config.MANUAL_COOLDOWN:
            remain = int(config.MANUAL_COOLDOWN - (now - last_manual_time))
            if now - last_cooldown_print >= 1:
                next_update = compute_auto_interval()
                logger.warning(f"Manual override cooling down. Please wait {remain}s. Next auto update in ~{int(next_update)}s.")
                new_last_cooldown_print = now
            return (None, None, last_manual_time, new_last_cooldown_print)
            
        # Check rate limits
        if requests_remaining <= 0:
            logger.warning("No requests left this hour. Can't do manual override.")
            return (None, None, last_manual_time, last_cooldown_print)
            
        # Process manual override
        logger.info("Manual override triggered! Changing wallpaper...")
        command = "update"
        trigger_type = "manual"
        new_last_manual_time = now
        
    elif key == 's':  # Save wallpaper
        if not is_desktop_foreground():
            logger.warning("Ignoring save command because you're not on the desktop.")
            return (None, None, last_manual_time, last_cooldown_print)
            
        logger.info("Save command triggered! Saving current wallpaper...")
        command = "save"
        
    elif key == 'q':  # Quit
        if not is_desktop_foreground():
            logger.warning("Ignoring exit because you're not on the desktop.")
            return (None, None, last_manual_time, last_cooldown_print)
            
        logger.info("Exiting wallpaper changer.")
        exit_flag.set()
        command = "exit"
        
    return (command, trigger_type, new_last_manual_time, new_last_cooldown_print)

def manual_override_listener(category):
    """
    Listen for keyboard input to manually change wallpapers.
    
    Args:
        category (str): Category to use for wallpaper
    """
    last_manual_time = 0.0
    last_cooldown_print = 0.0
    last_key_press_time = 0
    key_press_cooldown = 0.3  # 300ms cooldown between key presses to prevent duplicates
    
    # Check if keyboard functionality is available
    if not hasattr(keyboard, 'read_key'):
        logger.error("Keyboard functionality is not available. Manual controls disabled.")
        # Just wait until the program exits
        while not exit_flag.is_set():
            time.sleep(1)
        return
    
    # Main listener loop
    while not exit_flag.is_set():
        try:
            key = keyboard.read_key(suppress=False)
            
            # Ignore empty keys or non-string keys
            if not key or not isinstance(key, str):
                time.sleep(0.1)
                continue
            
            key = key.lower()
            
            # Prevent duplicate key presses by adding a cooldown
            current_time = time.time()
            if current_time - last_key_press_time < key_press_cooldown:
                time.sleep(0.05)  # Small sleep to prevent CPU spike
                continue
            
            last_key_press_time = current_time
            
            # Process the key press
            command, trigger_type, last_manual_time, last_cooldown_print = process_key_press(
                key, last_manual_time, last_cooldown_print)
                
            # Add command to queue if applicable
            if command == "update":
                command_queue.put((command, trigger_type))
            elif command == "save":
                command_queue.put((command, None))
            elif command == "exit":
                sys.exit(0)
                
        except Exception as e:
            logger.error(f"Error in keyboard handling: {e}")
            time.sleep(1)  # Avoid CPU spike if we're having errors

def process_commands():
    """
    Process commands from the command queue.
    
    Returns:
        bool: True if commands were processed, False otherwise
    """
    commands_processed = False
    
    while not command_queue.empty():
        try:
            cmd, trig = command_queue.get_nowait()
            if cmd == "update":
                update_wallpaper_cmd(trig, None)  # Category is None here - will need to be fixed
            elif cmd == "save":
                wallpaper.save_current_wallpaper()
            commands_processed = True
        except queue.Empty:
            break
            
    return commands_processed

# -----------------------------------------------------------------------------
# Auto Wallpaper Changer Operation
# -----------------------------------------------------------------------------

def handle_auto_mode(auto_interval=None):
    """
    Run the wallpaper changer in auto mode, updating at computed intervals
    
    Args:
        auto_interval (int): Maximum interval between updates in seconds
    """
    try:
        while True:
            # Update wallpaper
            update_wallpaper()
            
            # Calculate interval until next update
            interval = compute_auto_interval()
            if auto_interval and interval > auto_interval:
                interval = auto_interval
                
            # Wait for the computed interval
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting auto mode")

def main_loop(auto_mode, fixed_interval, category):
    """
    Main application loop - updates wallpapers periodically and handles user commands.
    
    Args:
        auto_mode (bool): Whether to use auto interval mode
        fixed_interval (float): Fixed interval in minutes (used if auto_mode is False)
        category (str): Category to use for wallpapers
    """
    while not exit_flag.is_set():
        # Process any pending commands
        process_commands()
        
        # Update wallpaper
        update_wallpaper_cmd("auto", category)
        
        # Determine sleep time
        if auto_mode:
            sleep_sec = compute_auto_interval()
        else:
            sleep_sec = fixed_interval * 60
            
        # Wait for the specified interval
        t0 = time.time()
        ten_sec_logged = False
        
        while time.time() - t0 < sleep_sec and not exit_flag.is_set():
            # Show imminent update notification
            remaining = sleep_sec - (time.time() - t0)
            if remaining <= 10 and not ten_sec_logged:
                logger.info(f"[Auto Update Imminent] Next update in ~{int(remaining)} second(s).")
                ten_sec_logged = True
                
            # Process any commands while waiting
            process_commands()
                
            # Small sleep to prevent CPU spiking
            time.sleep(0.5)

# -----------------------------------------------------------------------------
# JSON Config Functions
# -----------------------------------------------------------------------------

def read_requests_log(log_path):
    """
    Read the requests log file
    
    Args:
        log_path: Path to the log file
    
    Returns:
        dict: Log data as a dictionary with 'requests' key
    """
    if not os.path.exists(log_path):
        return {"requests": []}
    
    try:
        with open(log_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"requests": []}

def write_requests_log(log_path, data):
    """
    Write data to the requests log file
    
    Args:
        log_path: Path to the log file
        data: Dictionary with 'requests' key to write
    """
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=2)

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

def run():
    """
    Main entry point function for the application.
    Returns exit code.
    """
    try:
        # Ensure required directories exist
        init_dirs.ensure_directories()
        
        # Parse command-line arguments
        args = cli.parse_args()
        category = cli.select_category()
        
        # Determine interval mode
        auto_mode = (args.interval.lower() == "auto")
        if not auto_mode:
            try:
                fixed_interval = float(args.interval)
            except ValueError:
                fixed_interval = config.DEFAULT_INTERVAL
        else:
            fixed_interval = None

        # Display category info with special handling for multiple categories
        if isinstance(category, list):
            category_display = f"[{', '.join(category)}]"
        else:
            category_display = f"'{category}'"
            
        # Output startup information
        logger.info(f"Starting wallpaper changer. Category={category_display}")
        if auto_mode:
            logger.info("[!] Interval mode: auto (adaptive to remaining requests).")
        else:
            logger.info(f"[!] Interval mode: fixed {fixed_interval} minute(s).")
        logger.info("Press 'n' to manually change wallpaper (desktop only).")
        logger.info("Press 's' to save the current wallpaper (desktop only).")
        logger.info("Press 'q' to exit (desktop only).")

        # Start keyboard listener thread
        threading.Thread(target=manual_override_listener, args=(category,), daemon=True).start()
        
        # Run main application loop
        main_loop(auto_mode, fixed_interval, category)
        return 0
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Exiting...")
        exit_flag.set()
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(run())
