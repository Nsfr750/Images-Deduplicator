import os
import sys
import traceback
import queue
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QTimer, QObject, QUrl, QRunnable, QThreadPool, QSettings, 
    QMetaObject, Q_ARG, pyqtSlot
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QProgressBar, QCheckBox, QFrame, QMenuBar, QMenu, QStatusBar, QSizePolicy,
    QDialog, QGroupBox, QTextEdit, QDialogButtonBox, QTabWidget, QSplitter, QStyleFactory
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
from script.styles import setup_styles
from script.translations import t, LANGUAGES
from script.updates import UpdateChecker
from script.version import get_version, __version__
from script.settings import SettingsDialog
from script.menu import MenuManager
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
                    self.signals.error.emit(f"Error accessing folder {folder}: {str(e)}")
                    return

            # Remove duplicates and sort for consistent processing
            image_files = list(set(image_files))
            image_files.sort()

            total_files = len(image_files)
            if total_files < 2:
                error_msg = t('found_images', 'en', count=total_files)  # TODO: Use current language
                if total_files == 1:
                    error_msg += f"\n{t('found_image', 'en', image=os.path.basename(image_files[0]))}"
                elif total_files == 0:
                    error_msg += f"\n{t('no_images_found', 'en', exts=', '.join(supported_extensions))}"
                self.signals.error.emit(error_msg)
                return

            # Process images in chunks
            chunk_size = 10
            images = {}
            duplicates = {}
            processed_count = 0

            for i in range(0, len(image_files), chunk_size):
                if not self.is_running:
                    return
                    
                chunk = image_files[i:i + chunk_size]
                for filepath in chunk:
                    if not self.is_running:
                        return
                        
                    try:
                        # Skip if file doesn't exist or is not a file
                        if not os.path.isfile(filepath):
                            continue

                        # Skip if file is too large (prevent memory issues)
                        if os.path.getsize(filepath) > 100 * 1024 * 1024:  # 100MB limit
                            print(f"Skipping large file {filepath}")
                            continue

                        # Open and convert image to RGBA if it has transparency
                        image = Image.open(filepath)
                        if image.mode == 'P' and 'transparency' in image.info:
                            image = image.convert('RGBA')
                        hash_value = imagehash.average_hash(image)
                        
                        # Check for duplicates based on hash with similarity threshold
                        new_hash = str(hash_value)
                        duplicates_found = False
                        
                        # Compare with existing images
                        for existing_hash, existing_path in images.items():
                            # Calculate similarity percentage
                            similarity = 100 - (hash_value - imagehash.hex_to_hash(existing_hash))
                            if similarity >= self.similarity_threshold:
                                duplicates[filepath] = existing_path
                                duplicates_found = True
                                break
                        
                        if not duplicates_found:
                            images[new_hash] = filepath
                        
                        processed_count += 1
                        progress = int((processed_count / total_files) * 100)
                        self.signals.progress.emit(progress)
                    except Exception as e:
                        print(f"Skipping file {filepath}: {str(e)}")
                        continue

            self.signals.finished.emit(
                t('found_duplicates', 'en', count=len(duplicates)),  # TODO: Use current language
                duplicates
            )

        except Exception as e:
            self.signals.error.emit(
                t('error_comparison', 'en', error=str(e))  # TODO: Use current language
            )
    
    def stop(self):
        """Stop the worker thread."""
        self.is_running = False


class ImagePreview(QLabel):
    """Custom widget for displaying image previews with aspect ratio preservation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        self._pixmap = None
    
    def setPixmap(self, pixmap):
        """Override to store the original pixmap for scaling."""
        self._pixmap = pixmap
        self._scale_pixmap()
    
    def _scale_pixmap(self):
        """Scale the pixmap to fit the label while preserving aspect ratio."""
        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)
    
    def resizeEvent(self, event):
        """Handle resize events to scale the image."""
        self._scale_pixmap()
        super().resizeEvent(event)


class SponsorDialog(QDialog):
    """Dialog for sponsoring the project."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('sponsor', lang))
        self.setFixedSize(500, 200)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add message
        message = QLabel(t('sponsor_message', lang))
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Create buttons
        buttons = [
            (t('sponsor_github', lang), "https://github.com/sponsors/Nsfr750"),
            (t('join_discord', lang), "https://discord.gg/q5Pcgrju"),
            (t('buy_me_coffee', lang), "https://paypal.me/3dmega"),
            (t('join_patreon', lang), "https://www.patreon.com/Nsfr750")
        ]
        
        for text, url in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, u=url: self.open_url(u))
            layout.addWidget(btn)
        
        # Close button
        close_btn = QPushButton(t('close', lang))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def open_url(self, url):
        """Open URL in default browser."""
        QDesktopServices.openUrl(QUrl(url))


class StylePreviewDialog(QDialog):
    """Dialog to preview different styles."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('style_preview'))
        self.setMinimumSize(800, 600)
        self.current_theme = 'light'
        self.current_style = QApplication.style().objectName()
        self.preview_widgets = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout()
        
        self.theme_group = QButtonGroup(self)
        
        self.light_theme_btn = QRadioButton("Light")
        self.light_theme_btn.setChecked(True)
        self.theme_group.addButton(self.light_theme_btn, 0)
        
        self.dark_theme_btn = QRadioButton("Dark")
        self.theme_group.addButton(self.dark_theme_btn, 1)
        
        self.theme_group.buttonToggled.connect(self.on_theme_changed)
        
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.light_theme_btn)
        theme_layout.addWidget(self.dark_theme_btn)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        
        # Style selection
        style_group = QGroupBox(t('select_style_preview'))
        style_layout = QHBoxLayout()
        
        # Style list
        self.style_list = QListWidget()
        self.style_list.setMaximumWidth(200)
        self.style_list.currentItemChanged.connect(self.on_style_changed)
        
        # Preview area
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        
        # Sample widgets for preview
        sample_group = QGroupBox("Preview")
        self.sample_layout = QVBoxLayout()
        
        # Create sample widgets
        self.create_sample_widgets()
        
        sample_group.setLayout(self.sample_layout)
        preview_layout.addWidget(sample_group)
        
        # Add style list and preview to layout
        style_layout.addWidget(self.style_list)
        style_layout.addWidget(self.preview_widget, 1)
        style_group.setLayout(style_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add all to main layout
        layout.addWidget(theme_group)
        layout.addWidget(style_group, 1)
        layout.addWidget(button_box)
        
        # Populate styles
        self.populate_styles()
    
    def create_sample_widgets(self):
        """Create sample widgets for preview."""
        # Clear existing widgets
        while self.sample_layout.count():
            item = self.sample_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create new sample widgets
        self.sample_label = QLabel(t('sample_text'))
        self.sample_button = QPushButton(t('sample_button'))
        self.sample_checkbox = QCheckBox(t('sample_checkbox'))
        self.sample_progress = QProgressBar()
        self.sample_progress.setValue(50)
        
        # Store references
        self.preview_widgets = [
            self.sample_label,
            self.sample_button,
            self.sample_checkbox,
            self.sample_progress
        ]
        
        # Add to layout
        self.sample_layout.addWidget(self.sample_label)
        self.sample_layout.addWidget(self.sample_button)
        self.sample_layout.addWidget(self.sample_checkbox)
        self.sample_layout.addWidget(self.sample_progress)
        self.sample_layout.addStretch()
    
    def populate_styles(self):
        """Populate the style list with available styles."""
        self.style_list.clear()
        styles = QStyleFactory.keys()
        
        for style in styles:
            item = QListWidgetItem(style)
            item.setData(Qt.ItemDataRole.UserRole, style)
            if style.lower() == self.current_style.lower():
                item.setSelected(True)
                self.style_list.setCurrentItem(item)
            self.style_list.addItem(item)
    
    def on_theme_changed(self, button, checked):
        """Handle theme change."""
        if checked:
            self.current_theme = 'dark' if button == self.dark_theme_btn else 'light'
            self.update_preview_style()
    
    def on_style_changed(self, current, previous):
        """Handle style change."""
        if not current:
            return
            
        style_name = current.data(Qt.ItemDataRole.UserRole)
        if not style_name:
            return
            
        self.current_style = style_name
        self.update_preview_style()
    
    def update_preview_style(self):
        """Update the preview with current style and theme."""
        try:
            # Create a temporary style
            style = QStyleFactory.create(self.current_style)
            if not style:
                return
            
            # Apply stylesheet based on theme
            stylesheet = self.get_stylesheet()
            
            # Apply to preview widget and its children
            def apply_style(widget):
                widget.setStyle(style)
                widget.setStyleSheet(stylesheet)
                widget.update()
            
            apply_style(self.preview_widget)
            for widget in self.preview_widgets:
                apply_style(widget)
                
        except Exception as e:
            logging.error(f"Error updating preview: {e}")
    
    def get_stylesheet(self):
        """Get the stylesheet for the current theme."""
        if self.current_theme == 'dark':
            return """
                QWidget {
                    background-color: #353535;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #404040;
                    color: #f0f0f0;
                    border: 1px solid #555555;
                    padding: 5px;
                    min-width: 80px;
                }
                QCheckBox {
                    color: #f0f0f0;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    background: #2a2a2a;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d7;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    color: #f0f0f0;
                    margin-top: 10px;
                    padding-top: 15px;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    min-width: 80px;
                }
                QProgressBar {
                    border: 1px solid #cccccc;
                    background: #ffffff;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d7;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    margin-top: 10px;
                    padding-top: 15px;
                }
            """
    
    def get_selected_style(self):
        """Get the currently selected style."""
        current = self.style_list.currentItem()
        return current.data(Qt.ItemDataRole.UserRole) if current else None
    
    def get_selected_theme(self):
        """Get the currently selected theme."""
        return self.current_theme


class ImageDeduplicatorApp(QMainWindow):
    """Main application window for Image Deduplicator."""
    
    def __init__(self):
        super().__init__()
        self.config_file = Path('config.json')
        self.load_config()
        
        # Initialize default values if not in config
        self.lang = self.config.get('language', 'en')
        self.duplicates = {}
        self.worker = None
        self.comparison_in_progress = False
        self.update_checker = UpdateChecker(__version__)
        self.log_file = str(log_path)
        
        # Set default style and theme from config
        self.current_style = self.config.get('style', 'Fusion')
        self.current_theme = self.config.get('theme', 'dark')
        
        # Load settings
        self.settings = QSettings('ImagesDeduplicator', 'ImageDeduplicator')
        
        # Set up thread pool
        self.thread_pool = QThreadPool()
        
        # Apply the style and theme
        self.apply_style(self.current_style, save=False)
        self.apply_theme(self.current_theme)
        
        # Set application icon
        icon_path = os.path.join('assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui()
        self.setup_connections()
        
        # Log application start
        logger.info("=" * 50)
        logger.info(f"Starting Image Deduplicator v{__version__}")
        logger.info(f"Log file: {self.log_file}")
        
        # Check for updates on startup
        QTimer.singleShot(1000, self.check_for_updates_on_startup)

    def load_config(self):
        """Load configuration from config.json."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Create default config if it doesn't exist
                self.config = {
                    "language": "en",
                    "theme": "dark",
                    "style": "Fusion",
                    "comparison": {
                        "similarity_threshold": 85,
                        "recursive_search": True
                    }
                }
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading config: {str(e)}")
            self.config = {
                "language": "en",
                "theme": "dark",
                "style": "Fusion",
                "comparison": {
                    "similarity_threshold": 85,
                    "recursive_search": True
                }
            }

    def save_config(self):
        """Save configuration to config.json."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving config: {str(e)}")

    def set_language(self, lang_code):
        """Change the application language and update the UI."""
        action = self.sender()
        if action and action.isChecked():
            self.lang = lang_code
            self.config['language'] = lang_code
            self.save_config()
            self.menu_manager.update_language(lang_code)
            self.retranslate_ui()

    def apply_theme(self, theme, apply_style=True):
        """Apply the selected theme."""
        self.current_theme = theme
        self.config['theme'] = theme
        self.save_config()
        
        # Rest of the apply_theme method...

    def apply_style(self, style_name='Fusion', save=True, apply_theme=True):
        """Apply the selected style."""
        self.current_style = style_name
        self.config['style'] = style_name
        self.save_config()
        
        # Rest of the apply_style method...

    def closeEvent(self, event):
        """Handle the window close event."""
        # Save current settings to config
        self.config['language'] = self.lang
        self.config['theme'] = self.current_theme
        self.config['style'] = self.current_style
        self.save_config()
        
        # Clean up preview widgets to prevent QPainter errors
        if hasattr(self, 'duplicate_preview'):
            self.duplicate_preview.clear()
        if hasattr(self, 'original_preview'):
            self.original_preview.clear()
        
        # Clean up thread
        if hasattr(self, 'thread') and isinstance(self.thread, QThread):
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
        
        # Clean up worker
        if hasattr(self, 'worker'):
            if self.worker:
                self.worker.stop()
                self.worker.deleteLater()
        
        event.accept()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(t('app_title', self.lang, version=get_version()))
        self.setGeometry(100, 100, 1200, 800)
        
        # Set up status bar first
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t('ready', self.lang))
        
        # Apply style and theme
        self.apply_style(self.current_style)
        self.apply_theme(self.current_theme)
        
        # Initialize menu manager
        self.menu_manager = MenuManager(self, self.lang)
        self.setMenuBar(self.menu_manager.get_menubar())
        
        self.setup_central_widget()
        
        # Check for updates
        self.check_for_updates()
    
    def setup_central_widget(self):
        """Set up the central widget."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Progress bar
        self.progress_frame = QFrame()
        self.progress_layout = QHBoxLayout(self.progress_frame)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("font-weight: bold;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        
        self.progress_layout.addWidget(self.progress_label)
        self.progress_layout.addWidget(self.progress_bar, 1)
        
        # Duplicates list
        self.duplicates_list = QListWidget()
        self.duplicates_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Buttons frame
        self.buttons_frame = QFrame()
        self.buttons_layout = QHBoxLayout(self.buttons_frame)
        
        self.select_all_button = QPushButton(t('select_all', self.lang))
        self.delete_selected_button = QPushButton(t('delete_selected', self.lang))
        self.delete_all_button = QPushButton(t('delete_all_duplicates', self.lang))
        
        self.buttons_layout.addWidget(self.select_all_button)
        self.buttons_layout.addWidget(self.delete_selected_button)
        self.buttons_layout.addWidget(self.delete_all_button)
        
        # Preview frame
        self.preview_frame = QFrame()
        self.preview_layout = QHBoxLayout(self.preview_frame)
        
        # Duplicate preview
        self.duplicate_frame = QGroupBox(t('duplicate_image_preview', self.lang))
        self.duplicate_layout = QVBoxLayout(self.duplicate_frame)
        self.duplicate_preview = QLabel()
        self.duplicate_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duplicate_preview.setStyleSheet("background-color: #f0f0f0;")
        self.duplicate_preview.setMinimumSize(400, 300)
        self.duplicate_layout.addWidget(self.duplicate_preview)
        
        # Original preview
        self.original_frame = QGroupBox(t('original_image_preview', self.lang))
        self.original_layout = QVBoxLayout(self.original_frame)
        self.original_preview = QLabel()
        self.original_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_preview.setStyleSheet("background-color: #f0f0f0;")
        self.original_preview.setMinimumSize(400, 300)
        self.original_layout.addWidget(self.original_preview)
        
        self.preview_layout.addWidget(self.duplicate_frame, 1)
        self.preview_layout.addWidget(self.original_frame, 1)
        
        # Folder selection
        self.folder_frame = QFrame()
        self.folder_layout = QHBoxLayout(self.folder_frame)
        
        # Left side of folder frame
        self.folder_left = QFrame()
        self.folder_left_layout = QVBoxLayout(self.folder_left)
        
        self.folder_label = QLabel(t('select_folder', self.lang))
        self.folder_entry = QLineEdit()
        self.folder_entry.setReadOnly(True)
        
        self.folder_left_layout.addWidget(self.folder_label)
        self.folder_left_layout.addWidget(self.folder_entry)
        
        # Right side of folder frame
        self.folder_right = QFrame()
        self.folder_right_layout = QVBoxLayout(self.folder_right)
        
        self.browse_button = QPushButton(t('browse', self.lang))
        self.recursive_check = QCheckBox(t('search_subfolders', self.lang))
        self.recursive_check.setChecked(True)
        
        self.folder_right_layout.addWidget(self.browse_button)
        self.folder_right_layout.addWidget(self.recursive_check)
        
        # Add to folder layout
        self.folder_layout.addWidget(self.folder_left, 1)
        self.folder_layout.addWidget(self.folder_right)
        
        # Compare button
        self.compare_button = QPushButton(t('compare_images', self.lang))
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.folder_frame)
        self.main_layout.addWidget(self.compare_button)
        self.main_layout.addWidget(self.progress_frame)
        self.main_layout.addWidget(self.duplicates_list, 1)
        self.main_layout.addWidget(self.buttons_frame)
        self.main_layout.addWidget(self.preview_frame, 1)
    
    def setup_connections(self):
        """Set up signal-slot connections."""
        self.browse_button.clicked.connect(self.browse_folder)
        
        self.compare_button.clicked.connect(self.compare_images)
        self.select_all_button.clicked.connect(self.select_all_duplicates)
        self.delete_selected_button.clicked.connect(self.delete_selected)  
        self.delete_all_button.clicked.connect(self.delete_all_duplicates)
        
        # Connect item selection changes to both preview and button state updates
        self.duplicates_list.itemSelectionChanged.connect(self.update_preview)
        self.duplicates_list.itemSelectionChanged.connect(self.update_button_states)
    
    def update_ui_state(self):
        """Update the UI state based on the current application state."""
        has_duplicates = len(self.duplicates) > 0
        self.delete_all_button.setEnabled(has_duplicates)
        self.update_button_states()
    
    def update_button_states(self):
        """Update the state of the action buttons."""
        has_selection = len(self.duplicates_list.selectedItems()) > 0
        self.delete_selected_button.setEnabled(has_selection)
    
    def change_language(self):
        """Change the application language."""
        action = self.sender()
        if action and action.isChecked():
            self.lang = action.data()
            self.menu_manager.update_language(lang_code)
            self.retranslate_ui()
        
    def retranslate_ui(self):
        """Retranslate all UI elements to the current language."""
        self.setWindowTitle(t('app_title', self.lang, version=get_version()))
        self.status_bar.showMessage(t('ready', self.lang))
        
    def closeEvent(self, event):
        """Handle the window close event."""
        # Save current settings to config
        self.config['language'] = self.lang
        self.config['theme'] = self.current_theme
        self.config['style'] = self.current_style
        self.save_config()
        
        # Clean up preview widgets to prevent QPainter errors
        if hasattr(self, 'duplicate_preview'):
            self.duplicate_preview.clear()
        if hasattr(self, 'original_preview'):
            self.original_preview.clear()
        
        # Clean up thread
        if hasattr(self, 'thread') and isinstance(self.thread, QThread):
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
        
        # Clean up worker
        if hasattr(self, 'worker'):
            if self.worker:
                self.worker.stop()
                self.worker.deleteLater()
        
        event.accept()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(t('app_title', self.lang, version=get_version()))
        self.setGeometry(100, 100, 1200, 800)
        
        # Set up status bar first
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t('ready', self.lang))
        
        # Apply style and theme
        self.apply_style(self.current_style)
        self.apply_theme(self.current_theme)
        
        # Initialize menu manager
        self.menu_manager = MenuManager(self, self.lang)
        self.setMenuBar(self.menu_manager.get_menubar())
        
        self.setup_central_widget()
        
        # Check for updates
        self.check_for_updates()
    
    def browse_folder(self):
        """Open a folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            t('select_folder', self.lang),
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if folder:
            self.folder_entry.setText(folder)
            self.update_status(t('selected_folder', self.lang, folder=folder))
            
    def compare_images(self):
        """Start the image comparison process."""
        folder = self.folder_entry.text().strip()
        if not folder:
            QMessageBox.warning(self, t('warning', self.lang), t('no_folder_selected', self.lang))
            return

        if not os.path.isdir(folder):
            QMessageBox.warning(self, t('warning', self.lang), t('invalid_folder', self.lang))
            return

        # Get comparison settings from config
        comparison = self.config.get('comparison', {})
        similarity_threshold = comparison.get('similarity_threshold', 85)
        recursive = comparison.get('recursive_search', True)

        self.comparison_in_progress = True
        self.compare_button.setEnabled(False)
        self.update_status(t('scanning_folder', self.lang, folder=folder))
        
        # Clear previous results
        self.duplicates_list.clear()
        self.duplicates.clear()
        self.duplicate_preview.clear()
        self.original_preview.clear()
        
        # Create and start worker
        self.worker = ImageComparisonWorker(
            folder,
            recursive=recursive,
            similarity_threshold=similarity_threshold
        )
        
        # Connect signals
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.comparison_complete)
        self.worker.signals.error.connect(self.comparison_error)
        
        # Start the worker in the thread pool
        self.thread_pool.start(self.worker)

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)
    
    def comparison_complete(self, message, duplicates):
        """Handle completion of the image comparison."""
        self.comparison_in_progress = False
        self.compare_button.setEnabled(True)
        self.progress_label.setText(message)
        
        self.duplicates = duplicates
        self.display_duplicates()
        self.update_status(t('comparison_complete', self.lang, count=len(duplicates)))
        
    def comparison_error(self, message):
        """Handle errors during image comparison."""
        self.comparison_in_progress = False
        self.compare_button.setEnabled(True)
        self.progress_label.setText(message)
        self.update_status(t('comparison_error', self.lang), 5000)  # Show for 5 seconds
        
    def display_duplicates(self):
        """Display the list of duplicate images."""
        self.duplicates_list.clear()
        
        for duplicate, original in self.duplicates.items():
            item = QListWidgetItem(
                f"{t('duplicate', self.lang)}: {duplicate} | {t('original', self.lang)}: {original}"
            )
            item.setData(Qt.ItemDataRole.UserRole, (duplicate, original))
            self.duplicates_list.addItem(item)
        
        self.update_ui_state()
    
    def update_preview(self):
        """Update the preview panes with the selected duplicate and original images."""
        if not self.comparison_in_progress:
            self._load_preview_images()

    def _load_preview_images(self):
        """Internal method to load and display preview images."""
        selected_items = self.duplicates_list.selectedItems()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        file_paths = selected_item.data(Qt.ItemDataRole.UserRole)
        
        if not file_paths or not isinstance(file_paths, tuple) or len(file_paths) != 2:
            self.duplicate_preview.clear()
            self.original_preview.clear()
            return
            
        duplicate_path, original_path = file_paths
        
        try:
            # Load and display duplicate image
            if os.path.exists(duplicate_path):
                with Image.open(duplicate_path) as img:
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    pixmap = QPixmap.fromImage(ImageQt.ImageQt(img))
                    self.duplicate_preview.setPixmap(pixmap)
            else:
                self.duplicate_preview.clear()
            
            # Load and display original image
            if os.path.exists(original_path):
                with Image.open(original_path) as img:
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    pixmap = QPixmap.fromImage(ImageQt.ImageQt(img))
                    self.original_preview.setPixmap(pixmap)
            else:
                self.original_preview.clear()
                    
        except Exception as e:
            logger.error(f"Error loading preview: {str(e)}")
            self.duplicate_preview.clear()
            self.original_preview.clear()

    def resizeEvent(self, event):
        """Handle window resize events to update previews."""
        super().resizeEvent(event)
        if not self.comparison_in_progress:
            self._load_preview_images()

    def preview_image(self):
        """Preview the selected duplicate and original images."""
        if not self.comparison_in_progress:
            self._load_preview_images()
    
    def select_all_duplicates(self):
        """Select all items in the duplicates list."""
        # Select all items in the list
        self.duplicates_list.selectAll()
        
        # Update the button states to reflect the selection
        self.update_button_states()
        
        # Update the preview to show the first selected item
        if self.duplicates_list.count() > 0:
            self.duplicates_list.setCurrentRow(0)
    
    def delete_selected(self):
        """Delete the selected duplicate images."""
        selected_items = self.duplicates_list.selectedItems()
        if not selected_items:
            self.update_status(t('no_items_selected', self.lang))
            return
        
        num_selected = len(selected_items)
        if num_selected > 1:
            message = t('confirm_delete_selected', self.lang, count=num_selected)
        else:
            message = t('confirm_delete_one', self.lang)
        
        reply = QMessageBox.question(
            self,
            t('confirm_delete', self.lang),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            failed_count = 0
            failed_items = []
            
            for item in selected_items:
                duplicate_path, _ = item.data(Qt.ItemDataRole.UserRole)
                try:
                    os.remove(duplicate_path)
                    deleted_count += 1
                    
                    # Remove from duplicates dictionary
                    if duplicate_path in self.duplicates:
                        del self.duplicates[duplicate_path]
                    
                except Exception as e:
                    failed_count += 1
                    failed_items.append(f"{duplicate_path}: {str(e)}")
            
            # Update the UI
            self.display_duplicates()
            
            # Show result message
            if failed_count > 0:
                error_message = "\n".join(failed_items)
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('failed_to_delete_items', self.lang, count=failed_count, error=error_message)
                )
            
            if deleted_count > 0:
                if deleted_count > 1:
                    QMessageBox.information(
                        self,
                        t('info', self.lang),
                        t('successfully_deleted', self.lang, count=deleted_count)
                    )
                else:
                    QMessageBox.information(
                        self,
                        t('info', self.lang),
                        t('successfully_deleted_one', self.lang)
                    )
    
    def delete_all_duplicates(self):
        """Delete all duplicate images."""
        if not self.duplicates:
            self.update_status(t('no_duplicates_found', self.lang))
            return
        
        reply = QMessageBox.question(
            self,
            t('confirm_delete_all', self.lang),
            t('confirm_delete_all', self.lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            failed_count = 0
            failed_items = []
            
            for duplicate_path in list(self.duplicates.keys()):
                try:
                    os.remove(duplicate_path)
                    deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_items.append(f"{duplicate_path}: {str(e)}")
            
            # Clear duplicates and update UI
            self.duplicates.clear()
            self.display_duplicates()
            
            # Show result message
            if failed_count > 0:
                error_message = "\n".join(failed_items)
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('failed_to_delete_items', self.lang, count=failed_count, error=error_message)
                )
            
            if deleted_count > 0:
                QMessageBox.information(
                    self,
                    t('info', self.lang),
                    t('all_deleted', self.lang)
                )
    
    def show_about(self):
        """Show the about dialog."""
        from script.about import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def check_for_updates(self, silent=False):
        """Check for application updates."""
        self.update_status(t('checking_for_updates', self.lang))
        
        def update_check_complete(update_available, update_info):
            if update_available and update_info:
                self.show_update_dialog(update_info)
            elif not silent:
                QMessageBox.information(
                    self,
                    t('no_updates', self.lang),
                    t('you_are_using_latest_version', self.lang)
                )
        
        # Create worker and thread
        self.update_worker = UpdateCheckerWorker(self.update_checker)
        self.update_thread = QThread()
        self.update_worker.moveToThread(self.update_thread)
        
        # Connect signals
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished_signal.connect(update_check_complete)
        self.update_worker.finished_signal.connect(self.update_thread.quit)
        self.update_worker.finished_signal.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        
        # Start the thread
        self.update_thread.start()
    
    def check_for_updates_on_startup(self):
        """Check for updates on application startup."""
        # Only check for updates if not in debug mode
        if not getattr(sys, 'gettrace', lambda: None)():
            self.check_for_updates(silent=True)
        else:
            logger.info("Debug mode: Skipping update check")
    
    def show_update_dialog(self, update_info):
        """Show update dialog with update information."""
        dialog = QDialog(self)
        dialog.setWindowTitle(t('update_available', self.lang))
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Version info
        current = QLabel(f"{t('current_version', self.lang)}: {get_version()}")
        new = QLabel(f"{t('new_version_available', self.lang).format(version=update_info['version'])}")
        
        # Release notes
        notes = QTextEdit()
        notes.setReadOnly(True)
        notes.setHtml(update_info.get('notes', t('no_release_notes', self.lang)))
        
        # Buttons
        btn_box = QDialogButtonBox()
        download_btn = btn_box.addButton(t('download_now', self.lang), QDialogButtonBox.ButtonRole.AcceptRole)
        later_btn = btn_box.addButton(t('remind_me_later', self.lang), QDialogButtonBox.ButtonRole.RejectRole)
        
        download_btn.clicked.connect(lambda: self.download_update(update_info['url']))
        later_btn.clicked.connect(dialog.reject)
        
        layout.addWidget(current)
        layout.addWidget(new)
        layout.addWidget(QLabel(t('release_notes', self.lang) + ":"))
        layout.addWidget(notes)
        layout.addWidget(btn_box)
        
        dialog.exec()
    
    def download_update(self, url):
        """Open download URL in default browser."""
        QDesktopServices.openUrl(QUrl(url))
    
    def show_help(self):
        """Show help dialog."""
        dialog = HelpDialogScript(self, self.lang)
        dialog.exec()
    
    def show_sponsor(self):
        """Show sponsor dialog."""
        dialog = SponsorDialog(self, self.lang)
        dialog.exec()
    
    def show_style_preview(self):
        """Show the style preview dialog."""
        dialog = StylePreviewDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_style(dialog.get_selected_style(), save=True)
    
    def show_log_viewer(self):
        """Show the log viewer dialog."""
        try:
            self.log_viewer = LogViewer(self, self.log_file)
            self.log_viewer.show()
        except Exception as e:
            logger.error(f"Failed to open log viewer: {str(e)}")
            QMessageBox.critical(
                self,
                t('error', self.lang),
                t('log_viewer_error', self.lang, default="Failed to open log viewer: {error}").format(error=str(e))
            )

    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.lang, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pass  # Settings saved automatically through config

    def set_language(self, lang_code):
        """Change the application language."""
        self.lang = lang_code
        self.menu_manager.update_language(lang_code)
        self.retranslate_ui()
        
    def apply_style(self, style_name='Fusion', save=True, apply_theme=True):
        """
        Apply the selected style to the application.
        
        Args:
            style_name: Name of the style to apply (only 'Fusion' is supported)
            save: Whether to save the style preference
            apply_theme: Whether to apply the current theme after changing the style
        """
        try:
            # Only allow Fusion style
            style_name = 'Fusion'
            
            # Apply the style
            style = QStyleFactory.create(style_name)
            if not style:
                raise ValueError(f"Failed to create style: {style_name}")
                
            QApplication.setStyle(style)
            self.current_style = style_name
            
            # Apply the current theme if requested
            if apply_theme and hasattr(self, 'current_theme'):
                # Use apply_theme with apply_style=False to prevent recursion
                self.apply_theme(self.current_theme, apply_style=False)
            
            # Save the style preference
            if save:
                self.settings.setValue('style', style_name)
                
            logging.info(f"Successfully applied style: {style_name}")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error applying style: {error_msg}")
            QMessageBox.critical(
                self,
                t('error', self.lang),
                t('style_apply_error', self.lang).format(error=error_msg)
            )
    
    def apply_theme(self, theme, apply_style=True):
        """Apply the selected theme."""
        try:
            from script.styles import setup_dark_theme, setup_light_theme
            
            # Force dark theme
            theme = 'dark'
            
            # Apply the theme
            if theme.lower() == 'dark':
                setup_dark_theme(QApplication.instance())
            else:
                setup_light_theme(QApplication.instance())
                
            # Save the theme preference
            self.settings.setValue('theme', theme)
            self.current_theme = theme
            
            # Apply the style to ensure theme is properly set
            if apply_style:
                self.apply_style('Fusion', save=False)
            
            # Update the status bar message if it exists
            status_bar = self.statusBar()
            if status_bar is not None:
                status_bar.showMessage(
                    t('theme_changed', self.lang).format(theme=theme.capitalize()),
                    3000
                )
                
            logging.info(f'Theme changed to: {theme}')
            
            # Force update all widgets
            self.style().unpolish(QApplication.instance())
            self.style().polish(QApplication.instance())
            self.update()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f'Error applying theme: {error_msg}')
            QMessageBox.critical(
                self, 
                t('error', self.lang), 
                t('theme_error', self.lang).format(error=error_msg)
            )
    
    def update_status(self, message: str, timeout: int = 3000):
        """
        Update the status bar message.
        
        Args:
            message: The message to display
            timeout: How long to display the message in milliseconds (0 = show until next message)
        """
        self.statusBar().showMessage(message, timeout)
        # Also log status messages at info level
        logger.info(f"Status: {message}")


class UpdateCheckerWorker(QObject):
    """Worker object for checking updates."""
    finished_signal = pyqtSignal(bool, object)
    
    def __init__(self, update_checker):
        super().__init__()
        self.update_checker = update_checker
        self.update_available = False
        self.update_info = None
    
    def on_update_available(self, update_info):
        self.update_available = True
        self.update_info = update_info
        self.finished_signal.emit(True, self.update_info)
    
    def on_no_updates(self):
        self.update_available = False
        self.finished_signal.emit(False, None)
    
    def on_error(self, error_msg):
        print(f"Error checking for updates: {error_msg}", file=sys.stderr)
        self.finished_signal.emit(False, None)
    
    def run(self):
        """Run the update check."""
        # Connect signals
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_updates.connect(self.on_no_updates)
        self.update_checker.error_occurred.connect(self.on_error)
        
        # Start the update check
        self.update_checker.check_for_updates(force_check=True)


def main():
    """Main entry point for the application."""
    # Create the application instance
    app = QApplication(sys.argv)
    
    try:
        # Setup application styles and theme
        setup_styles(app)
        
        # Set application information
        app.setApplicationName("Image Deduplicator")
        app.setApplicationVersion(__version__)
        app.setOrganizationName("Nsfr750")
        
        # Create and show the main window
        window = ImageDeduplicatorApp()
        window.show()
        
        # Start the event loop
        return app.exec()
    except Exception as e:
        # Log any unhandled exceptions
        logging.critical(f"Unhandled exception: {str(e)}")
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"A fatal error occurred: {str(e)}\n\nPlease check the log file for more details."
        )
        return 1


if __name__ == "__main__":
    # Set up basic logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "image_dedup.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Run the application
    sys.exit(main())
