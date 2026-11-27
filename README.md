# Images Deduplicator

[![GitHub license][b-license]][gh-license]
[![GitHub issues][b-issues]][gh-issues]
[![GitHub stars][b-stars]][gh-stars]
[![Python Version][b-python]][python]
[![PyQt6][b-pyqt]][pyqt]
[![Wand][b-wand]][wand-docs]
[![ImageMagick][b-im]][im]

[b-license]: https://img.shields.io/github/license/Nsfr750/Images-Deduplicator
[b-issues]: https://img.shields.io/github/issues/Nsfr750/Images-Deduplicator
[b-stars]: https://img.shields.io/github/stars/Nsfr750/Images-Deduplicator
[b-python]: https://img.shields.io/badge/python-3.8%2B-blue
[b-pyqt]: https://img.shields.io/badge/PyQt6-6.4.0+-blue
[b-wand]: https://img.shields.io/badge/Wand-0.6.11%2B-blue
[b-im]: https://img.shields.io/badge/ImageMagick-7.0.0+-blue
[gh-license]: https://github.com/Nsfr750/Images-Deduplicator/blob/master/LICENSE
[gh-issues]: https://github.com/Nsfr750/Images-Deduplicator/issues
[gh-stars]: https://github.com/Nsfr750/Images-Deduplicator/stargazers
[python]: https://www.python.org/
[pyqt]: https://www.riverbankcomputing.com/software/pyqt/
[wand-docs]: https://docs.wand-py.org/
[im]: https://imagemagick.org/

A powerful desktop application for finding and managing duplicate images
in your folders using perceptual hashing technology. Built with PyQt6 and
Wand (ImageMagick) for robust image processing across multiple formats.

## Latest Improvements (v1.8.0)

### 🚀 New Features

- **File Size Comparison**
  - Optional, additional duplicate detection method with a UI toggle
  - Size-based pre-filtering skips most hashing work on large collections

- **Batch Processing**
  - Image collections processed in sequential batches for lower memory usage

- **Progress Saving & Resuming**
  - Long scans checkpoint progress and resume automatically after interruption

- **Performance Metrics**
  - Per-run metrics: file counts, cache hits/misses, timings and throughput

- **Improved Error Handling**
  - Clear messages for offline network drives, permissions and missing folders

- **Tests & Documentation**
  - Comprehensive Wand image processing test suite (49 tests)
  - New `docs/WAND.md` covering Wand features and limitations

### 🐛 Bug Fixes

- **Metadata Extraction**
  - Fixed EXIF entries never being collected during scans
- **UI Stability**
  - Fixed a crash on starting comparison (undefined status label)

## Features

- **Modern UI** with dark theme and improved usability
- **Fast Duplicate Detection** using perceptual hashing
- **File Size Comparison** as an optional, additional detection method
- **Batch Processing** for large image collections
- **Progress Saving & Resuming** for long-running scans
- **Performance Metrics** for every comparison run
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

1. Download and install ImageMagick from the [download page][im-dl]
2. During installation, check "Add application directory to your system path"

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

- If you get `Wand` import errors, ensure ImageMagick is in your PATH
- On Windows, you may need to restart your terminal/IDE after installing
  ImageMagick
- For Linux, you might need additional development packages:

  ```bash
  sudo apt-get install -y libmagickwand-dev
  ```

### Performance Tips

- For large image collections, increase the chunk size in the settings
- Enable "Preserve Metadata" only when needed — it slows down processing
- Close memory-intensive applications when processing many images

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under GPLv3 - see the [LICENSE](LICENSE) file for details.

## Support

If you find this project useful, consider supporting its development:

- [GitHub Sponsors](https://github.com/sponsors/Nsfr750)
- [Patreon](https://www.patreon.com/Nsfr750)
- [PayPal](https://paypal.me/3dmega)

## Author

Nsfr750 - [GitHub](https://github.com/Nsfr750)

[im-dl]: https://imagemagick.org/script/download.php#windows
