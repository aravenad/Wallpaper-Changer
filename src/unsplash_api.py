"""
Module for interacting with the Unsplash API.
"""
import logging
import os
import random
import time
import urllib.parse
from typing import Dict, List, Optional, Tuple

import requests

# Import categories directly from our module
# To prevent circular imports, include categories list directly
from src.categories import CATEGORIES

logger = logging.getLogger(__name__)

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.debug("Environment variables loaded from .env file")
except ImportError:
    logger.debug("dotenv package not available, skipping .env loading")

# API configuration - Check for the API key in environment variables
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
if not UNSPLASH_ACCESS_KEY:
    logger.warning("No Unsplash API key found. Using demo mode.")

# Use demo mode if explicitly requested or no key provided
DEMO_MODE = os.environ.get("USE_DEMO_MODE", "").lower() in ("true", "1", "yes", "y") or not UNSPLASH_ACCESS_KEY
UNSPLASH_API_URL = "https://api.unsplash.com/photos/random"

# Demo images to use when demo mode is enabled
DEMO_IMAGES = [
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
    "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
    "https://images.unsplash.com/photo-1497449493050-aad1e7cad165",
    "https://images.unsplash.com/photo-1472214103451-9374bd1c798e",
    "https://images.unsplash.com/photo-1429516387459-9891b7b96c78",
    "https://images.unsplash.com/photo-1433086966358-54859d0ed716",
    "https://images.unsplash.com/photo-1501854140801-50d01698950b",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e"
]


def fetch_wallpaper(category: Optional[str] = None, search_term: Optional[str] = None) -> Tuple[Optional[str], Dict]:
    """Fetch a random wallpaper from Unsplash with optional category or search term."""
    # Declare that we'll use the global DEMO_MODE variable
    global DEMO_MODE
    
    # Check if we're in demo mode
    if DEMO_MODE:
        logger.info("🧪 Using demo mode with local images.")
        # Return a random demo image
        image_url = random.choice(DEMO_IMAGES)
        # Add category info to URL for better tracking
        if category:
            image_url += f"?cat={category}"
        elif search_term:
            image_url += f"?search={urllib.parse.quote(search_term)}"
        else:
            image_url += "?cat=random"
            
        # Return dummy headers
        dummy_headers = {
            'X-Ratelimit-Limit': '50',
            'X-Ratelimit-Remaining': '49',
            'X-Ratelimit-Reset': str(int(time.time()) + 3600)
        }
        return image_url, dummy_headers
    
    # Build parameters for the API request
    params = {
        "featured": "true",
        "orientation": "landscape",
    }
    
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    try:
        # Handle category vs search priority
        if search_term:
            # If search term is provided, use search query
            params["query"] = search_term
            logger.info(f"🔍 Searching for wallpapers with term: {search_term}")
        elif category:
            # If category is provided, use it
            # Handle "random" category specially
            if category == "random" or not category:
                # Choose a random category from the list
                random_category = random.choice(CATEGORIES)
                params["query"] = random_category
                logger.info(f"🎲 Random category selected: {random_category}")
            else:
                params["query"] = category
                logger.info(f"🏷️ Using category: {category}")
        else:
            # Default to a random category if nothing specified
            random_category = random.choice(CATEGORIES)
            params["query"] = random_category
            logger.info(f"🏷️ No category specified. Using random category: {random_category}")

        # Make API request
        logger.debug(f"Making API request with key: {UNSPLASH_ACCESS_KEY[:5] if UNSPLASH_ACCESS_KEY else 'None'}...")
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params, timeout=10)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            
            # Get image URL for the appropriate resolution
            if "urls" in data:
                # Try full resolution first, then fall back to others
                image_url = data["urls"].get("full") or data["urls"].get("regular") or data["urls"].get("raw")
                
                if image_url:
                    logger.debug(f"Successfully retrieved image: {image_url[:50]}...")
                    return image_url, response.headers
            
            logger.error("Invalid response format from Unsplash API")
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            # If unauthorized, try again with demo mode
            if response.status_code == 401:
                logger.warning("API authentication failed. Switching to demo mode.")
                # Set demo mode for this session
                DEMO_MODE = True
                # Try again in demo mode
                return fetch_wallpaper(category, search_term)
        
        return None, {}
        
    except Exception as e:
        logger.error(f"Error fetching wallpaper: {e}")
        # Fall back to demo mode on error
        logger.warning("Error occurred. Switching to demo mode.")
        # Set demo mode for this session
        DEMO_MODE = True
        # Try again in demo mode
        return fetch_wallpaper(category, search_term)
