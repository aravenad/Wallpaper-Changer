from setuptools import setup, find_packages

setup(
    name="wallpaper_changer",
    version="0.1.0",
    description="Automatically change your desktop wallpaper using Unsplash images",
    author="Damien",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "keyboard>=0.13.5",
        "pywin32>=300",
        "pillow",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov",
            "black",
            "pylint",
        ],
    },
)
