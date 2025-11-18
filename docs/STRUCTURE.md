# Project Structure

```text
Images-Deduplicator/
├── assets/                         # Static assets (icons, images, etc.)
│   └── icons/                      # Application icons
│   └── styles/                     # Style sheets and themes
│
├── cache/                          # Cache directory for temporary files
│   └── image_hashes.json           # Cached image hashes for comparison
│
├── config/                         # Configuration files
│   └── settings.json               # User settings and preferences
│
├── docs/                           # Documentation
│   ├── CHANGELOG.md                # Project changelog
│   ├── README.md                   # Main documentation
│   ├── ROADMAP.md                  # Development roadmap
│   ├── SECURITY.md                 # Security policy
│   ├── STRUCTURE.md                # This file (project structure)
│   └── IMAGES/                     # Documentation images and screenshots
│
├── logs/                           # Application logs
│   └── app.log                     # Main application log file
│
├── script/                         # Main application source code
│   ├── __init__.py                 # Package initialization
│   ├── about.py                    # About dialog implementation
│   ├── empty_trash.py              # Trash management functionality
│   ├── help.py                     # Help system implementation
│   ├── image_dialog_preview.py     # Image preview dialog
│   ├── language_manager.py         # Internationalization support
│   ├── log_viewer.py               # Log viewer interface
│   ├── logger.py                   # Logging configuration
│   ├── menu.py                     # Application menu implementation
│   ├── settings_dialog.py          # Settings dialog
│   ├── sponsor.py                  # Sponsorship information
│   ├── styles.py                   # UI styling and theming
│   ├── translations.py             # Translation strings
│   ├── undo_manager.py             # Undo/Redo functionality
│   ├── update_preview.py           # Preview update functionality
│   ├── updates.py                  # Update checking and management
│   ├── version.py                  # Version information
│   └── workers.py                  # Background workers
│
├── setup/                          # Build and installation
│   ├── setup.py                    # Installation script
│   └── requirements.txt            # Python dependencies
│
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_ui.py                  # UI component tests
│   └── test_workers.py             # Worker thread tests
│
├── .gitignore                      # Git ignore rules
├── README.md                       # Project README
└── requirements.txt                # Main project dependencies

## Directory Descriptions

- **assets/**: Contains all static resources like icons and stylesheets
- **cache/**: Stores temporary data and cached information
- **config/**: Holds configuration files and user settings
- **docs/**: Project documentation and related files
- **logs/**: Application log files
- **script/**: Main source code of the application
- **setup/**: Build and installation related files
- **tests/**: Automated tests for the application

## Key Files

- `script/__main__.py`: Application entry point
- `script/UI.py`: Main user interface implementation
- `script/workers.py`: Background task handlers
- `script/logger.py`: Logging configuration
- `script/translations.py`: Internationalization strings
- `requirements.txt`: Python package dependencies
- `setup.py`: Installation and distribution configuration
