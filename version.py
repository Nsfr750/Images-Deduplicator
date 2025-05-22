"""
Version management for Database Browser application.

This module provides a centralized version tracking system 
for the Database Browser project.
"""

# Version components
MAJOR_VERSION = 1
MINOR_VERSION = 3
PATCH_VERSION = 0

# Additional version qualifiers
VERSION_QUALIFIER = ''  # Could be 'alpha', 'beta', 'rc', or ''

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
        'major': VERSION_MAJOR,
        'minor': VERSION_MINOR,
        'patch': VERSION_PATCH,
        'qualifier': VERSION_QUALIFIER,
        'full_version': get_version()
    }

def check_version_compatibility(min_version):
    """
    Check if the current version meets the minimum required version.
    
    Args:
        min_version (str): Minimum version to compare against
    
    Returns:
        bool: True if current version is compatible, False otherwise
    """
    current_parts = [VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH]
    min_parts = [int(part) for part in min_version.split('.')]
    
    for current, minimum in zip(current_parts, min_parts):
        if current > minimum:
            return True
        elif current < minimum:
            return False
    
    return True

# Expose version as a module-level attribute for easy access
__version__ = get_version()
