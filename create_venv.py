#!/usr/bin/env python3
"""
Helper script to create a standardized .venv virtual environment.
"""
import os
import platform
import shutil
import subprocess
import sys


def main():
    """Create a standardized .venv virtual environment."""
    print("Setting up a standardized .venv virtual environment...")
    
    # Check if legacy virtual environment directories exist and offer to delete them
    legacy_dirs = ['venv', 'env', 'ENV']
    found_legacy_dirs = [d for d in legacy_dirs if os.path.exists(d)]
    
    if found_legacy_dirs:
        for dir_name in found_legacy_dirs:
            print(f"Legacy virtual environment '{dir_name}' detected.")
        
        response = input("Would you like to delete these legacy environments? (y/n): ")
        if response.lower() == 'y':
            for dir_name in found_legacy_dirs:
                try:
                    print(f"Removing {dir_name}...")
                    shutil.rmtree(dir_name)
                    print(f"Successfully removed {dir_name}")
                except Exception as e:
                    print(f"Error removing {dir_name}: {e}")
                    print(f"Please remove {dir_name} manually if needed.")
        else:
            print("Legacy environments will be kept.")
    
    # Check if .venv already exists
    if os.path.exists('.venv'):
        response = input(".venv directory already exists. Replace it? (y/n): ")
        if response.lower() == 'y':
            print("Removing existing .venv directory...")
            # On Windows, sometimes we need to handle permission errors differently
            try:
                shutil.rmtree('.venv')
            except Exception as e:
                print(f"Error removing .venv: {e}")
                print("Please remove it manually and try again.")
                return 1
        else:
            print("Operation canceled.")
            return 0
    
    # Create the virtual environment
    print("Creating new .venv environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to create virtual environment. Is 'venv' module installed?")
        return 1
    
    # Determine paths based on the platform
    if platform.system() == 'Windows':
        python_path = os.path.abspath('.venv\\Scripts\\python.exe')
        activate_script = '.venv\\Scripts\\activate.bat'
    else:
        python_path = os.path.abspath('.venv/bin/python')
        activate_script = '.venv/bin/activate'
    
    # Check if the activation script exists
    if not os.path.exists(activate_script):
        print(f"Warning: Activation script {activate_script} not found.")
    else:
        print(f"Virtual environment created at .venv")
        print(f"Activate it with:")
        if platform.system() == 'Windows':
            print(f"    .venv\\Scripts\\activate")
        else:
            print(f"    source .venv/bin/activate")
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        # Upgrade pip first using the venv's Python to avoid the notice/error
        print("Upgrading pip...")
        subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Install project in development mode with dev dependencies
        print("Installing project dependencies...")
        subprocess.run([python_path, '-m', 'pip', 'install', '-e', '.[dev]'], check=True)
        print("Dependencies installed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        print("Try activating the environment manually and running:")
        print(f"    pip install -e .[dev]")
        return 1
    
    print("\nSetup complete! Your .venv environment is ready to use.")
    print(f"To activate: {'.\\.venv\\Scripts\\activate' if platform.system() == 'Windows' else 'source .venv/bin/activate'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
