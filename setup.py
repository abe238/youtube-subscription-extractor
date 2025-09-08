#!/usr/bin/env python3
"""
Setup script for YouTube Subscription Extractor
"""

from setuptools import setup, find_packages
import sys
import os

# Add the bin directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bin'))

try:
    from extract import __version__, __author__
except ImportError:
    __version__ = "1.0.0"
    __author__ = "abe238"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-subscription-extractor",
    version=__version__,
    author=__author__,
    author_email="",
    description="Extract comprehensive channel information from YouTube subscription MHTML files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abe238/youtube-subscription-extractor",
    project_urls={
        "Bug Reports": "https://github.com/abe238/youtube-subscription-extractor/issues",
        "Source": "https://github.com/abe238/youtube-subscription-extractor",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    entry_points={
        "console_scripts": [
            "youtube-subscription-extractor=bin.extract:main",
        ],
    },
    scripts=[
        "bin/extract.py",
    ],
    include_package_data=True,
    zip_safe=False,
)