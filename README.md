# Images Deduplicator

[![GitHub license](https://img.shields.io/github/license/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/issues)
[![GitHub stars](https://img.shields.io/github/stars/Nsfr750/Images-Deduplicator)](https://github.com/Nsfr750/Images-Deduplicator/stargazers)

A powerful desktop application for finding and managing duplicate images in your folders using perceptual hashing technology.

## Features

- **Image Comparison**
  - Utilizes perceptual hashing for accurate duplicate detection
  - Supports PNG, JPG, JPEG, GIF, BMP, TIFF, and TIF formats
  - Handles truncated or corrupted images gracefully

- **User Interface**
  - Modern and intuitive graphical interface
  - Menu-driven navigation with About and Sponsor options
  - Clear visual feedback for operations

- **File Management**
  - Easy folder selection and browsing

## Requirements

- Python 3.8 or higher
- Required Python packages (automatically installed via requirements.txt):
  - Pillow (PIL)
  - imagehash
  - tkinter

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Select a folder containing images using the "Select Folder" option
2. Enable "Search subfolders" to scan nested directories
3. Adjust the quality threshold slider for duplicate matching
4. Click "Compare Images" to find duplicates
5. Review duplicates in the preview window
6. Select multiple duplicates using Ctrl or Shift
7. Click "Delete Selected" to remove duplicates
8. Use "Delete All Duplicates" to remove all found duplicates

## Quality Comparison

The app uses a quality threshold (0.8-1.0) to determine if images are duplicates:
- Lower values (0.8-0.9) find more similar images
- Higher values (0.95-1.0) find exact duplicates
- Adjust based on your needs using the quality threshold slider

## Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF/TIF

## Error Handling

The app includes comprehensive error handling and will display detailed error messages if something goes wrong during image processing.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

Found a bug or have a feature request? Please open an issue.

## Acknowledgments

- Thanks to all contributors and users
- Special thanks to the open-source community

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

For detailed changes in each version, see the [CHANGELOG.md](CHANGELOG.md) file.

## Social Links

- 🎯 [Patreon](https://www.patreon.com/Nsfr750)
- 🐙 [GitHub](https://github.com/Nsfr750)
- 🗣️ [Discord](https://discord.gg/q5Pcgrju)
- 💰 [PayPal](https://paypal.me/3dmega)
