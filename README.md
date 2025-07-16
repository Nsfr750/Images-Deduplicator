# Images Deduplicator

[![GitHub license](https://img.shields.io/github/license/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/issues)
[![GitHub stars](https://img.shields.io/github/stars/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-blue)](https://www.riverbankcomputing.com/software/pyqt/)

A powerful desktop application for finding and managing duplicate images in your folders using perceptual hashing technology. Now with a modern PyQt6 interface, available in multiple languages with automatic update checking.

## Latest Improvements (v1.5.1)

- **Crash Fixes**
  - Fixed application crashes when selecting images with invalid formats
  - Improved handling of temporary files during metadata operations
  - Added robust error handling for image preview loading
  - Fixed import issues with PyQt6's sip module

- **Enhanced Stability**
  - Added widget safety checks to prevent crashes
  - Improved memory management for image processing
  - Better error messages and user feedback
  - Detailed logging for troubleshooting

## Features

- **Modern UI** with dark theme and improved usability
- **Fast Duplicate Detection** using perceptual hashing
- **Multiple Language Support** with automatic detection
- **Smart Preview** with aspect ratio preservation
- **Undo Support** for all file operations
- **Metadata Preservation** when keeping the best quality image
- **Cross-Platform** - works on Windows, macOS, and Linux

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Click "Browse" to select a folder to scan for duplicates
2. Click "Compare" to start the duplicate detection process
3. Review the found duplicates in the list
4. Use the preview panel to compare images side by side
5. Select duplicates to delete or use the "Delete All Duplicates" button
6. Use "Undo" to restore any deleted files if needed

## Keyboard Shortcuts

- `Ctrl+O`: Open folder
- `Ctrl+Q`: Quit application
- `Ctrl+U`: Check for updates
- `F1`: Show help
- `F5`: Refresh view

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
