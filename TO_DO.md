# TO DO List

## Version 1.7.0 (2025-11-18)
- [x] Fixed PyQt6 signal handling in workers.py
- [x] Updated WorkerSignals to use pyqtSignal consistently
- [x] Improved thread safety in signal handling
- [x] Updated project documentation
- [x] Bumped version to 1.7.0

## High Priority
- [ ] Add file size comparison as an additional duplicate detection method
- [ ] Implement batch processing for large image collections
- [ ] Add progress saving and resuming for long operations
- [ ] Improve error handling for network drives and special folders
- [x] Add support for image metadata comparison (Basic support added with Wand)
- [x] Implement automated tests for the update checker
- [ ] Add performance metrics for image comparison
- [ ] Add comprehensive tests for Wand image processing
- [ ] Document Wand-specific features and limitations

## User Interface
- [x] Complete PyQt6 migration with modern UI components
- [x] Implement dark mode theme support
- [x] Add drag and drop support for folder selection
- [x] Add keyboard shortcuts for common actions
- [x] Add visual feedback for long-running operations
- [x] Add language selection menu
- [x] Enhance About dialog with version information
- [x] Improve status bar with better feedback
- [x] Add log viewer with filtering capabilities
- [x] Enhance Help Dialog
  - [x] Add search functionality
  - [x] Implement dark theme
  - [x] Add language support
  - [x] Fix layout issues
  - [x] Improve content organization
- [ ] Add Wand/ImageMagick version info in About dialog

## Features
- [ ] Add image organization by similarity groups
- [ ] Implement image quality comparison
- [x] Add support for more image formats (PSD, GIF, BMP via Wand)
- [x] Improve error handling and user feedback
- [x] Add logging system with log viewer
- [x] Implement undo/redo functionality for file operations
- [x] Migrate from Pillow to Wand for image processing
- [x] Create installers for windows platforms

## Performance
- [x] Optimize PyQt6 UI responsiveness
- [ ] Optimize image comparison algorithm
- [x] Implement caching for faster duplicate detection
- [x] Implement background processing for large folders
- [x] Add image metadata preservation options (Basic support with Wand)
- [x] Optimize memory usage for large image sets
- [ ] Optimize memory usage for large image collections
- [ ] Add caching for faster subsequent scans
- [ ] Implement parallel processing for image comparison
- [ ] Optimize Wand image loading and processing

## Documentation
- [x] Update installation instructions for Wand/ImageMagick
- [ ] Add Wand-specific examples to documentation
- [ ] Document migration guide from Pillow to Wand
- [ ] Update API documentation for new Wand-based functions
- [x] Improve handling of large image files
- [ ] Add support for GPU acceleration
- [ ] Optimize database queries for large datasets
- [ ] Implement background processing for better responsiveness

## Quality of Life
- [x] Add image preview with zoom functionality
- [x] Add option to save duplicate reports
- [x] Implement undo functionality for file operations
- [x] Add confirmation dialogs for destructive actions

## Documentation
- [x] Update README with PyQt6 information
- [x] Update CHANGELOG with recent changes
- [x] Update README with new features
- [x] Update CHANGELOG with latest changes
- [x] Add comprehensive API documentation
- [x] Improve installation and setup instructions
- [x] Add troubleshooting section
- [ ] Document the image comparison algorithm
- [ ] Add user guide
- [ ] Add developer documentation

## Testing
- [x] Add unit tests for core functionality
- [x] Add integration tests for the GUI
- [ ] Add performance benchmarks
- [ ] Add test coverage reporting
- [ ] Implement automated UI testing

## Future Enhancements
- [ ] Add machine learning for better duplicate detection
- [ ] Implement machine learning for better duplicate detection
- [ ] Add support for more image formats

## Bug Fixes & Improvements
- [x] Fix application crash when closing application with active threads
- [x] Resolved threading issues in update checker
- [x] Improved error handling and logging
- [x] Simplified theme selection to light/dark only
- [x] Reorganized project structure with Python package layout
- [x] Fixed infinite recursion in theme/style application
- [x] Improved language menu and translations
- [x] Fix application crash when selecting invalid images
- [x] Improve handling of temporary files
- [x] Add widget safety checks
- [x] Fix PyQt6 sip module import issue
- [ ] Improve error messages for better user feedback
- [ ] Add more detailed logging for troubleshooting

## Completed in v1.5.1
- [x] Fixed application crashes during image selection
- [x] Improved memory management for image processing
- [x] Added widget safety checks
- [x] Enhanced error handling and logging
- [x] Fixed PyQt6 sip module import issue

## Completed in v1.5.0
- [x] Fixed crash when closing application with active threads
- [x] Resolved threading issues in update checker
- [x] Improved error handling and logging
- [x] Simplified theme selection to light/dark only
- [x] Reorganized project structure with Python package layout
- [x] Fixed infinite recursion in theme/style application
- [x] Improved language menu and translations
- [x] Added comprehensive logging system
- [x] Implemented dark theme
- [x] Added multi-language support
- [x] Improved error handling
- [x] Enhanced help system with search

## Completed in v1.4.5
- [x] Migrated from Tkinter to PyQt6
- [x] Added dark theme support
- [x] Improved image preview functionality
- [x] Added status bar with operation feedback
- [x] Implemented automatic update checking
- [x] Added multi-language support
- [x] Improved error handling and user feedback
