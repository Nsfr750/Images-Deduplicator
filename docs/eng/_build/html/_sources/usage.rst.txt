Usage
=====

Main Interface
-------------

The application features a modern, user-friendly interface with the following key components:

1. **Menu Bar**: Access to all application functions and settings
2. **Toolbar**: Quick access to frequently used functions
3. **Folder Browser**: Navigate and select directories to scan
4. **Preview Pane**: View and compare images side by side
5. **Results Panel**: Displays found duplicates with similarity scores
6. **Status Bar**: Shows operation progress and system information

Basic Workflow
--------------

1. **Select Source Folder**
   - Click the "Open Folder" button or use ``File > Open Folder``
   - The application will scan for supported image formats
   - Supported formats: JPEG, PNG, WEBP, PSD, BMP, GIF, and more (via Wand/ImageMagick)

2. **Configure Scan Settings**
   - Adjust similarity threshold (default: 90%)
   - Set minimum image size to consider
   - Choose which image properties to compare (size, date, content hash)

3. **Start the Scan**
   - Click "Start Scan" to begin duplicate detection
   - Progress is shown in the status bar
   - Pause or stop the scan at any time

4. **Review Results**
   - Duplicate groups are displayed with previews
   - Sort by file size, date, or similarity score
   - Use the side-by-side comparison tool for verification

5. **Manage Duplicates**
   - Select images to keep or delete
   - Move duplicates to trash (recoverable) or delete permanently
   - Export results to CSV/JSON for reference

Advanced Features
----------------

**Batch Processing**
- Process multiple folders in sequence
- Save and load scan configurations
- Schedule automatic scans

**Smart Selection**
- Auto-select images by criteria (oldest, smallest, etc.)
- Keep highest resolution version
- Preserve images with specific naming patterns

**Image Comparison Tools**
- Side-by-side and overlay comparison modes
- Zoom and pan synchronized between images
- Histogram and EXIF data comparison

**Custom Filters**
- Filter by image dimensions
- Filter by creation/modification date
- Filter by image format or color profile

**Wand/ImageMagick Integration**
- Advanced image format support
- Better handling of color profiles and metadata
- Support for RAW camera formats when enabled in ImageMagick

Keyboard Shortcuts
-----------------

+----------------+-----------------------------------+
| Shortcut       | Action                            |
+================+===================================+
| ``Ctrl+O``     | Open folder                       |
+----------------+-----------------------------------+
| ``Ctrl+F``     | Start new scan                    |
+----------------+-----------------------------------+
| ``Space``      | Toggle selection of current image  |
+----------------+-----------------------------------+
| ``Del``        | Move selected to trash            |
+----------------+-----------------------------------+
| ``Ctrl+Z``     | Undo last action                  |
+----------------+-----------------------------------+
| ``F5``         | Refresh view                      |
+----------------+-----------------------------------+

Performance Optimization
-----------------------

1. **For Large Collections**
   - Use the "Quick Compare" mode for initial filtering
   - Increase the minimum file size to skip thumbnails
   - Schedule scans during off-hours for large collections

2. **Memory Management**
   - Close other memory-intensive applications
   - Adjust ImageMagick's resource limits if needed (see Installation)
   - Process images in smaller batches

3. **Storage Considerations**
   - Ensure sufficient free space for temporary files
   - Process images directly from the source drive when possible
   - Consider using a fast SSD for better performance

Troubleshooting
--------------

**Slow Performance**
- Check ImageMagick's policy settings (see Installation)
- Reduce the number of concurrent operations
- Disable real-time preview for large collections

**Missing Images**
- Verify ImageMagick supports the image format
- Check file permissions
- Look for error messages in the log viewer

**Unexpected Results**
- Adjust the similarity threshold
- Check if filters are too restrictive
- Verify image metadata is being read correctly

For additional help, refer to the :doc:`configuration` section or check the FAQ.
