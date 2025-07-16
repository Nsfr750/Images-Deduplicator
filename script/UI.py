"""
UI module for Image Deduplicator application.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os
import logging
from PyQt6.QtCore import Qt, QTimer, QThreadPool, QSettings, QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QSplitter, QSizePolicy, QGroupBox, QStatusBar
)
from PyQt6.QtGui import QPixmap, QDesktopServices, QPainter, QColor
from PIL import Image, ImageQt
from script.translations import t
from script.styles import apply_style, apply_theme
from script.about import AboutDialog
from script.help import HelpDialog as HelpDialogScript
from script.log_viewer import LogViewer
from script.sponsor import SponsorDialog
from script.menu import MenuManager
from script.updates import UpdateChecker
from script.version import __version__
from script.workers import ImageComparisonWorker
from script.settings_dialog import SettingsDialog  # Add this import

logger = logging.getLogger(__name__)

class ImagePreview(QLabel):
    """Custom widget for displaying image previews with aspect ratio preservation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("""
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 4px;
            color: #e0e0e0;
        """)
        self._pixmap = None
        self._original_pixmap = None
        
    def setPixmap(self, pixmap):
        """Set the pixmap and keep a reference to the original."""
        if pixmap and not pixmap.isNull():
            self._original_pixmap = pixmap
            self._pixmap = pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(self._pixmap)
        else:
            self._original_pixmap = None
            self._pixmap = None
            super().setPixmap(QPixmap())
    
    def resizeEvent(self, event):
        """Handle resize events to maintain aspect ratio."""
        super().resizeEvent(event)
        if self._original_pixmap and not self._original_pixmap.isNull():
            self._pixmap = self._original_pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(self._pixmap)
    
    def paintEvent(self, event):
        """Custom paint event to handle painting with error checking."""
        if not self._pixmap or self._pixmap.isNull():
            # Draw placeholder when no image is set
            painter = QPainter(self)
            if not painter.isActive():
                return
                
            try:
                # Draw background
                painter.fillRect(self.rect(), QColor(60, 63, 65))
                
                # Draw placeholder text
                font = painter.font()
                font.setPointSize(12)
                painter.setFont(font)
                painter.setPen(QColor(224, 224, 224))
                
                text = "No image"
                text_rect = painter.fontMetrics().boundingRect(text)
                text_rect.moveCenter(self.rect().center())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
                
            finally:
                painter.end()
        else:
            # Draw the scaled pixmap
            painter = QPainter(self)
            if not painter.isActive():
                return
                
            try:
                # Draw background
                painter.fillRect(self.rect(), QColor(60, 63, 65))
                
                # Calculate centered position for the pixmap
                x = (self.width() - self._pixmap.width()) // 2
                y = (self.height() - self._pixmap.height()) // 2
                
                # Draw the pixmap
                painter.drawPixmap(x, y, self._pixmap)
                
            finally:
                painter.end()

class UI(QMainWindow):
    """Main UI class for Image Deduplicator."""
    
    def __init__(self, config, lang='en'):
        super().__init__()
        self.config = config
        self.lang = lang
        self.duplicates = {}
        self.worker = None
        self.comparison_in_progress = False
        self.update_checker = UpdateChecker(__version__)
        self.log_file = str(Path("logs") / "image_dedup.log")
        
        # Set default style and theme from config
        self.current_style = self.config.get('appearance', {}).get('style', 'Fusion')
        self.current_theme = self.config.get('appearance', {}).get('theme', 'dark')
        
        # Load settings
        self.settings = QSettings('ImagesDeduplicator', 'ImageDeduplicator')
        
        # Set up thread pool
        self.thread_pool = QThreadPool()
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        # Apply the style and theme
        self.apply_style(self.current_style, save=False, apply_theme_flag=True)
        
        # Log application start
        logger.info("=" * 50)
        logger.info(f"Starting Image Deduplicator v{__version__}")
        logger.info(f"Log file: {self.log_file}")
        
        # Check for updates on startup
        QTimer.singleShot(1000, self.check_for_updates_on_startup)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(t('app_title', self.lang, version=__version__))
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Initialize menu bar
        self.menu_manager = MenuManager(self, self.lang)
        self.setMenuBar(self.menu_manager.menubar)
        
        # --- Folder Selection ---
        folder_frame = QFrame()
        folder_layout = QHBoxLayout(folder_frame)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        
        self.folder_label = QLabel(t('select_folder', self.lang))
        self.folder_entry = QLineEdit()
        self.folder_entry.setReadOnly(True)
        self.browse_button = QPushButton(t('browse', self.lang))
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_entry, 1)
        folder_layout.addWidget(self.browse_button)
        
        # --- Compare Button ---
        self.compare_button = QPushButton(t('compare', self.lang))
        self.compare_button.setObjectName("compareButton")
        
        # --- Progress Bar ---
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        # --- Duplicates List ---
        duplicates_group = QGroupBox(t('duplicates_found', self.lang))
        duplicates_layout = QVBoxLayout(duplicates_group)
        
        self.duplicates_list = QListWidget()
        self.duplicates_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        duplicates_layout.addWidget(self.duplicates_list)
        
        # --- Image Previews ---
        preview_frame = QFrame()
        preview_layout = QHBoxLayout(preview_frame)
        
        # Original Image
        original_group = QGroupBox(t('original_image', self.lang))
        original_layout = QVBoxLayout(original_group)
        self.original_preview = ImagePreview()
        self.original_path = QLabel()
        self.original_path.setWordWrap(True)
        original_layout.addWidget(self.original_preview, 1)
        original_layout.addWidget(self.original_path)
        
        # Duplicate Image
        duplicate_group = QGroupBox(t('duplicate_image', self.lang))
        duplicate_layout = QVBoxLayout(duplicate_group)
        self.duplicate_preview = ImagePreview()
        self.duplicate_path = QLabel()
        self.duplicate_path.setWordWrap(True)
        duplicate_layout.addWidget(self.duplicate_preview, 1)
        duplicate_layout.addWidget(self.duplicate_path)
        
        preview_layout.addWidget(original_group, 1)
        preview_layout.addWidget(duplicate_group, 1)
        
        # --- Action Buttons ---
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        self.select_all_button = QPushButton(t('select_all', self.lang))
        self.select_none_button = QPushButton(t('select_none', self.lang))
        self.delete_selected_button = QPushButton(t('delete_selected', self.lang))
        self.delete_all_button = QPushButton(t('delete_all_duplicates', self.lang))
        
        # Style delete buttons differently
        self.delete_selected_button.setObjectName("deleteButton")
        self.delete_all_button.setObjectName("deleteButton")
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.select_none_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.delete_selected_button)
        buttons_layout.addWidget(self.delete_all_button)
        
        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t('ready', self.lang))
        
        # Add all widgets to main layout
        self.main_layout.addWidget(folder_frame)
        self.main_layout.addWidget(self.compare_button)
        self.main_layout.addWidget(self.progress_frame)
        self.main_layout.addWidget(duplicates_group, 1)
        self.main_layout.addWidget(preview_frame, 1)
        self.main_layout.addWidget(buttons_frame)
        
        # Set minimum sizes
        self.duplicates_list.setMinimumHeight(150)
        self.original_preview.setMinimumHeight(200)
        self.duplicate_preview.setMinimumHeight(200)
        
        # Initially hide progress bar
        self.progress_frame.hide()
    
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Menu connections
        self.menu_manager.action_exit.triggered.connect(self.close)
        
        # Button connections
        self.browse_button.clicked.connect(self.browse_folder)
        self.compare_button.clicked.connect(self.compare_images)
        self.select_all_button.clicked.connect(self.select_all_duplicates)
        self.select_none_button.clicked.connect(self.select_none_duplicates)
        self.delete_selected_button.clicked.connect(self.delete_selected)
        self.delete_all_button.clicked.connect(self.delete_all_duplicates)
        
        # List selection
        self.duplicates_list.itemSelectionChanged.connect(self.update_preview)
        
        # Update button states
        self.duplicates_list.itemSelectionChanged.connect(self.update_button_states)
        self.duplicates_list.model().rowsInserted.connect(self.update_button_states)
        self.duplicates_list.model().rowsRemoved.connect(self.update_button_states)
    
    def apply_style(self, style_name, save=True, apply_theme_flag=True):
        """
        Apply the specified style to the application.
        
        Args:
            style_name: Name of the style to apply (only 'Fusion' is supported)
            save: Whether to save the style to config
            apply_theme_flag: Whether to also apply the current theme
        """
        if style_name != 'Fusion':
            logger.warning(f"Style '{style_name}' is not supported. Using 'Fusion' style.")
            style_name = 'Fusion'
        
        # Apply the style
        apply_style(QApplication.instance(), style_name)
        
        # Save to config if requested
        if save:
            if 'appearance' not in self.config:
                self.config['appearance'] = {}
            self.config['appearance']['style'] = style_name
            self._save_config()
        
        # Apply theme if requested
        if apply_theme_flag:
            self.apply_theme(self.current_theme, apply_style_flag=False)
    
    def apply_theme(self, theme_name, apply_style_flag=True):
        """
        Apply the specified theme to the application.
        
        Args:
            theme_name: Name of the theme to apply (only 'dark' is supported)
            apply_style_flag: Whether to also apply the current style
        """
        if theme_name != 'dark':
            logger.warning(f"Theme '{theme_name}' is not supported. Using 'dark' theme.")
            theme_name = 'dark'
        
        # Apply the theme
        apply_theme(QApplication.instance(), theme_name)
        
        # Save to config
        if 'appearance' not in self.config:
            self.config['appearance'] = {}
        self.config['appearance']['theme'] = theme_name
        self._save_config()
        
        # Apply style if requested
        if apply_style_flag:
            self.apply_style(self.current_style, save=False, apply_theme_flag=False)
    
    def _save_config(self):
        """Save the current configuration to the config file."""
        try:
            config_dir = Path('config')
            config_dir.mkdir(exist_ok=True)
            
            with open(config_dir / 'config.json', 'w') as f:
                import json
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def browse_folder(self):
        """Open a folder selection dialog and update the folder path."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            t('select_folder', self.lang),
            self.folder_entry.text() or str(Path.home())
        )
        
        if folder:
            self.folder_entry.setText(folder)
    
    def compare_images(self):
        """Start the image comparison process."""
        folder = self.folder_entry.text()
        if not folder or not Path(folder).is_dir():
            QMessageBox.warning(self, 
                             t('error', self.lang), 
                             t('invalid_folder', self.lang))
            return
        
        # Reset state
        self.duplicates = {}
        self.duplicates_list.clear()
        self.original_preview.clear()
        self.duplicate_preview.clear()
        self.original_path.clear()
        self.duplicate_path.clear()
        
        # Show progress
        self.progress_frame.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText(t('scanning_folder', self.lang))
        self.status_bar.showMessage(t('scanning_folder', self.lang))
        
        # Disable UI during comparison
        self.set_ui_enabled(False)
        self.comparison_in_progress = True
        
        # Get comparison settings from config
        similarity_threshold = self.config.get('comparison', {}).get('similarity_threshold', 85)
        recursive = self.config.get('comparison', {}).get('recursive_search', True)
        
        # Create and start the worker
        self.worker = ImageComparisonWorker(
            folder=folder,
            recursive=recursive,
            similarity_threshold=similarity_threshold
        )
        
        # Connect signals
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.finished.connect(self.on_comparison_finished)
        self.worker.signals.error.connect(self._handle_worker_error)
        
        # Start the worker in the thread pool
        self.thread_pool.start(self.worker)
    
    def _handle_worker_error(self, msg):
        """Handle errors from the worker thread."""
        QMessageBox.critical(self, t('error', self.lang), msg)
        self.set_ui_enabled(True)
        self.comparison_in_progress = False
    
    def on_comparison_finished(self, message, duplicates):
        """Handle the completion of the image comparison."""
        try:
            logger.info("Image comparison finished")
            self.comparison_in_progress = False
            
            # Update progress bar and status
            self.progress_bar.setValue(100)
            self.progress_label.setText(t('comparison_complete', self.lang))
            self.status_bar.showMessage(message)
            
            # Update duplicates list if provided
            if duplicates:
                logger.info(f"Found {sum(len(dups) for dups in duplicates.values())} duplicates to display")
                self.duplicates = duplicates
                self.update_duplicates_list()
            else:
                logger.info("No duplicates found")
                QMessageBox.information(
                    self,
                    t('no_duplicates', self.lang),
                    t('no_duplicates_found_message', self.lang)
                )
                
        except Exception as e:
            error_msg = f"Error processing comparison results: {str(e)}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self,
                t('error', self.lang),
                error_msg
            )
        finally:
            # Always re-enable UI and clean up
            self.set_ui_enabled(True)
            self.worker = None
            QApplication.processEvents()  # Ensure UI updates are processed
    
    def update_duplicates_list(self):
        """Update the duplicates list with the current duplicates."""
        self.duplicates_list.clear()
        
        try:
            # The duplicates dictionary is now {original_path: [duplicate1_path, duplicate2_path, ...]}
            for original_path, dup_paths in self.duplicates.items():
                for dup_path in dup_paths:
                    # Create a display name that shows the relative path from the search directory
                    display_name = os.path.relpath(dup_path, self.folder_entry.text()) if self.folder_entry.text() else dup_path
                    
                    item = QListWidgetItem(display_name)
                    # Store both original and duplicate paths in the item's data
                    item.setData(Qt.ItemDataRole.UserRole, (original_path, dup_path))
                    self.duplicates_list.addItem(item)
            
            # Update status with total number of duplicates found (not the number of groups)
            total_duplicates = sum(len(dups) for dups in self.duplicates.values())
            self.status_bar.showMessage(t('duplicates_found', self.lang).format(count=total_duplicates))
            
        except Exception as e:
            logger.error(f"Error updating duplicates list: {e}")
            self.status_bar.showMessage(t('error_updating_list', self.lang))
    
    def update_preview(self):
        """Update the image preview based on the current selection."""
        try:
            selected_items = self.duplicates_list.selectedItems()
            if not selected_items:
                self.original_preview.clear()
                self.duplicate_preview.clear()
                self.original_path.clear()
                self.duplicate_path.clear()
                return
            
            # Get the first selected item
            item = selected_items[0]
            try:
                # Get the stored data (original_path, duplicate_path)
                original_path, duplicate_path = item.data(Qt.ItemDataRole.UserRole)
                
                # Load and display original image
                self.load_image_preview(original_path, self.original_preview, self.original_path)
                
                # Load and display duplicate image
                self.load_image_preview(duplicate_path, self.duplicate_preview, self.duplicate_path)
                
            except (TypeError, ValueError) as e:
                logger.error(f"Error getting image paths from selected item: {e}")
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('error_loading_preview', self.lang)
                )
                
        except Exception as e:
            logger.error(f"Error in update_preview: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                t('error', self.lang),
                f"An unexpected error occurred: {str(e)}"
            )
    
    def load_image_preview(self, image_path, preview_widget, path_label):
        """Load an image preview into the specified widget.
        
        Args:
            image_path: Path to the image file
            preview_widget: QLabel or ImagePreview widget to display the image
            path_label: QLabel to display the image path
        """
        # Clear previous content
        preview_widget.clear()
        path_label.clear()
        
        # Validate input
        if not image_path or not isinstance(image_path, (str, Path)):
            logger.warning(f"Invalid image path: {image_path}")
            path_label.setText(t('invalid_image_path', self.lang))
            return
        
        try:
            # Convert to Path object and validate
            img_path = Path(image_path)
            
            # Check if the path exists and is a file
            if not img_path.exists():
                logger.warning(f"Image file not found: {image_path}")
                path_label.setText(t('image_not_found', self.lang))
                return
                
            if not img_path.is_file():
                logger.warning(f"Path is not a file: {image_path}")
                path_label.setText(t('not_a_file', self.lang))
                return
            
            # Update path label with filename and tooltip with full path
            path_label.setText(img_path.name)
            path_label.setToolTip(str(img_path.absolute()))
            
            # Load and process image using Pillow
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB if needed (e.g., for PNG with transparency)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        background = Image.new('RGB', img.size, (60, 63, 65))  # Match dark theme
                        background.paste(img, mask=img.split()[-1])  # Paste with alpha mask
                        img = background
                    
                    # Convert to QPixmap
                    qimg = ImageQt.ImageQt(img)
                    pixmap = QPixmap.fromImage(qimg)
                    
                    # Set the pixmap
                    if hasattr(preview_widget, 'setPixmap'):
                        preview_widget.setPixmap(pixmap)
                    else:
                        logger.error(f"Preview widget does not support setPixmap: {preview_widget}")
                        
            except Exception as img_error:
                logger.error(f"Error processing image {img_path}: {img_error}", exc_info=True)
                path_label.setText(t('error_processing_image', self.lang))
                
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}", exc_info=True)
            path_label.setText(t('error_loading_image', self.lang))
    
    def select_all_duplicates(self):
        """Select all items in the duplicates list."""
        self.duplicates_list.selectAll()
    
    def select_none_duplicates(self):
        """Deselect all items in the duplicates list."""
        self.duplicates_list.clearSelection()
    
    def delete_selected(self):
        """Delete the selected duplicate files."""
        selected_items = self.duplicates_list.selectedItems()
        if not selected_items:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            t('confirm_deletion', self.lang),
            t('confirm_delete_selected', self.lang).format(count=len(selected_items)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            deleted = 0
            for item in selected_items:
                _, duplicate_path = item.data(Qt.ItemDataRole.UserRole)
                try:
                    Path(duplicate_path).unlink()
                    deleted += 1
                except Exception as e:
                    logger.error(f"Error deleting file {duplicate_path}: {e}")
            
            # Update UI
            self.status_bar.showMessage(t('deleted_files', self.lang).format(count=deleted))
            self.update_duplicates_list()
    
    def delete_all_duplicates(self):
        """Delete all duplicate files, keeping only the originals."""
        if self.duplicates_list.count() == 0:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            t('confirm_deletion', self.lang),
            t('confirm_delete_all', self.lang).format(count=self.duplicates_list.count()),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            deleted = 0
            for i in range(self.duplicates_list.count()):
                item = self.duplicates_list.item(i)
                _, duplicate_path = item.data(Qt.ItemDataRole.UserRole)
                try:
                    Path(duplicate_path).unlink()
                    deleted += 1
                except Exception as e:
                    logger.error(f"Error deleting file {duplicate_path}: {e}")
            
            # Update UI
            self.status_bar.showMessage(t('deleted_files', self.lang).format(count=deleted))
            self.update_duplicates_list()
    
    def update_button_states(self):
        """Update the state of the action buttons based on the current selection."""
        has_items = self.duplicates_list.count() > 0
        has_selection = len(self.duplicates_list.selectedItems()) > 0
        
        self.select_all_button.setEnabled(has_items)
        self.select_none_button.setEnabled(has_items)
        self.delete_selected_button.setEnabled(has_selection)
        self.delete_all_button.setEnabled(has_items)
    
    def set_ui_enabled(self, enabled):
        """Enable or disable UI elements during long operations."""
        self.browse_button.setEnabled(enabled)
        self.compare_button.setEnabled(enabled)
        self.select_all_button.setEnabled(enabled and self.duplicates_list.count() > 0)
        self.select_none_button.setEnabled(enabled and self.duplicates_list.count() > 0)
        self.delete_selected_button.setEnabled(enabled and len(self.duplicates_list.selectedItems()) > 0)
        self.delete_all_button.setEnabled(enabled and self.duplicates_list.count() > 0)
    
    def show_about(self):
        """Show the about dialog."""
        dialog = AboutDialog(self)  
        dialog.exec()
    
    def show_help(self):
        """Show the help dialog."""
        dialog = HelpDialogScript(self, self.lang)
        dialog.exec()
    
    def show_log_viewer(self):
        """Show the log viewer dialog."""
        dialog = LogViewer(self, self.lang)
        dialog.exec()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.lang, self.config)
        if dialog.exec():
            # Apply any changed settings
            if 'appearance' in dialog.config:
                new_style = dialog.config['appearance'].get('style', 'Fusion')
                new_theme = dialog.config['appearance'].get('theme', 'dark')
                
                if new_style != self.current_style:
                    self.current_style = new_style
                    self.apply_style(new_style, save=False, apply_theme_flag=True)
                elif new_theme != self.current_theme:
                    self.current_theme = new_theme
                    self.apply_theme(new_theme, apply_style_flag=False)
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        dialog = SponsorDialog(self, self.lang)
        dialog.exec()
    
    def set_language(self, lang_code):
        """
        Set the application language.
        
        Args:
            lang_code: Language code to set (e.g., 'en', 'es')
        """
        if lang_code != self.lang:
            self.lang = lang_code
            
            # Save language preference
            self.config['language'] = lang_code
            self._save_config()
            
            # Update UI language
            self.retranslate_ui()
    
    def retranslate_ui(self):
        """Retranslate all UI elements to the current language."""
        self.setWindowTitle(t('app_title', self.lang, version=__version__))
        
        # Update folder selection
        self.folder_label.setText(t('select_folder', self.lang))
        self.browse_button.setText(t('browse', self.lang))
        self.compare_button.setText(t('compare', self.lang))
        
        # Update group boxes if they exist
        if hasattr(self, 'duplicates_group'):
            self.duplicates_group.setTitle(t('duplicates_found', self.lang))
        
        # Update preview groups if they exist
        if hasattr(self, 'original_group'):
            self.original_group.setTitle(t('original_image', self.lang))
        if hasattr(self, 'duplicate_group'):
            self.duplicate_group.setTitle(t('duplicate_image', self.lang))
        
        # Update buttons
        self.select_all_button.setText(t('select_all', self.lang))
        self.select_none_button.setText(t('select_none', self.lang))
        self.delete_selected_button.setText(t('delete_selected', self.lang))
        self.delete_all_button.setText(t('delete_all_duplicates', self.lang))
        
        # Update status bar
        if not self.comparison_in_progress:
            self.status_bar.showMessage(t('ready', self.lang))
    
    def check_for_updates_on_startup(self):
        """Check for updates on application startup."""
        try:
            # Only check once per day
            last_check = self.settings.value('last_update_check')
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            if last_check != today:
                logger.info("Checking for updates...")
                try:
                    # Use a singleShot timer to ensure the UI is fully initialized
                    QTimer.singleShot(2000, self._perform_update_check)
                except Exception as e:
                    logger.error(f"Error scheduling update check: {e}")
        except Exception as e:
            logger.error(f"Error in check_for_updates_on_startup: {e}")
    
    def _perform_update_check(self):
        """Perform the actual update check."""
        try:
            update_available, latest_version, changelog = self.update_checker.check_for_updates()
            
            # Update last check time
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            self.settings.setValue('last_update_check', today)
            
            if update_available:
                logger.info(f"Update available: {latest_version}")
                msg = t('update_available', self.lang).format(
                    current=__version__,
                    latest=latest_version
                )
                
                # Show update dialog in a non-blocking way
                QTimer.singleShot(100, lambda: self._show_update_dialog(msg, latest_version, changelog))
            else:
                logger.info("No updates available")
                
        except Exception as e:
            logger.error(f"Error in _perform_update_check: {e}")
    
    def _show_update_dialog(self, message, latest_version, changelog):
        """Show the update dialog with the given message and changelog."""
        try:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(t('update_available_title', self.lang))
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)
            
            # Add detailed text if available
            if changelog:
                msg_box.setDetailedText(changelog)
            
            # Add buttons
            download_btn = msg_box.addButton(t('download_update', self.lang), QMessageBox.ButtonRole.AcceptRole)
            msg_box.addButton(t('later', self.lang), QMessageBox.ButtonRole.RejectRole)
            
            # Show the dialog
            msg_box.exec()
            
            if msg_box.clickedButton() == download_btn:
                QDesktopServices.openUrl(QUrl(f"https://github.com/Nsfr750/Images-Deduplicator/releases/tag/v{latest_version}"))
                
        except Exception as e:
            logger.error(f"Error showing update dialog: {e}")
    
    def check_for_updates(self, silent=False):
        """Check for application updates.
        
        Args:
            silent: If True, don't show a message when no updates are available
        """
        try:
            from script.updates import UpdateChecker
            
            self.status_bar.showMessage(t('checking_for_updates', self.lang))
            
            def update_check_complete(update_available, version_info):
                if update_available:
                    msg = t('update_available', self.lang).format(
                        current=__version__,
                        latest=version_info.get('tag_name', 'unknown')
                    )
                    
                    # Add release notes if available
                    if 'body' in version_info:
                        msg += f"\n\n{version_info['body']}"
                    
                    # Add download URL if available
                    if 'html_url' in version_info:
                        msg += f"\n\n{t('download_at', self.lang)}: {version_info['html_url']}"
                    
                    # Show update dialog
                    reply = QMessageBox.information(
                        self,
                        t('update_available_title', self.lang),
                        msg,
                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore,
                        QMessageBox.StandardButton.Ok
                    )
                    
                    if reply == QMessageBox.StandardButton.Ok and 'html_url' in version_info:
                        QDesktopServices.openUrl(QUrl(version_info['html_url']))
                elif not silent:
                    QMessageBox.information(
                        self,
                        t('no_updates_title', self.lang),
                        t('no_updates_available', self.lang).format(version=__version__)
                    )
                
                self.status_bar.showMessage(t('ready', self.lang))
            
            # Run update check in a separate thread
            self.update_checker = UpdateChecker(current_version=__version__)
            self.update_checker.update_available.connect(update_check_complete)
            self.update_checker.error_occurred.connect(
                lambda error: (
                    logger.error(f"Error checking for updates: {error}"),
                    self.status_bar.showMessage(t('update_check_failed', self.lang)),
                    QMessageBox.warning(
                        self,
                        t('error', self.lang),
                        t('update_check_failed', self.lang)
                    ) if not silent else None
                )
            )
            self.update_checker.start()
            
        except Exception as e:
            logger.error(f"Error in check_for_updates: {e}", exc_info=True)
            if not silent:
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('update_check_failed', self.lang)
                )
            self.status_bar.showMessage(t('update_check_failed', self.lang))
    
    def closeEvent(self, event):
        """
        Handle the close event to ensure proper cleanup of resources.
        
        Args:
            event: The close event
        """
        # Stop any running operations
        if hasattr(self, 'worker') and self.worker is not None:
            self.worker.stop()
            self.worker.wait()
        
        # Save window geometry
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        
        # Log application shutdown
        logger.info("Image Deduplicator shutting down")
        logger.info("=" * 50)
        
        # Accept the close event
        event.accept()
