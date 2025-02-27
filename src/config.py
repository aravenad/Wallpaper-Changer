# src/config.py

# Unsplash API configuration
ACCESS_KEY = "-nQCvLoZDU_1rvFtaeokiDSbo3miLHKJVnVPUWx6iBQ"
API_URL = "https://api.unsplash.com/photos/random"

# Wallpaper update settings
RESERVED_FOR_MANUAL = 10       # Reserve 10 requests per hour for manual override
MANUAL_COOLDOWN = 60           # Seconds to wait between manual updates
DEFAULT_INTERVAL = 1.5         # Default fixed interval (in minutes)

# Logging settings
LOG_LEVEL = "INFO"             # Options: DEBUG, INFO, WARN, ERROR

# Other settings
RATE_LIMIT_PER_HOUR = 50       # For Unsplash API demo keys

# Directory where wallpapers are stored
IMG_DIR = "img"

# Directory where saved wallpapers are stored - now a subdirectory of IMG_DIR
SAVED_DIR = "img/saved"
