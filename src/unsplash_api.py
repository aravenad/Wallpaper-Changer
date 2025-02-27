# src/unsplash_api.py

import random
import requests
import os
import logging
from . import config

# Setup logger directly in this file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def fetch_wallpaper(category):
    """
    Fetch a random wallpaper from Unsplash for the given category.
    If category is a list, one is chosen at random.
    Returns (image_path, x_ratelimit_remaining) on success.
    """
    params = {"orientation": "landscape"}
    
    # Handle multiple categories by choosing one randomly
    chosen_category = None
    if isinstance(category, list):
        if category:
            chosen_category = random.choice(category)
            logger.info(f"Randomly selected '{chosen_category}' from your categories.")
        else:
            chosen_category = "random"
    else:
        chosen_category = category
    
    # Set the query parameter if not using "random"
    if chosen_category.lower() != "random":
        params["query"] = chosen_category

    headers = {"Authorization": f"Client-ID {config.ACCESS_KEY}"}
    try:
        response = requests.get(config.API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching photo metadata: {e}")
        return None, None

    rl = response.headers.get("X-Ratelimit-Remaining")
    data = response.json()
    if "urls" not in data:
        logger.error("Unexpected response format from Unsplash.")
        return None, None

    image_url = data["urls"]["raw"] + "&w=3840&q=80"
    try:
        img_resp = requests.get(image_url, stream=True, timeout=15)
        img_resp.raise_for_status()
        # Ensure IMG_DIR exists
        if not os.path.exists(config.IMG_DIR):
            os.makedirs(config.IMG_DIR)
        img_path = os.path.join(config.IMG_DIR, "wallpaper.jpg")
        with open(img_path, "wb") as f:
            for chunk in img_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return img_path, rl
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None, rl
