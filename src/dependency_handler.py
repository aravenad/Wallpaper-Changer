"""
Dependency Handler - Automatically checks and installs missing dependencies

This module ensures all required dependencies are available before importing them
in other modules, which prevents import errors during runtime.
"""

import sys
import subprocess
import importlib
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("dependency_handler")

# Define required packages and their pip package names (if different)
REQUIRED_PACKAGES = {
    'colorama': 'colorama',
    'keyboard': 'keyboard',
    'requests': 'requests',
    'pytest': 'pytest',
    'win32gui': 'pywin32',  # Maps module name to package name
    'PIL': 'pillow',
    'setuptools': 'setuptools',
}

def is_package_installed(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    pip_pkg = REQUIRED_PACKAGES.get(package_name, package_name)
    try:
        logger.info(f"Installing {pip_pkg}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_pkg], 
                             stdout=subprocess.DEVNULL)
        logger.info(f"Successfully installed {pip_pkg}")
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to install {pip_pkg}")
        return False

def ensure_dependencies(package_list=None):
    """
    Ensure all dependencies are installed.
    
    Args:
        package_list: List of package names to check and install,
                      or None to check all REQUIRED_PACKAGES
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    packages_to_check = package_list or list(REQUIRED_PACKAGES.keys())
    missing_packages = [pkg for pkg in packages_to_check if not is_package_installed(pkg)]
    
    if not missing_packages:
        return True
    
    logger.info("Installing missing dependencies...")
    
    all_success = True
    for package in missing_packages:
        if not install_package(package):
            all_success = False
    
    if all_success:
        logger.info("All dependencies are now installed.")
    else:
        logger.warning("Some dependencies could not be installed.")
    
    return all_success

if __name__ == "__main__":
    # When run as a script, check and install all dependencies
    ensure_dependencies()
