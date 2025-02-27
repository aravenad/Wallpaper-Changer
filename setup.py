"""
This file is deprecated. Please use pyproject.toml instead.

This file is kept temporarily for backward compatibility and 
will be removed in the future.
"""

import warnings

warnings.warn(
    "Using setup.py is deprecated. Please use pyproject.toml for package configuration.", 
    DeprecationWarning,
    stacklevel=2
)

from setuptools import setup

if __name__ == "__main__":
    setup(
        name="wallpaper-changer",
        version="0.1.0",
        description="An application to automatically change desktop wallpapers",
        author="Damien",
        # Minimal setup to keep backward compatibility
        # All actual configuration is in pyproject.toml
    )
