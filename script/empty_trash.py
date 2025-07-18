"""
Empty trash functionality for Image Deduplicator.

This module provides platform-specific implementations for emptying the system trash/recycle bin.
"""
import os
import platform
import subprocess
import glob
import logging
from typing import Optional, Tuple, Dict, Any

# Import translation function
try:
    from .translations import t
except ImportError:
    # Fallback if translations module is not available
    def t(key: str, lang: str = 'en', **kwargs) -> str:
        return key  # Return the key as-is if translations are not available

logger = logging.getLogger(__name__)

def empty_system_trash(lang: str = 'en') -> Tuple[bool, str]:
    """
    Empty the system trash/recycle bin using platform-specific implementations.
    
    Args:
        lang: Language code for translations (e.g., 'en', 'it')
        
    Returns:
        Tuple[bool, str]: (success, message) - success status and a translated message
    """
    system = platform.system().lower()
    logger.info(f"Emptying trash on {system} platform")
    
    try:
        if system == 'windows':
            return _empty_windows_trash(lang)
        elif system == 'darwin':
            return _empty_macos_trash(lang)
        elif system == 'linux':
            return _empty_linux_trash(lang)
        else:
            return False, t('error.unsupported_platform', lang, platform=system)
    except Exception as e:
        logger.error(f"Error emptying trash: {e}", exc_info=True)
        return False, str(e)

def _empty_windows_trash(lang: str = 'en') -> Tuple[bool, str]:
    """
    Empty the Windows Recycle Bin.
    
    Args:
        lang: Language code for translations
        
    Returns:
        Tuple[bool, str]: (success, message) - success status and a translated message
    """
    try:
        # Try PowerShell method first
        result = subprocess.run(
            ['powershell', '-Command', 'Clear-RecycleBin -Force -ErrorAction Stop'],
            check=True,
            shell=True,
            capture_output=True,
            text=True
        )
        return True, t('empty_trash.success.windows', lang)
    except subprocess.CalledProcessError as e:
        logger.warning(f"PowerShell method failed: {e.stderr}")
        try:
            # Fall back to Shell API
            import ctypes
            SHELL32 = ctypes.windll.shell32
            SHELL32.SHEmptyRecycleBinW(None, None, 0)
            return True, t('empty_trash.success.windows', lang)
        except Exception as shell_error:
            logger.warning(f"Shell API method failed: {shell_error}")
            return False, t('empty_trash.error.windows', lang, error=str(shell_error))

def _empty_macos_trash(lang: str = 'en') -> Tuple[bool, str]:
    """
    Empty the macOS Trash.
    
    Args:
        lang: Language code for translations
        
    Returns:
        Tuple[bool, str]: (success, message) - success status and a translated message
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell app "Finder" to empty trash'],
            check=True,
            capture_output=True,
            text=True
        )
        return True, t('empty_trash.success.macos', lang)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to empty Trash: {e.stderr}")
        return False, t('empty_trash.error.macos', lang, error=e.stderr)

def _empty_linux_trash(lang: str = 'en') -> Tuple[bool, str]:
    """
    Empty the Linux trash directories.
    
    Args:
        lang: Language code for translations
        
    Returns:
        Tuple[bool, str]: (success, message) - success status and a translated message
    """
    try:
        # Try using the trash-cli package if available
        result = subprocess.run(
            ['trash-empty'],
            check=True,
            capture_output=True,
            text=True
        )
        return True, t('empty_trash.success.linux', lang)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to manual cleanup of common trash locations
        try:
            from send2trash import TrashDirectories
            trash_dirs = TrashDirectories()
            for trash_dir in trash_dirs:
                try:
                    files = glob.glob(os.path.join(trash_dir, '*'))
                    for f in files:
                        try:
                            os.remove(f)
                        except Exception as e:
                            logger.warning(f"Failed to remove {f}: {e}")
                except Exception as e:
                    logger.warning(f"Error processing trash dir {trash_dir}: {e}")
            return True, t('empty_trash.success.linux_manual', lang)
        except Exception as e:
            logger.error(f"Failed to empty trash: {e}", exc_info=True)
            return False, t('empty_trash.error.linux', lang, error=str(e))
