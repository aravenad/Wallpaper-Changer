# Unsplash Wallpaper Changer

![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automatically changes your desktop wallpaper at regular intervals with beautiful high-resolution images from Unsplash.

![Wallpaper Example](./img/wallpaper.jpg)

## ✨ Features

- 🖼️ **Auto-update wallpapers** at fixed or adaptive intervals  
- 🔄 **Manual override** with hotkeys when you want a new image
- 💾 **Save your favorite wallpapers** with a single keystroke  
- 🔍 **Multiple category support** with automatic rotation
- ⚡ **Adaptive rate limit handling** to stay within Unsplash API limits
- 🌈 **Colorful terminal output** for better usability
- 🧪 **Comprehensive test suite** for reliability

## 🔧 Requirements

- Python 3.6 or higher
- Windows operating system (wallpaper setting is Windows-specific)
- Internet connection for downloading images

## 🚀 Quick Start

### Method 1: Simple Installation (Recommended)

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/wallpaper_changer.git
   cd wallpaper_changer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python wallpaper_changer.py --interval auto --categories-list
   ```

### Method 2: For Windows Users

1. Download and extract the repository
2. Double-click on `run.bat`
3. Follow the on-screen prompts to select categories

## 🎮 Usage

### Command-line Arguments

- `-i, --interval`: Interval in minutes between updates (default: 1.5, use "auto" for adaptive)
- `-c, --category`: Single category to use (e.g. 'nature', 'space', 'random')
- `--categories-list`: Show available categories and prompt for selection

### Examples

```bash
# Use auto interval with interactive category selection
python wallpaper_changer.py --interval auto --categories-list

# Update every 5 minutes with nature images
python wallpaper_changer.py --interval 5 --category nature

# Use multiple categories in one command
python wallpaper_changer.py --interval auto --category "nature space architecture"
```

### Keyboard Shortcuts

These shortcuts work only when the desktop is in focus:

- `n`: Manually get a new wallpaper
- `s`: Save the current wallpaper to the saved folder
- `q`: Quit the application

## ⚙️ Configuration

Edit `src/config.py` to change settings:

```python
# Unsplash API configuration
ACCESS_KEY = "your-unsplash-api-key"  # Default key is for demo use only

# Update settings
RESERVED_FOR_MANUAL = 10              # Reserve requests for manual override
MANUAL_COOLDOWN = 60                  # Seconds to wait between manual updates
DEFAULT_INTERVAL = 1.5                # Default interval (minutes)

# Directory settings 
IMG_DIR = "img"                       # Where current wallpaper is stored
SAVED_DIR = "img/saved"               # Where saved wallpapers go
```

## 🗂️ Saved Wallpapers

Your favorite wallpapers can be saved by pressing 's' when the desktop is in focus.
Saved wallpapers are stored in the 'saved' directory with sequential numbering:

- `wallpaper-001.jpg`
- `wallpaper-002.jpg`
- etc.

## 🐛 Troubleshooting

### Common Issues

1. **No keyboard input detected**
   - Make sure the desktop window is active/in focus
   - Check if you have admin rights
   - Try reinstalling the keyboard module: `pip install keyboard --upgrade`

2. **API rate limit reached**
   - The application will automatically slow down
   - Wait for the rate limit to reset (about an hour)
   - Default API key has limited requests, consider getting your own

3. **Wallpaper not changing**
   - Check your internet connection
   - Verify the img directory exists and is writable
   - Check console for error messages

## 🧪 Development

### Setting up a development environment

```bash
# Install dev dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

Or for more detailed output:

```bash
pytest -v
```

To generate a test coverage report:

```bash
pytest --cov=src
```

## 📂 Project Structure

```
.
├── .vscode/                  # VS Code configuration
├── img/                      # Contains downloaded wallpaper images
│   ├── saved/                # Directory for saved wallpapers
├── src/                      # Source code directory
│   ├── categories.py         # Category definitions
│   ├── cli.py                # Command-line interface
│   ├── config.py             # Configuration settings
│   ├── dependency_handler.py # Dependency management
│   ├── init_dirs.py          # Directory initialization
│   ├── logger.py             # Logging configuration
│   ├── main.py               # Main program logic
│   ├── unsplash_api.py       # Unsplash API interaction
│   └── wallpaper.py          # Wallpaper setting functions
├── tests/                    # Test suite
├── README.md                 # This documentation
├── requirements.txt          # Dependencies
└── wallpaper_changer.py      # Main entry point
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [Unsplash](https://unsplash.com/) for providing the amazing wallpaper API
- All contributors and users of this project
