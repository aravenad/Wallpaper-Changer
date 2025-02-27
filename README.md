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

### For Developers

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/wallpaper-changer.git
   cd wallpaper-changer
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   # Windows:
   setup.bat
   
   # macOS/Linux:
   ./setup.sh
   ```

   Alternatively, use the helper script directly:
   ```bash
   python create_venv.py
   ```

3. Activate the environment:
   ```bash
   # Windows:
   .venv\Scripts\activate
   
   # macOS/Linux:
   source .venv/bin/activate
   ```

## 🎮 Usage

### Command-line Arguments

```bash
wallpaper-changer [options]

Options:
  --config, -c    Path to a custom configuration file (default: settings.json)
  --interval, -i  Time between wallpaper changes in minutes
  --source, -s    Directory or URL for wallpapers
  --once          Change wallpaper once and exit
```

### Examples

```bash
# Change wallpaper once and exit
wallpaper-changer --once

# Use images from a specific folder with a 1-hour interval
wallpaper-changer --source "C:\My Wallpapers" --interval 60

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

## 🐛 Troubleshooting

### Common Issues

1. **Wallpaper not changing**
   - Check your internet connection
   - Verify the wallpaper directory exists and is writable
   - Check logs for error messages

2. **Installation issues**
   - Make sure you have the correct Python version
   - Try running `create_venv.py` with administrator privileges
   - Verify that your pip can access external packages

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
