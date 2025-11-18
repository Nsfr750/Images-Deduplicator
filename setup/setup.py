from setuptools import setup, find_packages
from pathlib import Path
import sys

# Import version from script/version.py
sys.path.insert(0, str(Path(__file__).parent / 'script'))
from version import __version__

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define core dependencies that are required for basic functionality
CORE_DEPS = [
    'Wand>=0.6.11',            # Image processing (requires ImageMagick)
    'ImageHash>=4.3.1',         # Perceptual hashing
    'PyQt6>=6.4.0',            # GUI framework
    'requests>=2.31.0',         # HTTP requests
    'qrcode>=7.4.2',           # QR code generation
    'psutil>=5.9.0',           # System information
    'send2trash>=1.8.0',       # Safe file operations
    'pywin32>=306; sys_platform == "win32"',  # Windows API integration
]

# Define optional dependencies for additional features
EXTRAS_DEPS = {
    'opencv': ['opencv-python-headless>=4.8.0'],  # Advanced image processing
    'numpy': ['numpy>=1.24.0'],                  # Numerical operations
    'scikit': ['scikit-image>=0.21.0'],           # Additional image processing
    'dev': [                                     # Development dependencies
        'pytest>=7.4.0',
        'pytest-qt>=4.2.0',
        'pytest-cov>=4.1.0',
        'black>=23.7.0',
        'mypy>=1.5.0',
        'flake8>=6.1.0',
        'isort>=5.12.0',
    ],
    'docs': [                                    # Documentation dependencies
        'Sphinx>=7.0.0',
        'sphinx-rtd-theme>=1.3.0',
        'sphinx-autodoc-typehints>=1.24.0',
        'myst-parser>=1.0.0',
    ],
    'packaging': [                              # Packaging dependencies
        'pyinstaller>=5.12.0',
        'setuptools>=68.0.0',
        'wheel>=0.41.0',
    ]
}

# Combine all optional dependencies under 'all' extra
EXTRAS_DEPS['all'] = [dep for deps in EXTRAS_DEPS.values() for dep in deps]

# Define package data to include
package_data = {
    '': ['*.txt', '*.md', '*.json', '*.ui', '*.qrc', '*.png', '*.ico'],
    'script': ['*.py', '*.png', '*.ico'],
}

# Create entry points for the application
entry_points = {
    'gui_scripts': [
        'images-dedup=main:main',
    ]
}

setup(
    name="images-deduplicator",
    version=__version__,
    author="Nsfr750",
    author_email="nsfr750@yandex.com",
    description="A powerful tool to find, compare, and manage duplicate images using perceptual hashing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750/Images-Deduplicator",
    project_urls={
        'Bug Reports': 'https://github.com/Nsfr750/Images-Deduplicator/issues',
        'Source': 'https://github.com/Nsfr750/Images-Deduplicator',
        'Documentation': 'https://nsfr750.github.io/Images-Deduplicator/',
        'Donate': 'https://paypal.me/3dmega',
    },
    packages=find_packages(include=['script*']),
    package_data=package_data,
    include_package_data=True,
    install_requires=CORE_DEPS,
    extras_require=EXTRAS_DEPS,
    entry_points=entry_points,
    python_requires='>=3.8',
    license='GPLv3',
    platforms=['Windows', 'macOS', 'Linux'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    keywords=[
        'image', 'duplicate', 'deduplication', 'cleanup', 'photos',
        'pictures', 'organize', 'manage', 'compare', 'Wand', 'ImageMagick'
    ],
    options={
        'build_exe': {
            'packages': ['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
            'include_files': ['assets/', 'LICENSE', 'README.md', 'PREREQUISITES.md'],
        }
    },
)
