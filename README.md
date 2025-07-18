# Images Deduplicator

[![GitHub license](https://img.shields.io/github/license/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/issues)
[![GitHub stars](https://img.shields.io/github/stars/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-blue)](https://www.riverbankcomputing.com/software/pyqt/)
[![Wand](https://img.shields.io/badge/Wand-0.6.11%2B-blue)](https://docs.wand-py.org/)
[![ImageMagick](https://img.shields.io/badge/ImageMagick-7.0.0+-blue)](https://imagemagick.org/)

A powerful desktop application for finding and managing duplicate images in your folders using perceptual hashing technology. Built with PyQt6 and Wand (ImageMagick) for robust image processing across multiple formats.

## Latest Improvements (v1.6.0)

### 🚀 New Features
- **Complete Migration to Wand**
  - Replaced Pillow with Wand (ImageMagick) for enhanced image processing
  - Added native support for additional formats: PSD, GIF, BMP, and more
  - Improved metadata extraction and preservation
  - Better handling of large and complex image files

### 🛠️ Stability & Performance
- **Thread Safety**
  - Fixed QThread destruction warnings
  - Improved update checker reliability
  - Better resource cleanup on application exit
  - Optimized memory management for large image collections

### 📚 Documentation
- **Comprehensive Guides**
  - Complete API documentation
  - Step-by-step installation for all platforms
  - Troubleshooting common issues
  - Migration guide from Pillow to Wand

### 🌍 Localization
- **Improved Language Support**
  - Fixed syntax errors in translations
  - Better handling of special characters
  - More consistent UI text across languages

## Features

- **Modern UI** with dark theme and improved usability
- **Fast Duplicate Detection** using perceptual hashing
- **Multiple Language Support** with automatic detection
- **Smart Preview** with aspect ratio preservation
- **Undo Support** for all file operations
- **Metadata Preservation** when keeping the best quality image
- **Wide Format Support** - works with JPG, PNG, GIF, BMP, TIFF, PSD, and WebP
- **Cross-Platform** - works on Windows, macOS, and Linux

## System Requirements

- Python 3.8 or higher
- ImageMagick 7.0.0 or higher
- Windows, macOS, or Linux

## Installation

### 1. Install System Dependencies

#### Windows
1. Download and install ImageMagick from [https://imagemagick.org/script/download.php#windows](https://imagemagick.org/script/download.php#windows)
2. During installation, make sure to check "Add application directory to your system path"

#### macOS
```bash
brew install imagemagick
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y libmagickwand-dev
```

### 2. Install Python Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Launch the application:
   ```bash
   python main.py
   ```

2. Click "Browse" to select a folder to scan for duplicates
3. Click "Compare" to start the duplicate detection process
4. Review the found duplicates in the list
5. Use the preview panel to compare images side by side
6. Select duplicates to delete or use the "Delete All Duplicates" button
7. Use "Undo" to restore any deleted files if needed

## Troubleshooting

### Wand/ImageMagick Issues
- If you get `Wand` import errors, ensure ImageMagick is properly installed and in your system PATH
- On Windows, you may need to restart your terminal/IDE after installing ImageMagick
- For Linux, you might need to install additional development packages:
  ```bash
  sudo apt-get install -y libmagickwand-dev
  ```

### Performance Tips
- For large image collections, increase the chunk size in the settings
- Use the "Preserve Metadata" option only when necessary as it can slow down processing
- Close other memory-intensive applications when working with large numbers of images

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Support

If you find this project useful, consider supporting its development:
- [GitHub Sponsors](https://github.com/sponsors/Nsfr750)
- [Patreon](https://www.patreon.com/Nsfr750)
- [PayPal](https://paypal.me/3dmega)

## Author

Nsfr750 - [GitHub](https://github.com/Nsfr750) | [Discord](https://discord.gg/BvvkUEP9)
