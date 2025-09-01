# Configuration Guide

## Main Options

### 1. Comparison Precision
- **Precision level (1-100)**:
  - Lower values find more duplicates (less strict)
  - Higher values find only nearly identical duplicates (more strict)
  - Recommended: 70-80 for general use, 90+ for strict comparisons

### 2. Minimum Sizes
- **Ignore images below**:
  - Minimum width (pixels): `min_width`
  - Minimum height (pixels): `min_height`
  - Minimum file size (KB): `min_size`

### 3. Supported Formats
- **Image formats**:
  - `.jpg`, `.jpeg`
  - `.png`
  - `.gif`
  - `.bmp`
  - `.webp`
  - `.tiff`
  - `.psd` (Photoshop)
  - `.cr2`, `.nef`, `.arw` (RAW camera formats, requires proper ImageMagick configuration)

### 4. Excluded Folders
- **Default exclusions**:
  - System folders (e.g., `$RECYCLE.BIN`, `System Volume Information`)
  - Hidden folders (starting with `.` on Unix-like systems)
  - Temporary folders (e.g., `temp`, `tmp`)
- **Custom exclusions**:
  - Add specific folders to exclude from scanning
  - Supports wildcards (e.g., `*backup*`)

### 5. Processing Options
- **Performance settings**:
  - Number of threads: `threads` (default: number of CPU cores - 1)
  - Cache size (MB): `cache_size` (default: 1024 MB)
  - Image pre-loading: `preload_images` (true/false)
  - Results buffering: `buffer_results` (true/false)

### 6. Output Options
- **Report generation**:
  - PDF report: `report_pdf` (true/false)
  - CSV export: `export_csv` (true/false)
  - JSON export: `export_json` (true/false)
- **Logging**:
  - Log level: `log_level` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Log file location: `log_file` (path)
  - Maximum log size: `max_log_size` (MB)
  - Log rotation: `log_backup_count` (number of backup files)

### 7. User Interface
- **Language**:
  - English (`en`)
  - Italian (`it`)
- **Theme**:
  - Light
  - Dark
  - System (follows OS setting)
- **Display**:
  - Thumbnail size: `thumbnail_size` (small, medium, large)
  - Show file extensions: `show_extensions` (true/false)
  - Show hidden files: `show_hidden` (true/false)

### 8. Advanced Settings
- **Comparison algorithm**:
  - `ahash`: Average Hash (fastest, less accurate)
  - `phash`: Perceptual Hash (balanced)
  - `dhash`: Difference Hash (slower, more accurate)
  - `whash`: Wavelet Hash (best for resized images)
- **Optimizations**:
  - `fast_compare`: Skip exact match check (faster, less accurate)
  - `ignore_alpha`: Ignore transparency channel
  - `grayscale`: Convert to grayscale before comparison
  - `resize_width`: Width to resize images to before hashing (default: 16px)
  - `hash_size`: Size of the hash (default: 8)

## Configuration File

The application stores its configuration in `config/config.json`. You can edit this file directly or use the settings dialog in the application.

### Example Configuration

```json
{
  "comparison": {
    "precision": 75,
    "algorithm": "phash",
    "min_width": 100,
    "min_height": 100,
    "min_size": 50,
    "hash_size": 8,
    "resize_width": 16,
    "grayscale": true,
    "ignore_alpha": true
  },
  "performance": {
    "threads": 4,
    "cache_size": 1024,
    "preload_images": true,
    "buffer_results": true
  },
  "ui": {
    "language": "en",
    "theme": "system",
    "thumbnail_size": "medium",
    "show_extensions": true,
    "show_hidden": false
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log",
    "max_size": 10,
    "backup_count": 5
  },
  "paths": {
    "last_directory": "",
    "export_directory": "exports",
    "exclude_patterns": ["*backup*", "temp/*"]
  }
}
```

## Environment Variables

You can override configuration settings using environment variables:

- `IMAGES_DEDUP_THREADS`: Number of worker threads
- `IMAGES_DEDUP_CACHE_SIZE`: Cache size in MB
- `IMAGES_DEDUP_LOG_LEVEL`: Logging level
- `IMAGES_DEDUP_CONFIG`: Path to custom config file

## Best Practices

### Performance Tuning
- For large collections (>10,000 images):
  - Increase `cache_size` to 2048 MB or more
  - Use `preload_images` for SSDs
  - Set `threads` to number of CPU cores - 1

### Memory Management
- Monitor RAM usage during first scan
- Reduce `cache_size` if system becomes unresponsive
- Close other memory-intensive applications

### Storage Optimization
- Set appropriate `min_size` to skip thumbnails
- Use `exclude_patterns` to skip backup folders
- Consider file modification dates in comparison

### Troubleshooting
- If images aren't being detected:
  - Check file permissions
  - Verify image formats are supported
  - Check minimum size settings
- For slow performance:
  - Reduce number of threads
  - Disable image pre-loading
  - Increase cache size

## Command Line Overrides

Many settings can be overridden via command line arguments:

```bash
images-dedup /path/to/folder \
  --precision 80 \
  --threads 4 \
  --min-size 100 \
  --algorithm phash \
  --theme dark
```

For a complete list of command line options, run:

```bash
images-dedup --help
```

## Resetting Configuration

To restore default settings:

1. Close the application
2. Delete or rename the `config/config.json` file
3. Restart the application

A new configuration file with default values will be created automatically.
