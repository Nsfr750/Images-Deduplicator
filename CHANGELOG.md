# Changelog

## Version 1.5.0 (2025-07-10)
### Added
- Added comprehensive logging system with log viewer
- Implemented log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Added dark theme as default for better user experience
- Improved error handling and user feedback
- Added more detailed status messages
- Enhanced logging of file operations

### Changed
- Reorganized project structure with Python package layout
- Moved all Python modules to `script` package
- Updated all imports to use package-relative imports
- Removed Windows 11 and Vista styles, keeping only Fusion style
- Simplified theme selection to light/dark only
- Improved thread safety in update checking

### Fixed
- Fixed crash when closing application with active threads
- Fixed infinite recursion in theme/style application
- Fixed language menu display issues
- Improved handling of missing menu items during language changes
- Fixed log viewer filter functionality
- Resolved threading issues in update checker
- Fixed status bar update issues
- Improved error handling for file operations

## Version 1.4.5 (2025-07-09)
### Added
- Migrated from Tkinter to PyQt6 for a more modern and responsive UI
- New modern dialogs with improved user experience
- Enhanced status bar with better messaging
- Improved error handling and user feedback
- Better cross-platform compatibility
- Added support for high DPI displays
- Improved dark mode support

### Changed
- Completely redesigned UI using Qt widgets
- Updated all dialogs to use PyQt6 (About, Help, Sponsor, Update)
- Improved threading model for better performance
- Enhanced image preview with better scaling and aspect ratio handling
- Modernized application styling and theming
- Improved window management and resizing behavior

### Fixed
- Fixed issues with language switching in the new Qt interface
- Resolved threading issues during image comparison
- Fixed status bar visibility and functionality
- Improved error handling during file operations
- Fixed various UI layout issues

## Version 1.4.0 (2025-06-23)
### Added
- Multi-language support (English, Spanish, French, German, Portuguese, Italian)
- Automatic update checking on startup
- Language selection menu
- Enhanced About dialog with version information
- New translation system with support for dynamic language switching
- Added support for more image formats
- Improved error handling and user feedback

### Fixed
- Fixed file deletion error handling
- Improved UI responsiveness during long operations
- Fixed layout issues in various dialogs
- Resolved issues with image preview functionality
- Fixed translation strings and improved localization coverage

## Version 1.3.0 (2025-05-22)
### Added
- "Select All" button for duplicates
- Improved UI organization with better button placement
- Better scrollbar positioning in results list
- Removed quality threshold functionality for simpler UI

### Fixed
- Removed redundant "Delete All Duplicates" button
- Improved spacing and layout consistency
- Fixed button organization in action frame

## Version 1.2.0 (2025-05-21)
### Added
- Multiple file selection for deletion
- Improved error handling in file operations
- Quality threshold slider for duplicate detection
- Recursive folder search option
- Better UI organization with separate preview areas
- Progress tracking during image comparison

### Changed
- Enhanced About dialog with proper window layout
- Improved code organization and readability
- Better error handling and user feedback
- Updated UI to use ttk widgets for a modern look
- Improved image preview functionality

### Fixed
- Various UI bugs and inconsistencies
- Fixed threading issues for smoother operation
- Improved memory management for large image sets
- Better handling of special characters in file paths

## Version 1.1.0 (2025-05-20)
### Added
- Modular code structure with separate files for About, Sponsor, and Version
- Version information integration
- Proper menu structure for About and Sponsor

### Changed
- Moved sponsor window to a menu
- Updated About dialog to use ttk widgets
- Improved code organization and readability
- Fixed version display in main window

### Fixed
- Various UI bugs and inconsistencies
- Improved error handling in file operations
- Sponsor window initialization error
- About dialog display
- Version information display

## Version 1.1.0
### Added
- Comprehensive help documentation
- Quality threshold slider for duplicate detection
- Side-by-side image preview
- Progress tracking during image comparison
- Batch operations for managing duplicates
- Improved error handling
- Support for multiple image formats

### Changed
- Improved UI layout and organization
- Better menu structure
- Enhanced image preview functionality
- Added quality comparison between images

### Fixed
- Various UI initialization issues
- Fixed image preview errors
- Improved error handling and user feedback

## Version 1.0.0
Initial release with basic functionality
- Image duplicate detection using perceptual hashing
- Basic GUI interface
- Folder browsing and image comparison
- Duplicate deletion capability
