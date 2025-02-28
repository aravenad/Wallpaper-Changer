# Unsplash Wallpaper Changer

![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automatically changes your desktop wallpaper at regular intervals with beautiful high-resolution images from Unsplash.

![Wallpaper Example](./img/example/readme.jpg)

## ✨ Features

- 🖼️ **Auto-update wallpapers** at fixed or adaptive intervals  
- 🔄 **Manual override** with hotkeys when you want a new image
- 💾 **Save your favorite wallpapers** with a single keystroke  
- 🔍 **Multiple category support** with automatic rotation
- ⚡ **Adaptive rate limit handling** to stay within Unsplash API limits
- 🌈 **Colorful terminal output** for better usability
- 🧪 **Comprehensive test suite** for reliability
- 🚫 **Demo mode** - works without an API key using curated images

## 🔧 Requirements

- Python 3.6 or higher
- Windows, macOS, or Linux (cross-platform support)
- Internet connection for downloading images

## 🚀 Quick Start

### For End Users

**Windows:**
```bash
# Just run the batch script:
run.bat
```

**macOS/Linux:**
```bash
# Make the script executable (first time only):
chmod +x run.sh

# Run the script:
./run.sh
```

## API Key Setup (Optional)

By default, the application runs in demo mode with a selection of high-quality images. For more variety, get your own Unsplash API key:

1. Sign up at [Unsplash Developers](https://unsplash.com/developers)
2. Create a new application
3. Copy your Access Key
4. Create a `.env` file in the project root with:
   ```
   UNSPLASH_ACCESS_KEY=your_access_key_here
   ```

## 🎮 Usage

### Command-line Arguments

```bash
wallpaper-changer [options]

Options:
  --config, -c       Path to a custom configuration file (default: settings.json)
  --interval, -i     Time between wallpaper changes in minutes (default: 15)
  --category, -cat   Specific wallpaper category to use
  --search           Search term for wallpapers
  --auto, -a         Auto-adjust interval based on API limits
  --once             Change wallpaper once and exit
  --save             Save downloaded wallpaper
  --list-categories  List available categories and exit
```

### Examples

```bash
# Change wallpaper once and exit
wallpaper-changer --once

# Use nature category with a 1-hour interval
wallpaper-changer --category nature --interval 60

# Search for specific wallpapers
wallpaper-changer --search "mountain sunset"

# Use custom configuration file
wallpaper-changer --config my_settings.json
```

## ⚙️ Configuration

Edit `settings.json` to change settings or create your own configuration file:

```json
{
    "interval": 30,
    "source": "wallpapers",
    "random": true,
    "save_downloaded": true,
    "download_folder": "wallpapers",
    "fit_mode": "fill"
}
```

## 🗂️ Saved Wallpapers

Your favorite wallpapers can be saved to the `img/saved` directory with sequential numbering:

- `wallpaper-001.jpg`
- `wallpaper-002.jpg`
- etc.

## ⌨️ Keyboard Shortcuts

While the application is running:
- `n` - Manually change to a new wallpaper
- `s` - Save the current wallpaper to your saved collection
- `q` - Quit the application

## 🐛 Troubleshooting

### Common Issues

1. **Keyboard shortcuts not working**
   - Make sure the terminal window is not in focus
   - Try running with administrator privileges
   - Check that the keyboard module is installed

2. **Wallpaper not changing**
   - Check your internet connection
   - Verify the wallpaper directory exists and is writable
   - Check logs for error messages

3. **Installation issues**
   - Make sure you have the correct Python version
   - Try running `create_venv.py` with administrator privileges
   - Verify that your pip can access external packages

4. **API Key issues**
   - The app will work in demo mode without an API key
   - Check your `.env` file format
   - Verify your Unsplash API key is valid

## 🧪 Development

### Virtual Environment

This project uses `.venv` as the standard directory for virtual environments:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install development dependencies
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
pytest --cov
```

### Code formatting

Format the code with black:
```
black src tests
```

## 📂 Project Structure

```
wallpaper-changer/
├── src/
│   └── wallpaper_changer/    # Main package
│       ├── __init__.py       # Package definition
│       ├── main.py           # Entry point
│       ├── config.py         # Configuration handling
│       └── wallpaper_handler.py  # Wallpaper operations
├── tests/                    # Test directory
├── wallpapers/               # Default wallpapers directory
├── img/
│   └── saved/                # Directory for saved wallpapers
├── .venv/                    # Virtual environment (not in repo)
├── pyproject.toml            # Project configuration
├── create_venv.py            # Virtual environment setup helper
├── setup.bat                 # Windows setup script
├── setup.sh                  # Unix setup script 
├── run.bat                   # Windows quick start
├── run.sh                    # Unix quick start
└── README.md                 # This documentation
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [Unsplash](https://unsplash.com/) for providing the amazing wallpaper API
- All contributors and users of this project
