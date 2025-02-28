# src/categories.py

"""
Module containing wallpaper categories for the Unsplash API.
"""

# List of available wallpaper categories
CATEGORIES = [
    # Nature
    "nature", "landscape", "forest", "mountains", "ocean", "beach", "sunset",
    "waterfall", "trees", "flowers", "wildlife", "desert", "sky", "underwater",
    "jungle", "river", "winter", "autumn", "spring", "summer", "stars",
    
    # Urban
    "architecture", "city", "street", "buildings", "urban", "night", "travel",
    "skyline", "bridge", "downtown", "traffic", "park",
    
    # Colors
    "blue", "red", "green", "yellow", "purple", "orange", "black", "white",
    
    # Styles
    "minimalist", "vintage", "modern", "abstract", "pattern", "texture",
    
    # Technology
    "technology", "computer", "digital", "space", "scifi", "cyberpunk",
    
    # Other
    "dark", "light", "wallpaper", "background", "art", "photography",
    "food", "car", "music", "sports", "animal", "pets",
    
    # Special
    "random"
]

# Remove any duplicates while preserving order
seen = set()
duplicates = [cat for cat in CATEGORIES if cat in seen or seen.add(cat)]
if duplicates:
    print(f"Removed {len(duplicates)} duplicates from categories: {', '.join(duplicates)}")
    
CATEGORIES = [cat for cat in CATEGORIES if cat in seen]

# For backward compatibility
get_categories = lambda: CATEGORIES
