# Usage Guide

## Main Interface

The application features a modern, user-friendly interface with the following key components:

1. **Menu Bar**: Access to all application functions and settings
2. **Toolbar**: Quick access to frequently used functions
3. **Folder Browser**: Navigate and select directories to scan
4. **Preview Pane**: View and compare images side by side
5. **Results Panel**: Displays found duplicates with similarity scores
6. **Status Bar**: Shows operation progress and system information

## Basic Workflow

### 1. Select Source Folder
- Click the "Open Folder" button or use `File > Open Folder`
- The application will scan for supported image formats
- Supported formats: JPEG, PNG, WEBP, PSD, BMP, GIF, and more (via Wand/ImageMagick)

### 2. Configure Scan Settings
- Adjust similarity threshold (default: 90%)
- Set minimum image size to consider
- Choose which image properties to compare (size, date, content hash)

### 3. Start the Scan
- Click "Start Scan" to begin duplicate detection
- Progress is shown in the status bar
- Pause or stop the scan at any time

### 4. Review Results
- Duplicate groups are displayed with previews
- Sort by file size, date, or similarity score
- Use the side-by-side comparison tool for verification

### 5. Manage Duplicates
- Select images to keep or delete
- Move duplicates to trash (recoverable) or delete permanently
- Export results to CSV/JSON for reference

## Advanced Features

### Batch Processing
- Process multiple folders in sequence
- Save and load scan configurations
- Schedule automatic scans

### Smart Selection
- Auto-select images by criteria (oldest, smallest, etc.)
- Keep highest resolution version
- Preserve images with specific naming patterns

### Image Comparison Tools
- Side-by-side and overlay comparison modes
- Zoom and pan synchronized between images
- Histogram and EXIF data comparison

### Custom Filters
- Filter by image dimensions
- Filter by creation/modification date
- Filter by image format or color profile

### Wand/ImageMagick Integration
- Advanced image format support
- Better handling of color profiles and metadata
- Support for RAW camera formats when enabled in ImageMagick

## Keyboard Shortcuts

| Shortcut    | Action                           |
|-------------|----------------------------------|
| `Ctrl+O`    | Open folder                      |
| `Ctrl+F`    | Start new scan                   |
| `Space`     | Toggle selection of current image |
| `Del`       | Move selected to trash           |
| `Ctrl+Z`    | Undo last action                 |
| `F5`        | Refresh view                     |

## Performance Optimization

### For Large Collections
- Use the "Quick Compare" mode for initial filtering
- Increase the minimum file size to skip thumbnails
- Schedule scans during off-hours for large collections

### Memory Management
- Close other memory-intensive applications
- Adjust the cache size in settings
- Use the 64-bit version for large image collections

### Storage Optimization
- Empty trash regularly
- Consider using a fast SSD for better performance
- Enable file compression for archived images

## Troubleshooting

### Common Issues

1. **Slow Performance**
   - Reduce the number of simultaneous comparisons
   - Increase the similarity threshold
   - Exclude system folders and application caches

2. **Missing Images**
   - Check file permissions
   - Verify the image format is supported
   - Ensure files aren't in use by other applications

3. **Unexpected Matches**
   - Adjust the similarity threshold
   - Check the comparison method in settings
   - Verify image metadata isn't affecting the comparison

## Best Practices

1. **Before Starting**
   - Backup important images
   - Close other applications to free up system resources
   - Ensure sufficient disk space is available

2. **During Scanning**
   - Start with a small test folder
   - Review the first few matches carefully
   - Use the preview function before making bulk changes

3. **After Completion**
   - Review the summary report
   - Check the trash before emptying it
   - Consider keeping a log of removed files

## Command Line Interface (CLI)

For advanced users, the application can be controlled via command line:

```bash
# Basic usage
images-dedup /path/to/folder

# With options
images-dedup /path/to/folder --threshold 95 --min-size 100KB --output results.csv

# For help
images-dedup --help
```

## Automation

### Scripting Example

```python
from images_deduplicator import Deduplicator

# Initialize with custom settings
dedup = Deduplicator(
    min_similarity=0.9,
    min_size='50KB',
    recursive=True
)

# Scan a folder
results = dedup.scan('/path/to/images')

# Process results
for group in results.duplicates:
    print(f"Found {len(group)} duplicates:")
    for img in group:
        print(f"  - {img.path} ({img.size})")
    
    # Keep the largest file, delete others
    if group:
        keep = max(group, key=lambda x: x.size)
        print(f"Keeping: {keep.path}")
        for img in group:
            if img != keep:
                img.delete()
```

## Support

For additional help, please refer to the [GitHub Issues](https://github.com/Nsfr750/Images-Deduplicator/issues) page or open a new issue.
