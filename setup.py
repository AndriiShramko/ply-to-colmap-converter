#!/usr/bin/env python3
"""
Setup script for PLY to COLMAP Converter
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ply-to-colmap-converter",
    version="1.0.0",
    author="AI Assistant",
    author_email="",
    description="Convert PLY dense point clouds from CloudCompare to COLMAP format for Postshot 3D Gaussian Splatting",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ply-to-colmap-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ply-to-colmap=ply_to_colmap_converter:main",
        ],
    },
    keywords="ply colmap point-cloud 3d-gaussian-splatting postshot cloudcompare",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ply-to-colmap-converter/issues",
        "Source": "https://github.com/yourusername/ply-to-colmap-converter",
        "Documentation": "https://github.com/yourusername/ply-to-colmap-converter#readme",
    },
)
