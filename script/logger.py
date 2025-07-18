"""
Logging configuration for Image Deduplicator.
"""
import os
import logging
import time
from pathlib import Path
from datetime import datetime

# Constants
LOG_FILE_PREFIX = "image_dedup_"
LOG_FILE_EXT = ".log"
LOG_DIR = Path("logs")
MAX_LOG_FILES = 10  # Maximum number of log files to keep

# Get the project root directory
APP_DIR = Path(__file__).parent.parent


def setup_logging() -> logging.Logger:
    """
    Configure and return the application logger with timestamped log files.
    
    Creates a new log file with timestamp on each application start.
    Also handles log rotation by keeping only the most recent MAX_LOG_FILES logs.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    try:
        # Create logs directory if it doesn't exist
        LOG_DIR.mkdir(exist_ok=True, parents=True)
        
        # Generate timestamp for log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{LOG_FILE_PREFIX}{timestamp}{LOG_FILE_EXT}"
        log_path = APP_DIR / LOG_DIR / log_filename
        
        # Clean up old log files
        _cleanup_old_logs()
        
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,  # Set to DEBUG to capture all levels
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Get the root logger
        logger = logging.getLogger()
        
        # Log the start of a new session
        logger.info("=" * 80)
        logger.info(f"Starting new logging session: {timestamp}")
        logger.info(f"Log file: {log_path}")
        logger.info("=" * 80)
        
        return logger
        
    except Exception as e:
        # Fallback to basic console logging if file logging fails
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to configure file logging: {e}")
        return logging.getLogger()


def _cleanup_old_logs():
    """Clean up old log files, keeping only the most recent MAX_LOG_FILES."""
    try:
        # Get all log files
        log_files = sorted(
            LOG_DIR.glob(f"{LOG_FILE_PREFIX}*{LOG_FILE_EXT}"),
            key=os.path.getmtime,
            reverse=True
        )
        
        # Remove old log files
        for log_file in log_files[MAX_LOG_FILES:]:
            try:
                log_file.unlink()
            except Exception as e:
                logging.warning(f"Failed to remove old log file {log_file}: {e}")
                
    except Exception as e:
        logging.error(f"Error during log cleanup: {e}")


# Create a module-level logger instance
logger = setup_logging()
