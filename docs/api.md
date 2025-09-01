# API Reference

This section provides detailed documentation for the Images Deduplicator API. The application is built with a modular architecture, with each module handling specific functionality.

## Core Modules

### Main Application

```python
# script/main.py
```

Main application entry point and core functionality.

**Key Components:**
- Application initialization and configuration
- Main event loop
- Core application logic

## Image Processing

```python
# script/image_processor.py
```

Handles all image processing operations using Wand/ImageMagick.

### Key Features
- Supports all major image formats (JPEG, PNG, WEBP, PSD, etc.)
- Perceptual hashing for duplicate detection
- Memory-efficient processing of large images
- EXIF and metadata handling

### Main Classes

#### `ImageProcessor`
```python
class ImageProcessor:
    def __init__(self, config=None):
        """Initialize with optional configuration."""
        
    def load_image(self, filepath):
        """Load an image from file."""
        
    def calculate_hash(self, image, method='phash'):
        """Calculate perceptual hash of an image."""
        
    def compare_images(self, image1, image2, method='phash', threshold=0.9):
        """Compare two images and return similarity score."""
        
    def get_metadata(self, image):
        """Extract metadata from image."""
```

## User Interface

### Main Window
```python
# script/UI.py
```

Main window and UI components built with PyQt6.

**Key Components:**
- Main application window
- Image grid view
- Preview panel
- Status bar

### Menu System
```python
# script/menu.py
```

Application menu and toolbar functionality.

### Image Preview Dialog
```python
# script/image_dialog_preview.py
```

Image preview and comparison dialog.

## Core Functionality

### Background Workers
```python
# script/workers.py
```

Background workers for non-blocking UI operations.

**Key Classes:**
- `ScanWorker`: Handles directory scanning
- `CompareWorker`: Handles image comparison
- `DeleteWorker`: Handles file deletion

### Undo Manager
```python
# script/undo_manager.py
```

Manages undo/redo operations for file operations.

**Key Methods:**
- `add_operation()`: Add an operation to the undo stack
- `undo()`: Undo the last operation
- `redo()`: Redo the last undone operation
- `clear()`: Clear the undo/redo stacks

## Internationalization

### Translations
```python
# script/translations.py
```

Contains all translatable strings.

### Language Manager
```python
# script/language_manager.py
```

Handles language switching and string translations.

**Key Methods:**
- `load_language(lang_code)`: Load a language
- `translate(key)`: Get translated string
- `get_available_languages()`: List available languages

## Utilities

### Logging
```python
# script/logger.py
```

Centralized logging functionality.

**Features:**
- Configurable log levels
- File and console output
- Log rotation

### Configuration
```python
# script/config.py
```

Manages application configuration.

**Key Methods:**
- `load()`: Load configuration from file
- `save()`: Save configuration to file
- `get(key, default)`: Get configuration value
- `set(key, value)`: Set configuration value

## Example Usage

### Basic Image Comparison

```python
from script.image_processor import ImageProcessor

# Initialize processor
processor = ImageProcessor()

# Load images
img1 = processor.load_image('image1.jpg')
img2 = processor.load_image('image2.jpg')

# Compare images
similarity = processor.compare_images(img1, img2, method='phash', threshold=0.9)
print(f"Images are {similarity*100:.2f}% similar")
```

### Using the Undo Manager

```python
from script.undo_manager import UndoManager

# Initialize undo manager
undo_manager = UndoManager()

# Add an operation
def delete_file(filepath):
    # Implementation to delete file
    pass
    
def restore_file(filepath):
    # Implementation to restore file
    pass

# Record operation
undo_manager.add_operation(
    action=delete_file,
    undo_action=restore_file,
    args=('path/to/file.jpg',)
)

# Later, undo the operation
undo_manager.undo()
```

## Extending the Application

### Adding a New Comparison Method

1. Create a new method in `ImageProcessor`:

```python
def my_comparison_method(self, image1, image2, **kwargs):
    # Your comparison logic here
    return similarity_score
```

2. Update the configuration to include your new method:

```python
# In config.py
DEFAULT_CONFIG = {
    'comparison': {
        'methods': {
            'my_method': {
                'name': 'My Comparison Method',
                'description': 'My custom comparison method',
                'default_threshold': 0.85
            }
        }
    }
}
```

3. The new method will be available in the UI and API.

## Error Handling

All API methods raise appropriate exceptions:

- `ImageLoadError`: Failed to load an image
- `ComparisonError`: Error during image comparison
- `FileOperationError`: Error during file operations
- `ConfigurationError`: Invalid configuration

## Testing

Run tests with:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

GPLv3 - See [LICENSE](LICENSE) for details.
