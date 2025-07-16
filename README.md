# Images Deduplicator

[![GitHub license](https://img.shields.io/github/license/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/issues)
[![GitHub stars](https://img.shields.io/github/stars/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-blue)](https://www.riverbankcomputing.com/software/pyqt/)

A powerful desktop application for finding and managing duplicate images in your folders using perceptual hashing technology. Now with a modern PyQt6 interface, available in multiple languages with automatic update checking.

## New in PyQt6 Version (v1.5.0)

- **Modern UI** with improved look and feel using Qt6
- **Enhanced Performance** with better threading using QThreadPool
- **Dark Theme** for better visibility and reduced eye strain
- **New Features**:
  - Tabbed Help system with rich text formatting
  - Improved image preview with aspect ratio preservation
  - Better error handling and user feedback
  - Status bar with operation feedback
  - More responsive interface with proper threading
  - Built-in log viewer with filtering capabilities
  - Automatic update checking
  - Multi-language support (English, Italian)

## Features

- **Image Comparison**
  - Utilizes perceptual hashing for accurate duplicate detection
  - Supports PNG, JPG, JPEG, GIF, BMP, TIFF, TIF, WEBP, SVG, PSD formats
  - Handles truncated or corrupted images gracefully
  - Configurable similarity threshold

- **User Interface**
  - Modern PyQt6-based interface with dark theme
  - Multi-language support with dynamic language switching
  - Menu-driven navigation with Help, About, and Sponsor options
  - Status bar with operation feedback
  - Tabbed Help system with rich content and search functionality
  - Image preview functionality with side-by-side comparison
  - Built-in log viewer with filtering options
  - Consistent dark theme across all components for better visibility

- **Help System**
  - Comprehensive tabbed interface with Usage, Features, and Tips sections
  - Real-time search with highlighting
  - Language support for all help content
  - Dark theme integration with proper text contrast
  - Organized content with easy navigation

- **File Management**
  - Easy folder selection and browsing
  - Recursive subfolder search
  - Batch delete functionality
  - Safe file operations with confirmation dialogs
  - Logging of all file operations

- **Updates & Localization**
  - Automatic update checking on startup
  - Manual update check option
  - Multi-language support with language switching
  - User-selectable language preferences
  - Localized UI elements and messages

## Requirements

- Python 3.8 or higher
- PyQt6 6.4.0 or higher
- Pillow (PIL Fork) 9.0.0 or higher
- imagehash 4.3.0 or higher

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

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Select a folder containing images using the "Browse" button
3. Click "Compare Images" to start the duplicate detection
4. Review the list of duplicate images
5. Use the preview panel to compare images side by side
6. Select duplicates to delete and click "Delete Selected"

## Project Structure

- `main.py` - Main application entry point
- `script/` - Python package containing all application modules
  - `__init__.py` - Package initialization
  - `about.py` - About dialog implementation
  - `help.py` - Help dialog with tabbed interface
  - `log_viewer.py` - Log viewer dialog with filtering
  - `sponsor.py` - Sponsor information dialog
  - `styles.py` - Application theming and styling
  - `translations.py` - Internationalization support
  - `updates.py` - Update checking functionality
  - `version.py` - Version information
- `assets/` - Application resources (icons, images)
- `docs/` - Documentation files
- `logs/` - Application logs (automatically created)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPLv2 License - see the [LICENSE](LICENSE) file for details.

## Support

If you find this project useful, please consider supporting it:
- [GitHub Sponsors](https://github.com/sponsors/Nsfr750)
- [Buy Me a Coffee](https://paypal.me/3dmega)
- [Patreon](https://www.patreon.com/Nsfr750)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

## Roadmap

See [TO_DO.md](TO_DO.md) for planned features and improvements.
