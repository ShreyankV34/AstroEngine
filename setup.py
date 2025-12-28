"""Setup script for AstroCamSync."""
from setuptools import setup, find_packages

setup(
    name="astrocamsync",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pytz>=2023.3",
        "python-dateutil>=2.8.2",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "ruff>=0.0.287",
            "mypy>=1.5.0",
        ],
        "sensors": [
            "pyserial>=3.5",
            "bleak>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "astrocam=astrocam_sync.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
)