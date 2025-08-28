"""
Setup script for ithome-bot package
"""
from setuptools import setup, find_packages
import os

# 讀取 README.md（如果存在）
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="ithome-bot",
    version="0.1.0",
    author="recca0120",
    author_email="recca0120@gmail.com",
    description="iThome 鐵人賽文章更新自動化工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/recca0120/ithome_bot",
    packages=["ithome_bot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "ithome-bot=ithome_bot.cli:main",
        ],
    },
)