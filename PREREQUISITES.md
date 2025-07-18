# Prerequisites

Before you can run or contribute to the Images-Deduplicator project, you'll need to set up your development environment with the following prerequisites:

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux with Python 3.8+
- **Python**: 3.8 or higher (recommended: 3.10+ for better performance)
- **RAM**: Minimum 4GB (8GB+ recommended for large image collections)
- **Disk Space**: At least 200MB free space (plus space for your image collection)
- **Display**: 1366x768 resolution or higher

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

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Python Dependencies

The project requires the following Python packages (automatically installed via requirements.txt):

- **Core Dependencies**:
  - Pillow>=10.0.0 (Image processing)
  - imagehash>=4.3.1 (Perceptual hashing)
  - PyQt6>=6.4.0 (GUI framework)
  - requests>=2.31.0 (HTTP requests)

- **System Utilities**:
  - psutil>=5.9.0 (System information)
  - send2trash>=1.8.0 (Safe file operations)

- **Windows Specific**:
  - pywin32>=306 (Windows API integration)

- **Packaging**:
  - pyinstaller>=5.12.0 (Creating standalone executables)

## Development Dependencies (Optional)

For contributing to the project, you might also need:

```bash
pip install -r requirements-dev.txt
```

This includes:
- pytest (Testing framework)
- pytest-qt (GUI testing)
- black (Code formatting)
- mypy (Static type checking)
- flake8 (Linting)

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
