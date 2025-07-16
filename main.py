"""
Image Deduplicator - Find and remove duplicate images.
"""
import os
import sys
import traceback
import queue
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QTimer, QObject, QUrl, QRunnable, 
    QThreadPool, QSettings, QMetaObject, Q_ARG, pyqtSlot
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QProgressBar, QCheckBox, QFrame, QMenuBar, QMenu, QStatusBar, QSizePolicy,
    QDialog, QGroupBox, QTextEdit, QDialogButtonBox, QTabWidget, QSplitter, 
    QStyleFactory, QComboBox
)
from PyQt6.QtGui import (
    QPixmap, QImage, QIcon, QPainter, QColor, QFont, QDesktopServices, QAction
)

from PIL import Image, ImageQt
import imagehash
from script.about import AboutDialog
from script.help import HelpDialog as HelpDialogScript
from script.log_viewer import LogViewer
from script.sponsor import SponsorDialog
from script.styles import setup_styles, apply_theme, apply_style
from script.translations import t, LANGUAGES
from script.updates import UpdateChecker
from script.version import get_version, __version__
from script.settings import SettingsDialog
from script.menu import MenuManager
from script.UI import UI
import logging

# Configure logging
LOG_FILE = "image_dedup.log"
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_path = log_dir / LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, dict)  # message, duplicates
    error = pyqtSignal(str)


class ImageComparisonWorker(QRunnable):
    """Worker thread for image comparison."""
    
    def __init__(self, folder: str, recursive: bool = True, similarity_threshold: int = 85):
        super().__init__()
        self.folder = folder
        self.recursive = recursive
        self.similarity_threshold = similarity_threshold
        self.signals = WorkerSignals()
        self.is_running = True

    def run(self):
        """Main processing function that runs in a separate thread."""
        try:
            # Get all image files using recursive search
            supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', 
                                  '.tiff', '.tif', '.psd', '.webp', '.svg')
            image_files = []
            
            # Normalize folder path to ensure correct path handling
            folder = os.path.abspath(self.folder)
            
            if self.recursive:
                # Use os.walk for more reliable recursive search
                for root, _, files in os.walk(folder):
                    for f in files:
                        if not self.is_running:
                            return
                            
                        if f.lower().endswith(supported_extensions):
                            full_path = os.path.join(root, f)
                            if os.path.isfile(full_path):
                                image_files.append(full_path)
            else:
                # Get files from current directory only
                try:
                    for f in os.listdir(folder):
                        if not self.is_running:
                            return
                            
                        if f.lower().endswith(supported_extensions):
                            full_path = os.path.join(folder, f)
                            if os.path.isfile(full_path):
                                image_files.append(full_path)
                except OSError as e:
                    self.signals.error.emit(str(e))
                    return
            
            if not image_files:
                self.signals.error.emit(t('no_images_found', 'en'))
                return
            
            total_images = len(image_files)
            logger.info(f"Found {total_images} images to process")
            
            # Calculate image hashes
            hashes = {}
            for i, image_path in enumerate(image_files):
                if not self.is_running:
                    return
                    
                try:
                    with Image.open(image_path) as img:
                        # Convert to RGB if image has an alpha channel
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            img = img.convert('RGB')
                        
                        # Calculate perceptual hash
                        phash = str(imagehash.phash(img))
                        
                        if phash in hashes:
                            hashes[phash].append(image_path)
                        else:
                            hashes[phash] = [image_path]
                    
                    # Update progress
                    progress = int((i + 1) / total_images * 100)
                    self.signals.progress.emit(progress)
                    
                except Exception as e:
                    logger.error(f"Error processing {image_path}: {str(e)}")
                    continue
            
            # Find duplicates (hashes with more than one image)
            duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
            
            if not duplicates:
                self.signals.finished.emit(t('no_duplicates_found', 'en'), {})
            else:
                self.signals.finished.emit(
                    t('duplicates_found', 'en', count=len(duplicates)),
                    duplicates
                )
                
        except Exception as e:
            logger.error(f"Error in image comparison: {str(e)}")
            logger.error(traceback.format_exc())
            self.signals.error.emit(str(e))
    
    def stop(self):
        """Stop the worker thread."""
        self.is_running = False


def main():
    """Main entry point for the application."""
    # Set up the application
    app = QApplication(sys.argv)
    
    # Load configuration
    config_file = Path('config.json')
    config = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading config: {str(e)}")
    
    # Create and show the main window
    window = UI(config)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    # Set up basic logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'image_dedup.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Start the application
    main()
