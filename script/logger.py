"""
Logging configuration for Image Deduplicator.
"""
import os
import logging
from pathlib import Path

# Constants
LOG_FILE = "image_dedup.log"
LOG_DIR = Path("logs")
APP_DIR = Path(__file__).parent.parent  # Get the project root directory
LOG_PATH = APP_DIR / LOG_DIR / LOG_FILE

def setup_logging() -> logging.Logger:
    """
    Configure and return the application logger.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Return the root logger
    return logging.getLogger(__name__)

# Create a module-level logger instance
logger = setup_logging()
