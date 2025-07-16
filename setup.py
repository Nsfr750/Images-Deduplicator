from setuptools import setup, find_packages
import os
import sys
from script.version import __version__

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Define package data to include
package_data = {
    '': ['*.txt', '*.md', '*.json'],
    'script': ['*.py'],
}

# Create entry points for the application
entry_points = {
    'console_scripts': [
        'images-dedup=main:main',
    ],
    'gui_scripts': [
        'images-dedup-gui=main:main',
    ]
}

setup(
    name="images-deduplicator",
    version=__version__,
    author="Nsfr750",
    author_email="nsfr750@yandex.com",
    description="A tool to find and remove duplicate images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750/Images-Deduplicator",
    packages=find_packages(include=['script*']),
    package_data=package_data,
    include_package_data=True,
    install_requires=requirements,
    entry_points=entry_points,
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    keywords='image duplicate deduplication cleanup',
    project_urls={
        'Bug Reports': 'https://github.com/Nsfr750/Images-Deduplicator/issues',
        'Source': 'https://github.com/Nsfr750/Images-Deduplicator',
        'Documentation': 'https://github.com/Nsfr750/Images-Deduplicator#readme',
    },
)
