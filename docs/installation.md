# Installation

## Prerequisites

Before installing Images Deduplicator, ensure you have:

1. Python 3.8 or higher (3.10+ recommended)
2. ImageMagick installed (required for Wand)
3. Git (optional, for development installation)

## Installing ImageMagick

### Windows

1. Download the latest ImageMagick installer from the [official website](https://imagemagick.org/script/download.php#windows)
2. Run the installer with these options:
   - Check "Install development headers and libraries for C and C++"
   - Check "Add application directory to your system path"
3. Verify installation by opening a new command prompt and running:
   ```bash
   magick --version
   ```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
# Install ImageMagick
brew install imagemagick
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    libmagickcore-dev
```

## Installation via pip

The recommended way to install Images Deduplicator is using pip:

```bash
# Install the package
pip install images-deduplicator
   
# Run the application
images-dedup
```

## Installation from Source

1. Clone the repository:

```bash
git clone https://github.com/Nsfr750/Images-Deduplicator.git
cd Images-Deduplicator
```

2. Install in development mode with all dependencies:

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
   
# Install package in development mode with all extras
pip install -e '.[dev,docs,packaging]'
```

3. Run the application:

```bash
python main.py
```

## Verifying the Installation

To verify that Wand can find and use ImageMagick:

```python
from wand.image import Image
from wand.version import QUANTUM_DEPTH, MAGICK_VERSION

print(f"ImageMagick version: {MAGICK_VERSION}")
print(f"Quantum depth: {QUANTUM_DEPTH} bits")

# Test basic image operations
with Image(width=200, height=100, background='red') as img:
    print(f"Created image: {img.size}")
```

## Troubleshooting

### Common Issues

1. **Wand can't find ImageMagick**
   - Ensure ImageMagick is installed and in your system PATH
   - On Windows, you may need to restart your terminal or computer after installation

2. **Permission errors**
   - On Linux/macOS, ensure you have the necessary permissions to install system packages
   - Consider using `--user` flag with pip if you don't have admin rights

3. **Missing dependencies**
   - On Linux, ensure you have development tools installed:
     ```bash
     sudo apt-get install build-essential python3-dev
     ```

4. **Virtual environment issues**
   - If you encounter issues with the virtual environment, try recreating it:
     ```bash
     rm -rf venv
     python -m venv venv
     source venv/bin/activate  # or venv\Scripts\activate on Windows
     pip install -e '.[dev,docs,packaging]'
     ```
