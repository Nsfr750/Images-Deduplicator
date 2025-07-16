"""
Version management for Images Deduplicator.

This module provides a centralized version tracking system 
for the Images Deduplicator project.
"""

# Version components
MAJOR_VERSION = 1
MINOR_VERSION = 5  # Bumped for PyQt6 migration
PATCH_VERSION = 1

# Additional version qualifiers
VERSION_QUALIFIER = ''  # Could be 'alpha', 'beta', 'rc', or ''

# Dependency versions
PYQT6_VERSION = '6.4.0'
PILLOW_VERSION = '9.0.0'
IMAGEHASH_VERSION = '4.3.1'

def get_version():
    """
    Generate a full version string.
    
    Returns:
        str: Formatted version string
    """
    version_parts = [
        str(MAJOR_VERSION),
        str(MINOR_VERSION),
        str(PATCH_VERSION)
    ]
    version_str = '.'.join(version_parts)
    
    if VERSION_QUALIFIER:
        version_str += f'-{VERSION_QUALIFIER}'
    
    return version_str

def get_version_info():
    """
    Provide a detailed version information dictionary.
    
    Returns:
        dict: Comprehensive version information
    """
    return {
        'major': MAJOR_VERSION,
        'minor': MINOR_VERSION,
        'patch': PATCH_VERSION,
        'qualifier': VERSION_QUALIFIER,
        'full_version': get_version(),
        'dependencies': {
            'PyQt6': PYQT6_VERSION,
            'Pillow': PILLOW_VERSION,
            'imagehash': IMAGEHASH_VERSION
        }
    }

def check_version_compatibility(min_version):
    """
    Check if the current version meets the minimum required version.
    
    Args:
        min_version (str): Minimum required version in 'X.Y.Z' format
        
    Returns:
        bool: True if current version is >= min_version, False otherwise
    """
    current = tuple(map(int, get_version().split('-')[0].split('.')))
    required = tuple(map(int, min_version.split('.')))
    return current >= required

# Expose version as a module-level attribute for easy access
__version__ = get_version()

# Add version information for PyInstaller if needed
def get_versions():
    """
    Get all version information including dependencies.
    
    Returns:
        dict: Complete version information
    """
    return {
        'app_version': __version__,
        'dependencies': {
            'PyQt6': PYQT6_VERSION,
            'Pillow': PILLOW_VERSION,
            'imagehash': IMAGEHASH_VERSION
        }
    }
