# Prerequisites

Before you can run or contribute to the Images-Deduplicator project, you'll need to set up your development environment with the following prerequisites:

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux with Python 3.8+
- **Python**: 3.8 or higher (recommended: 3.10+ for better performance)
- **RAM**: Minimum 4GB (8GB+ recommended for large image collections)
- **Disk Space**: At least 200MB free space (plus space for your image collection)
- **Display**: 1366x768 resolution or higher
- **ImageMagick**: Required for Wand image processing (see installation instructions below)

## Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Python Dependencies

The project uses the following key Python packages (automatically installed via requirements.txt):

### Core Dependencies
- **Wand** (>=0.6.11) - Image processing with ImageMagick
  - Replaces Pillow for better format support and performance
  - Requires ImageMagick to be installed on the system

- **ImageHash** (>=4.3.1) - Perceptual hashing for image comparison
  - Used for finding similar/duplicate images

- **PyQt6** (>=6.4.0) - Modern GUI framework
  - Provides the main application interface
  - Includes QtWebEngine for help documentation

- **Requests** (>=2.31.0) - HTTP client
  - Used for update checking and online features

### System Utilities
- **psutil** (>=5.9.0) - System information and process management
- **send2trash** (>=1.8.0) - Safe file operations with trash/recycle bin support
- **pywin32** (>=306) - Windows API integration (Windows only)
  - Required for Windows-specific features
  - Automatically skipped on non-Windows platforms

## ImageMagick Installation

Wand requires ImageMagick to be installed on your system. Follow these platform-specific instructions:

### Windows Installation

1. **Download the installer**:
   - Visit the [ImageMagick download page](https://imagemagick.org/script/download.php#windows)
   - Download the latest stable release (e.g., `ImageMagick-7.x.x-Q16-HDRI-x64-dll.exe`)

2. **Run the installer**:
   - Double-click the downloaded installer
   - **Important**: Check these options during installation:
     - ☑ Add application directory to your system path
     - ☑ Install development headers and libraries for C and C++
     - ☑ Install legacy utilities (e.g., convert, identify)
   - Complete the installation with default settings

3. **Verify installation**:
   Open a new Command Prompt and run:
   ```
   magick --version
   ```
   You should see version information if installed correctly.

### macOS Installation

#### Using Homebrew (recommended):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ImageMagick with required dependencies
brew install imagemagick
```

#### Verify installation:
```bash
magick --version
```

### Linux Installation

#### Debian/Ubuntu:
```bash
# Update package lists
sudo apt-get update

# Install ImageMagick and development files
sudo apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    libmagickcore-dev
```

#### Fedora/RHEL/CentOS:
```bash
sudo dnf install -y ImageMagick ImageMagick-devel
# or
sudo yum install -y ImageMagick ImageMagick-devel
```

### Verify Wand Installation

After installing ImageMagick, verify that Wand can communicate with it:

```python
import sys
import wand.version
from wand.image import Image

print(f"Python: {sys.version}")
print(f"Wand version: {wand.version.VERSION_STRING}")
print(f"ImageMagick version: {wand.version.MAGICK_VERSION}")
print(f"Features: {wand.version.MAGICK_FEATURES}")

# Test basic image operations
try:
    with Image(filename='wizard:' if not sys.platform.startswith('win') else 'rose:') as img:
        print(f"Test image: {img.format} {img.width}x{img.height}")
    print("✅ Wand is working correctly!")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Please ensure ImageMagick is properly installed and in your system PATH.")
```

## Development Dependencies (Optional)

For development and contributing to the project, install additional tools:

```bash
pip install -r requirements-dev.txt
```

### Included Tools:

- **Testing**
  - `pytest` - Testing framework
  - `pytest-qt` - GUI testing utilities
  - `pytest-cov` - Test coverage reporting

- **Code Quality**
  - `black` - Code formatter (enforced)
  - `mypy` - Static type checking
  - `flake8` - Linting
  - `isort` - Import sorting

- **Documentation**
  - `sphinx` - Documentation generator
  - `sphinx-rtd-theme` - ReadTheDocs theme
  - `myst-parser` - Markdown support for Sphinx

## Troubleshooting

### Common Issues

1. **Wand can't find ImageMagick**
   - Ensure ImageMagick is installed and in your system PATH
   - On Windows, restart your terminal/IDE after installation
   - Verify with `magick --version` in your terminal

2. **Permission issues on Linux/macOS**
   - You may need to add your user to the appropriate groups:
     ```bash
     # On Linux
     sudo usermod -a -G magick $USER
     # Log out and back in for changes to take effect
     ```

3. **Memory issues with large images**
   - Increase ImageMagick's resource limits in `policy.xml`
   - Location: `/etc/ImageMagick-7/policy.xml` (Linux/macOS) or `C:\Program Files\ImageMagick-7\policy.xml` (Windows)
   - Adjust these values as needed:
     ```xml
     <policy domain="resource" name="memory" value="4GiB"/>
     <policy domain="resource" name="width" value="32KP"/>
     <policy domain="resource" name="height" value="32KP"/>
     ```

4. **Unsupported image formats**
   - Install additional codecs if needed:
     - **Linux**: `sudo apt-get install libmagick++-dev`
     - **macOS**: `brew install libheif libraw`
     - **Windows**: Re-run the installer and select additional format support

## Building Documentation

To build the documentation locally:

1. Install documentation dependencies:
   ```bash
   pip install -r docs/requirements.txt
   ```

2. Build the documentation:
   ```bash
   cd docs
   make html
   ```

The documentation will be available in `docs/_build/html/index.html`

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   - Ensure all required system libraries are installed
   - On Linux, you might need to install additional packages:
     ```bash
     # For Debian/Ubuntu
     sudo apt-get install python3-dev python3-tk
     # For Fedora
     sudo dnf install python3-devel python3-tkinter
     ```

2. **Performance Issues**:
   - For large image collections, consider increasing Python's memory limits
   - Close other memory-intensive applications while running the deduplicator

3. **GUI Scaling Issues**:
   - On high-DPI displays, you might need to set the appropriate environment variable:
     ```bash
     export QT_SCALE_FACTOR=1.5  # Adjust the scale factor as needed
     ```

## Getting Help

If you encounter any issues setting up the development environment, please:
1. Check the [GitHub Issues](https://github.com/Nsfr750/Images-Deduplicator/issues) for similar problems
2. If your issue isn't reported, please open a new issue with detailed information about your problem
3. Join our [Discord server](https://discord.gg/BvvkUEP9) for community support
