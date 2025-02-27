# src/cli.py

import argparse
import sys
import random
from .categories import get_categories
from .logger import logger
from . import config

# Cache for imported functions to avoid circular imports
_update_wallpaper = None
_handle_auto_mode = None
_display_categories = None

def parse_args():
    """
    Parse command-line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Change your desktop wallpaper with images from Unsplash."
    )
    
    # General options
    parser.add_argument("-c", "--category", default="random",
                       help="Category to filter by (e.g., 'nature', 'architecture')")
    parser.add_argument("-s", "--search", help="Search term(s), comma-separated")
    parser.add_argument("-f", "--featured", action="store_true", help="Get only featured photos")
    parser.add_argument("--save", action="store_true", help="Save a copy of the wallpaper")
    parser.add_argument("-l", "--list-categories", action="store_true", help="List available categories")
    
    # Auto-update options
    parser.add_argument("-a", "--auto", action="store_true", help="Run in auto-update mode")
    parser.add_argument("-i", "--interval", default="1.5", 
                        help="Update interval in minutes, or 'auto' for adaptive interval")
    parser.add_argument("--auto-interval", type=int, default=None,
                        help="Maximum interval in seconds for auto mode")
    
    return parser.parse_args()

def select_category():
    """
    Select a category based on command-line arguments or default to random
    
    Returns:
        str: Selected category
    """
    args = parse_args()
    
    if args.search:
        # If search is provided, don't use a category
        return None
        
    if args.category:
        if args.category.lower() == "random":
            return random.choice(get_categories())
        return args.category
    
    # Default to random category
    return random.choice(get_categories())

def display_categories():
    """Display available categories"""
    categories = get_categories()
    print("\nAvailable categories:")
    
    # Display in columns
    cols = 4
    col_width = max(len(cat) for cat in categories) + 2
    
    for i, category in enumerate(sorted(categories)):
        if i % cols == 0 and i > 0:
            print()
        print(f"{category:{col_width}}", end="")
    
    print("\n")

def update_wallpaper(*args, **kwargs):
    """Proxy for imported update_wallpaper function"""
    global _update_wallpaper
    if _update_wallpaper is None:
        from .main import update_wallpaper as main_update_wallpaper
        _update_wallpaper = main_update_wallpaper
    return _update_wallpaper(*args, **kwargs)

def handle_auto_mode(*args, **kwargs):
    """Proxy for imported handle_auto_mode function"""
    global _handle_auto_mode
    if _handle_auto_mode is None:
        from .main import handle_auto_mode as main_handle_auto_mode
        _handle_auto_mode = main_handle_auto_mode
    return _handle_auto_mode(*args, **kwargs)

def run_cli():
    """Main CLI entry point - parse arguments and run appropriate command"""
    args = parse_args()
    
    # Handle list categories first
    if args.list_categories:
        display_categories()
        return
    
    # Handle auto mode
    if args.auto:
        try:
            handle_auto_mode(args.auto_interval)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Exiting.")
        return
    
    # Handle one-time wallpaper update
    update_wallpaper(
        category=args.category,
        search=args.search,
        save=args.save,
        featured=args.featured
    )

if __name__ == "__main__":
    run_cli()
