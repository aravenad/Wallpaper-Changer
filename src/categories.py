# src/categories.py

"""
This module contains popular Unsplash categories.
These are collected from Unsplash's website and popular search topics.
"""

# First define all categories, then we'll deduplicate them
_CATEGORIES_WITH_DUPES = [
    # Nature
    "animals", "birds", "cats", "dogs", "fish", "flowers", "forest", 
    "garden", "landscape", "mountains", "nature", "ocean", "plants", 
    "river", "sea", "sky", "sunset", "trees", "water", "wildlife",
    
    # Urban & Architecture
    "architecture", "buildings", "city", "interior", "street", "urban",
    
    # Technology
    "computers", "coding", "data", "technology", "programming", "developer",
    
    # Art & Abstract
    "abstract", "art", "design", "digital-art", "geometric", "illustrations", 
    "minimal", "pattern", "texture", "3d-renders",
    
    # Travel & Places
    "beach", "desert", "europe", "islands", "japan", "travel", "tropical",
    
    # Food & Drinks
    "coffee", "drinks", "food", "fruits", "healthy",
    
    # People & Lifestyle
    "business", "fashion", "fitness", "lifestyle", "people", "portrait",
    
    # Transportation
    "cars", "motorcycle", "transportation",
    
    # Seasonal & Events
    "christmas", "halloween", "holiday", "summer", "winter",
    
    # Space & Science
    "astronomy", "galaxy", "mars", "milky-way", "moon", "planets", "science", "space", "stars",
    
    # Sports & Recreation
    "cycling", "hiking", "sports", "swimming",
    
    # Backgrounds & Textures
    "backgrounds", "dark", "gradients", "light", "texture", "wallpapers",
    
    # Gaming
    "gaming", "video-games",
    
    # Books & Education
    "books", "education", "library", "school",
    
    # Miscellaneous
    "random", "vintage"
]

# Deduplicate the list while preserving order
seen = set()
UNSPLASH_CATEGORIES = [x for x in _CATEGORIES_WITH_DUPES if not (x in seen or seen.add(x))]

# Print information about any duplicates that were found
duplicate_count = len(_CATEGORIES_WITH_DUPES) - len(UNSPLASH_CATEGORIES)
if duplicate_count > 0:
    # Find duplicates for information purposes
    from collections import Counter
    duplicates = [item for item, count in Counter(_CATEGORIES_WITH_DUPES).items() if count > 1]
    print(f"Removed {duplicate_count} duplicates from categories: {', '.join(duplicates)}")

def get_categories():
    """
    Get the list of available Unsplash categories.
    
    Returns:
        list: List of category strings
    """
    return UNSPLASH_CATEGORIES
