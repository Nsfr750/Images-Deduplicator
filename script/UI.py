"""
UI module for Image Deduplicator application.
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os
import json
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QThreadPool, QSettings, QUrl, QThread, QMetaObject, Q_ARG
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QSplitter, QSizePolicy, QGroupBox, QStatusBar,
    QProgressDialog, QCheckBox, QSlider
)
from PyQt6.QtGui import QPixmap, QDesktopServices, QPainter, QColor, QImage
from wand.image import Image as WandImage
import io
from script.translations import t, LANGUAGES
from script.styles import apply_style, apply_theme
from script.about import AboutDialog
from script.help import HelpDialog as HelpDialogScript
from script.log_viewer import LogViewer
from script.sponsor import SponsorDialog
from script.menu import MenuManager
from script.updates import UpdateChecker
from script.version import __version__
from script.workers import ImageComparisonWorker
from script.settings_dialog import SettingsDialog  
from script.logger import logger
from script.undo_manager import UndoManager, FileOperation
from script.language_manager import LanguageManager  

class UI(QMainWindow):
    """Main UI class for Image Deduplicator."""
    
    def __init__(self, config, lang='en'):
        super().__init__()
        self.config = config
        
        # Initialize language manager
        self.lang_manager = LanguageManager(default_lang=lang)
        self.lang = self.lang_manager.current_language  
        
        self.duplicates = {}
        self.worker = None
        self.comparison_in_progress = False
        
        # Set up logging with DEBUG level
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger with DEBUG level
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "image_dedup_debug.log"),
                logging.StreamHandler()
            ]
        )
        
        # Get logger for this module
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Initialize thread pool for background tasks
        self.thread_pool = QThreadPool()
        self.logger.debug(f"Thread pool initialized with max thread count: {self.thread_pool.maxThreadCount()}")
        
        self.update_checker = UpdateChecker(__version__, language_manager=self.lang_manager)
        self.log_file = str(log_dir / "image_dedup.log")
        
        # Set default style and theme from config
        self.current_style = self.config.get('appearance', {}).get('style', 'Fusion')
        self.current_theme = self.config.get('appearance', {}).get('theme', 'dark')
        
        # Log initialization
        self.logger.info("=" * 50)
        self.logger.info(f"Starting Image Deduplicator v{__version__}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.debug(f"Configuration: {self.config}")
        
        # Load settings
        self.settings = QSettings("ImageDeduplicator", "ImageDeduplicator")
        
        # Initialize undo manager
        self.undo_manager = UndoManager()
        self.undo_action = None  # Will be set by MenuManager
        
        # Connect language changed signal
        self.lang_manager.language_changed.connect(self.on_language_changed)
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        # Apply the style and theme
        self.apply_style(self.current_style, save=False, apply_theme_flag=True)
        
        # Check for updates on startup
        QTimer.singleShot(1000, self.check_for_updates_on_startup)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.lang_manager.translate('app_title', version=__version__))
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Initialize menu bar with language manager
        self.menu_manager = MenuManager(self, self.lang_manager)
        self.setMenuBar(self.menu_manager.menubar)
        
        # --- Folder Selection ---
        folder_frame = QFrame()
        folder_layout = QHBoxLayout(folder_frame)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        
        self.folder_label = QLabel(self.lang_manager.translate('select_folder'))
        self.folder_entry = QLineEdit()
        self.folder_entry.setReadOnly(True)
        self.browse_button = QPushButton(self.lang_manager.translate('browse'))
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_entry, 1)
        folder_layout.addWidget(self.browse_button)
        
        # --- Scan Options ---
        options_frame = QFrame()
        options_layout = QHBoxLayout(options_frame)
        options_layout.setContentsMargins(0, 5, 0, 5)
        
        # Recursive search option
        self.recursive_checkbox = QCheckBox(self.lang_manager.translate('search_subfolders'))
        self.recursive_checkbox.setChecked(True)  # Default to True
        options_layout.addWidget(self.recursive_checkbox)
        
        # Keep better quality option
        self.keep_better_quality_checkbox = QCheckBox(self.lang_manager.translate('keep_better_quality'))
        self.keep_better_quality_checkbox.setChecked(True)  # Default to True
        options_layout.addWidget(self.keep_better_quality_checkbox)
        
        # Preserve metadata option
        self.preserve_metadata_checkbox = QCheckBox(self.lang_manager.translate('preserve_metadata'))
        self.preserve_metadata_checkbox.setChecked(True)  # Default to True
        options_layout.addWidget(self.preserve_metadata_checkbox)
        
        options_layout.addStretch()
        
        # --- Similarity Threshold ---
        threshold_frame = QFrame()
        threshold_layout = QHBoxLayout(threshold_frame)
        threshold_layout.setContentsMargins(0, 0, 0, 0)
        
        self.similarity_label = QLabel(self.lang_manager.translate('similarity_threshold'))
        self.similarity_slider = QSlider(Qt.Orientation.Horizontal)
        self.similarity_slider.setRange(70, 100)  # 70% to 100% similarity
        self.similarity_slider.setValue(85)  # Default value
        self.similarity_value = QLabel("85%")
        self.similarity_slider.valueChanged.connect(
            lambda v: self.similarity_value.setText(f"{v}%"))
        
        threshold_layout.addWidget(self.similarity_label)
        threshold_layout.addWidget(self.similarity_slider)
        threshold_layout.addWidget(self.similarity_value)
        
        # --- Compare Button ---
        self.compare_button = QPushButton(self.lang_manager.translate('compare'))
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
        duplicates_group = QGroupBox(self.lang_manager.translate('duplicates_found'))
        duplicates_layout = QVBoxLayout(duplicates_group)
        
        self.duplicates_list = QListWidget()
        self.duplicates_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        duplicates_layout.addWidget(self.duplicates_list)
        
        # --- Image Previews ---
        preview_frame = QFrame()
        preview_layout = QHBoxLayout(preview_frame)
        
        # Original Image
        original_group = QGroupBox(self.lang_manager.translate('original_image'))
        original_layout = QVBoxLayout(original_group)
        self.original_preview = QLabel()
        self.original_path = QLabel()
        self.original_path.setWordWrap(True)
        original_layout.addWidget(self.original_preview, 1)
        original_layout.addWidget(self.original_path)
        
        # Duplicate Image
        duplicate_group = QGroupBox(self.lang_manager.translate('duplicate_image'))
        duplicate_layout = QVBoxLayout(duplicate_group)
        self.duplicate_preview = QLabel()
        self.duplicate_path = QLabel()
        self.duplicate_path.setWordWrap(True)
        duplicate_layout.addWidget(self.duplicate_preview, 1)
        duplicate_layout.addWidget(self.duplicate_path)
        
        preview_layout.addWidget(original_group, 1)
        preview_layout.addWidget(duplicate_group, 1)
        
        # --- Action Buttons ---
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        self.select_all_button = QPushButton(self.lang_manager.translate('select_all'))
        self.select_none_button = QPushButton(self.lang_manager.translate('select_none'))
        self.delete_selected_button = QPushButton(self.lang_manager.translate('delete_selected'))
        self.delete_all_button = QPushButton(self.lang_manager.translate('delete_all_duplicates'))
        
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
        self.status_bar.showMessage(self.lang_manager.translate('ready'))
        
        # Add all widgets to main layout
        self.main_layout.addWidget(folder_frame)
        self.main_layout.addWidget(options_frame)
        self.main_layout.addWidget(threshold_frame)
        self.main_layout.addWidget(self.compare_button)
        self.main_layout.addWidget(self.progress_frame)  # Add progress frame to main layout
        self.main_layout.addWidget(duplicates_group, 1)
        self.main_layout.addWidget(preview_frame, 2)
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
            self.lang_manager.translate('select_folder'),
            self.folder_entry.text() or str(Path.home())
        )
        
        if folder:
            self.folder_entry.setText(folder)
    
    def compare_images(self):
        """Start the image comparison process."""
        folder = self.folder_entry.text().strip()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, self.lang_manager.translate('error'), 
                              self.lang_manager.translate('invalid_folder'))
            return
            
        # Get scan options from UI
        recursive = self.recursive_checkbox.isChecked()
        similarity = self.similarity_slider.value()
        keep_better_quality = self.keep_better_quality_checkbox.isChecked()
        preserve_metadata = self.preserve_metadata_checkbox.isChecked()

        # Clear previous results
        self.duplicates = {}
        self.duplicates_list.clear()
        self.clear_previews()
        
        # Disable UI during processing
        self.set_ui_enabled(False)
        self.progress_bar.setValue(0)
        
        # Create and configure worker
        self.worker = ImageComparisonWorker(
            folder=folder,
            recursive=recursive,
            similarity_threshold=similarity,
            keep_better_quality=keep_better_quality,
            preserve_metadata=preserve_metadata
        )
        
        # Connect signals
        self.worker.signals.progress.connect(self._update_progress)
        self.worker.signals.finished.connect(self.on_comparison_finished)
        self.worker.signals.error.connect(self._handle_worker_error)
        
        # Start the worker in the thread pool
        self.thread_pool.start(self.worker)
        
        # Update status
        self.statusBar().showMessage(t('scanning', self.lang))
    
    def _update_progress(self, value: int):
        """Update the progress bar with the given value."""
        # Ensure we're in the main thread for UI updates
        if QThread.currentThread() != self.thread():
            QMetaObject.invokeMethod(self, "_update_progress", 
                                   Qt.ConnectionType.QueuedConnection,
                                   Q_ARG(int, value))
            return
            
        # Update progress bar with smooth animation
        self.progress_bar.setValue(value)
        
        # Update status message based on progress
        if value < 95:
            self.statusBar().showMessage(
                self.lang_manager.translate('scanning_images_progress').format(progress=value)
            )
        elif value < 100:
            self.statusBar().showMessage(
                self.lang_manager.translate('processing_duplicates')
            )
        else:
            self.statusBar().showMessage(
                self.lang_manager.translate('scan_complete')
            )
    
    def _handle_worker_error(self, msg):
        """Handle errors from the worker thread."""
        QMessageBox.critical(self, self.lang_manager.translate('error'), msg)
        self.set_ui_enabled(True)
        self.comparison_in_progress = False
    
    def on_comparison_finished(self, message, duplicates):
        """Handle the completion of the image comparison."""
        try:
            logger.info("Image comparison finished")
            self.comparison_in_progress = False
            
            # Update progress bar and status
            self.progress_bar.setValue(100)
            self.progress_label.setText(self.lang_manager.translate('comparison_complete'))
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
                    self.lang_manager.translate('no_duplicates'),
                    self.lang_manager.translate('no_duplicates_found_message')
                )
                
        except Exception as e:
            error_msg = f"Error processing comparison results: {str(e)}"
            logger.error(f"Error processing comparison results: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.lang_manager.translate('error'),
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
            self.status_bar.showMessage(self.lang_manager.translate('duplicates_found').format(count=total_duplicates))
            
        except Exception as e:
            logger.error(f"Error updating duplicates list: {e}")
            self.status_bar.showMessage(self.lang_manager.translate('error_updating_list'))
    
    def update_preview(self):
        """Update the image preview based on the current selection."""
        try:
            selected_items = self.duplicates_list.selectedItems()
            if not selected_items:
                self.clear_previews()
                return
            
            item = selected_items[0]
            item_data = item.data(Qt.ItemDataRole.UserRole)
            
            if not item_data:
                self.logger.warning("No item data found for selected item")
                self.clear_previews()
                return
                
            if not isinstance(item_data, (list, tuple)) or len(item_data) < 2:
                self.logger.warning(f"Unexpected item data format: {item_data}")
                self.clear_previews()
                return
                
            original_path = str(item_data[0])
            duplicate_path = str(item_data[1])
            
            # Verify paths exist before showing preview
            if not os.path.exists(original_path) or not os.path.exists(duplicate_path):
                self.logger.error(f"One or both image paths do not exist. Original: {original_path}, Duplicate: {duplicate_path}")
                self.clear_previews()
                return
                
            # Show preview in dialog
            self.logger.debug(f"Showing preview for images - Original: {original_path}, Duplicate: {duplicate_path}")
            self.logger.info(f"Previewing images - Original: {os.path.basename(original_path)}, Duplicate: {os.path.basename(duplicate_path)}")
            
            # Force the UI to update before showing the dialog
            QApplication.processEvents()
            
            # Import here to avoid circular imports
            from script.image_dialog_preview import show_image_preview
            show_image_preview([original_path, duplicate_path], self)
            
        except Exception as e:
            self.logger.error(f"Error in update_preview: {str(e)}", exc_info=True)
            self.clear_previews()
    
    def clear_previews(self):
        """Clear all preview widgets."""
        try:
            # No need to clear previews anymore as they're in a separate dialog
            # Just update the UI state if needed
            if hasattr(self, 'original_path') and hasattr(self.original_path, 'clear'):
                self.original_path.clear()
            if hasattr(self, 'duplicate_path') and hasattr(self.duplicate_path, 'clear'):
                self.duplicate_path.clear()
        except Exception as e:
            self.logger.error(f"Error clearing previews: {str(e)}", exc_info=True)
    
    def select_all_duplicates(self):
        """Select all items in the duplicates list."""
        self.duplicates_list.selectAll()
    
    def select_none_duplicates(self):
        """Deselect all items in the duplicates list."""
        self.duplicates_list.clearSelection()
    
    def delete_selected(self):
        """Delete the selected duplicate files with undo support using send2trash."""
        selected_items = self.duplicates_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                self.lang_manager.translate('info'),
                self.lang_manager.translate('no_items_selected')
            )
            return

        # Get the full paths of selected items - handle both tuples and strings
        selected_paths = []
        for item in selected_items:
            path_data = item.data(Qt.ItemDataRole.UserRole)
            # If it's a tuple (original, duplicate), take the duplicate path
            if isinstance(path_data, tuple) and len(path_data) == 2:
                selected_paths.append(path_data[1])  # Take the duplicate path
            else:
                selected_paths.append(str(path_data))
        
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            self.lang_manager.translate('confirm_delete'),
            self.lang_manager.translate('confirm_delete_selected', count=len(selected_paths)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Process deletions with undo support
        failed_deletions = []
        
        for i, file_path in enumerate(selected_paths):
            try:
                # Move to trash using send2trash
                trash_path = self.undo_manager.move_to_trash(file_path)
                
                # Create an operation for undo
                operation = FileOperation(
                    operation_type='delete',
                    source=file_path,  # Store original path for undo
                    metadata={'original_path': file_path}
                )
                self.undo_manager.add_operation(operation)
                
                # Update UI
                self.duplicates_list.takeItem(self.duplicates_list.row(selected_items[i]))
                
            except Exception as e:
                self.logger.error(f"Failed to move {file_path} to trash: {e}", exc_info=True)
                failed_deletions.append(file_path)
        
        # Show result message
        if failed_deletions:
            QMessageBox.warning(
                self,
                self.lang_manager.translate('error'),
                self.lang_manager.translate('failed_to_delete_files', count=len(failed_deletions))
            )
        elif selected_paths:
            QMessageBox.information(
                self,
                self.lang_manager.translate('success'),
                self.lang_manager.translate('moved_to_trash', count=len(selected_paths))
            )
            
        # Update UI
        self.update_button_states()
        self.update_preview()
    
    def delete_all_duplicates(self):
        """Delete all duplicate files, keeping only the originals using send2trash."""
        if not self.duplicates:
            QMessageBox.information(
                self,
                self.lang_manager.translate('info'),
                self.lang_manager.translate('no_duplicates_found')
            )
            return

        # Count total duplicates to delete
        total_duplicates = sum(len(dupes) for dupes in self.duplicates.values())
        if total_duplicates == 0:
            QMessageBox.information(
                self,
                self.lang_manager.translate('info'),
                self.lang_manager.translate('no_duplicates_to_delete')
            )
            return

        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            self.lang_manager.translate('confirm_delete_all'),
            self.lang_manager.translate('confirm_delete_all_duplicates', count=total_duplicates),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Process deletions with undo support
        failed_deletions = []
        deleted_count = 0
        
        try:
            # Disable UI during operation
            self.set_ui_enabled(False)
            
            # Create progress dialog
            progress = QProgressDialog(
                self.lang_manager.translate('deleting_duplicates', count=total_duplicates),
                self.lang_manager.translate('cancel'),
                0, total_duplicates, self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setWindowTitle(self.lang_manager.translate('deleting'))
            progress.setValue(0)
            progress.show()
            
            # Process each original and its duplicates
            for original, duplicates in self.duplicates.items():
                for duplicate in duplicates:
                    if progress.wasCanceled():
                        break
                        
                    try:
                        # Move to trash using send2trash
                        self.undo_manager.move_to_trash(duplicate)
                        
                        # Create an operation for undo
                        operation = FileOperation(
                            operation_type='delete',
                            source=duplicate,  # Store original path for undo
                            metadata={'original_path': duplicate}
                        )
                        self.undo_manager.add_operation(operation)
                        
                        deleted_count += 1
                        progress.setValue(deleted_count)
                        QApplication.processEvents()
                        
                    except Exception as e:
                        self.logger.error(f"Failed to move {duplicate} to trash: {e}", exc_info=True)
                        failed_deletions.append(duplicate)
                
                if progress.wasCanceled():
                    break
                    
        except Exception as e:
            self.logger.error(f"Error during bulk delete: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.lang_manager.translate('error'),
                self.lang_manager.translate('error_during_bulk_delete', error=str(e))
            )
            return
            
        finally:
            progress.close()
            self.set_ui_enabled(True)
        
        # Show result message
        if failed_deletions:
            QMessageBox.warning(
                self,
                self.lang_manager.translate('warning'),
                self.lang_manager.translate('some_deletions_failed', 
                  success=deleted_count, 
                  failed=len(failed_deletions))
            )
        elif deleted_count > 0:
            QMessageBox.information(
                self,
                self.lang_manager.translate('success'),
                self.lang_manager.translate('moved_to_trash', count=deleted_count)
            )
            
        # Update UI
        self.duplicates = {}
        self.duplicates_list.clear()
        self.original_preview.clear()
        self.duplicate_preview.clear()
        self.original_path.clear()
        self.duplicate_path.clear()
        self.update_button_states()
    
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
        dialog = HelpDialogScript(self, self.lang_manager)
        dialog.exec()
    
    def show_log_viewer(self):
        """Show the log viewer dialog."""
        dialog = LogViewer(self)  
        dialog.exec()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.lang_manager, self.config)
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
        dialog = SponsorDialog(self, self.lang_manager)
        dialog.exec()
    
    def set_language(self, lang_code):
        """
        Set the application language.
        
        Args:
            lang_code: Language code to set (e.g., 'en', 'it')
        """
        if self.lang_manager.set_language(lang_code):
            # Language was changed, no need to retranslate here as the signal will handle it
            self.logger.info(f"Language changed to: {lang_code}")
            
    def on_language_changed(self, lang_code):
        """Handle language change signal from LanguageManager."""
        self.lang = lang_code
        self.retranslate_ui()
        self.config['language'] = lang_code
        self._save_config()

    def retranslate_ui(self):
        """Retranslate all UI elements to the current language."""
        # Update window title
        self.setWindowTitle(self.lang_manager.translate('app_title', version=__version__))
        
        # Update main UI elements
        if hasattr(self, 'folder_label'):
            self.folder_label.setText(self.lang_manager.translate('select_folder'))
        if hasattr(self, 'browse_button'):
            self.browse_button.setText(self.lang_manager.translate('browse'))
        if hasattr(self, 'compare_button'):
            self.compare_button.setText(self.lang_manager.translate('compare'))
        
        # Update group boxes if they exist
        if hasattr(self, 'duplicates_group'):
            self.duplicates_group.setTitle(self.lang_manager.translate('duplicates_found'))
        if hasattr(self, 'original_group'):
            self.original_group.setTitle(self.lang_manager.translate('original_image'))
        if hasattr(self, 'duplicate_group'):
            self.duplicate_group.setTitle(self.lang_manager.translate('duplicate_image'))
        
        # Update buttons
        if hasattr(self, 'select_all_button'):
            self.select_all_button.setText(self.lang_manager.translate('select_all'))
        if hasattr(self, 'select_none_button'):
            self.select_none_button.setText(self.lang_manager.translate('select_none'))
        if hasattr(self, 'delete_selected_button'):
            self.delete_selected_button.setText(self.lang_manager.translate('delete_selected'))
        if hasattr(self, 'delete_all_button'):
            self.delete_all_button.setText(self.lang_manager.translate('delete_all_duplicates'))
        
        # Update status bar
        if hasattr(self, 'status_bar') and not self.comparison_in_progress:
            self.status_bar.showMessage(self.lang_manager.translate('ready'))
        
        # Update menu items
        if hasattr(self, 'menu_manager'):
            self.menu_manager.retranslate_ui()

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
            # Create a new UpdateChecker instance with language manager
            self.update_checker = UpdateChecker(
                __version__,
                language_manager=self.lang_manager
            )
            
            # Connect signals
            self.update_checker.update_available.connect(self._handle_update_available)
            self.update_checker.no_updates.connect(self._handle_no_updates)
            self.update_checker.error_occurred.connect(self._handle_update_error)
            
            # Connect cleanup signals
            self.update_checker.update_available.connect(self._cleanup_update_thread)
            self.update_checker.no_updates.connect(self._cleanup_update_thread)
            self.update_checker.error_occurred.connect(self._cleanup_update_thread)
            
            # Perform the check in a separate thread
            self.update_thread = QThread()
            self.update_checker.moveToThread(self.update_thread)
            
            # Connect thread signals
            self.update_thread.started.connect(self.update_checker.check_for_updates)
            
            # Start the thread
            self.update_thread.start()
            
        except Exception as e:
            logger.error(f"Error in _perform_update_check: {e}", exc_info=True)
            
    def _cleanup_update_thread(self, *args):
        """Clean up the update thread and checker."""
        try:
            if hasattr(self, 'update_thread') and self.update_thread.isRunning():
                self.update_thread.quit()
                self.update_thread.wait()
                self.update_thread.deleteLater()
            
            if hasattr(self, 'update_checker'):
                self.update_checker.deleteLater()
                
        except Exception as e:
            logger.error(f"Error cleaning up update thread: {e}", exc_info=True)

    def _handle_update_available(self, version_info):
        """Handle the case when an update is available."""
        try:
            logger.info(f"Update available: {version_info.get('version')}")
            
            # Update last check time
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            self.settings.setValue('last_update_check', today)
            
            msg = self.lang_manager.translate('update_available').format(
                current=__version__,
                latest=version_info.get('version', 'unknown')
            )
            
            # Show update dialog in a non-blocking way
            QTimer.singleShot(100, lambda: self._show_update_dialog(
                msg, 
                version_info.get('version', ''), 
                version_info.get('notes', '')
            ))
            
        except Exception as e:
            logger.error(f"Error handling update available: {e}", exc_info=True)

    def _handle_no_updates(self):
        """Handle the case when no updates are available."""
        try:
            logger.info("No updates available")
            
            # Update last check time
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            self.settings.setValue('last_update_check', today)
            
        except Exception as e:
            logger.error(f"Error handling no updates: {e}", exc_info=True)

    def _handle_update_error(self, error_message):
        """Handle errors during update check."""
        try:
            logger.error(f"Update check error: {error_message}")
            # Optionally show a message to the user
            # self.status_bar.showMessage(f"Update check failed: {error_message}")
        except Exception as e:
            logger.error(f"Error handling update error: {e}", exc_info=True)

    def check_for_updates(self, silent=False):
        """Check for application updates.
        
        Args:
            silent: If True, don't show a message when no updates are available
        """
        try:
            # Only check once per day if not forced
            last_check = self.settings.value('last_update_check')
            from datetime import datetime, timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            
            if last_check != today or True:  # Temporarily force update check for testing
                logger.info("Checking for updates...")
                try:
                    # Perform the update check immediately
                    self._perform_update_check()
                except Exception as e:
                    logger.error(f"Error performing update check: {e}", exc_info=True)
                    if not silent:
                        QMessageBox.warning(
                            self,
                            self.lang_manager.translate('error'),
                            self.lang_manager.translate('update_check_error').format(error=str(e)),
                            QMessageBox.StandardButton.Ok
                        )
            else:
                logger.info("Skipping update check - already checked today")
                if not silent:
                    QMessageBox.information(
                        self,
                        self.lang_manager.translate('no_updates_title'),
                        self.lang_manager.translate('already_checked_today'),
                        QMessageBox.StandardButton.Ok
                    )
        except Exception as e:
            logger.error(f"Error in check_for_updates: {e}", exc_info=True)
            if not silent:
                QMessageBox.critical(
                    self,
                    self.lang_manager.translate('error'),
                    f"An error occurred while checking for updates: {str(e)}",
                    QMessageBox.StandardButton.Ok
                )
    
    def undo_last_operation(self):
        """Undo the last file operation."""
        if not self.undo_manager.can_undo():
            QMessageBox.information(
                self,
                self.lang_manager.translate('info'),
                self.lang_manager.translate('edit_menu.nothing_to_undo')
            )
            return
            
        try:
            if self.undo_manager.undo_last_operation():
                # Show success message
                self.status_bar.showMessage(self.lang_manager.translate('edit_menu.undo_success'))
                
                # Update undo action state
                if self.undo_action:
                    self.undo_action.setEnabled(self.undo_manager.can_undo())
                    
                # Refresh the duplicates list
                self.compare_images()
            else:
                QMessageBox.warning(
                    self,
                    self.lang_manager.translate('error'),
                    self.lang_manager.translate('edit_menu.undo_failed', error="Unknown error")
                )
                
        except Exception as e:
            logger.error(f"Error during undo: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.lang_manager.translate('error'),
                self.lang_manager.translate('edit_menu.undo_failed', error=str(e))
            )
    
    def closeEvent(self, event):
        """
        Handle the close event to ensure proper cleanup of resources.
        
        Args:
            event: The close event
        """
        # Stop any running operations
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                self.lang_manager.translate('operation_in_progress'),
                self.lang_manager.translate('confirm_close_during_operation'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            else:
                # Try to stop the worker gracefully
                self.worker.requestInterruption()
                self.worker.wait(2000)  # Wait up to 2 seconds for clean exit
        
        # Clean up resources
        if hasattr(self, 'update_thread') and self.update_thread.isRunning():
            self.update_thread.quit()
            self.update_thread.wait()
        
        # Save window state and geometry
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Save config
        self._save_config()
        
        # Log application exit
        logger.info("Image Deduplicator shutting down")
        logger.info("=" * 50)
        
        # Accept the close event
        event.accept()

    def save_duplicates_report(self):
        """Save a report of all duplicates to a file."""
        if not self.duplicates:
            QMessageBox.information(
                self,
                self.lang_manager.translate('info'),
                self.lang_manager.translate('no_duplicates_found_message')
            )
            return
            
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.lang_manager.translate('save_report'),
            'duplicates_report.txt',
            'Text Files (*.txt);;All Files (*)'
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"=== Image Deduplicator Report ===\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total duplicate groups: {len(self.duplicates)}\n")
                f.write(f"Total duplicate files: {sum(len(dupes) for dupes in self.duplicates.values())}\n\n")
                
                # Write each group of duplicates
                for i, (original, duplicates) in enumerate(self.duplicates.items(), 1):
                    f.write(f"\n--- Group {i} ---\n")
                    f.write(f"Original: {original}\n")
                    f.write("Duplicates:\n")
                    
                    # Sort duplicates by path for consistent ordering
                    for dup in sorted(duplicates):
                        # Get file size in KB
                        size_kb = os.path.getsize(dup) / 1024
                        # Get modification time
                        mtime = datetime.fromtimestamp(os.path.getmtime(dup))
                        f.write(f"  - {dup} ({size_kb:.2f} KB, modified: {mtime})\n")
                    
            # Show success message
            self.status_bar.showMessage(self.lang_manager.translate('report_saved', path=file_path))
            logger.info(f"Saved duplicates report to {file_path}")
            
        except Exception as e:
            error_msg = self.lang_manager.translate('error_saving_report', error=str(e))
            logger.error(f"Error saving report: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.lang_manager.translate('error'),
                error_msg
            )

    def load_image_preview(self, image_path, preview_widget, path_label):
        """
        Load and display an image preview in the specified widget with enhanced error handling.
        
        Args:
            image_path: Path to the image file
            preview_widget: QLabel widget to display the image
            path_label: QLabel widget to display the path
        """
        try:
            self.logger.debug(f"Loading image preview for: {image_path}")
            
            # Validate input parameters
            if not all([image_path, preview_widget, path_label]):
                raise ValueError("Missing required parameters for image preview")
                
            # Convert to Path object if it's a string
            if isinstance(image_path, str):
                image_path = Path(image_path)
            
            # Check if file exists and is accessible
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            if not os.access(image_path, os.R_OK):
                raise PermissionError(f"No read permission for file: {image_path}")
                
            # Log basic file info
            file_size = image_path.stat().st_size / (1024 * 1024)  # Size in MB
            self.logger.debug(f"Previewing image: {image_path.name} ({file_size:.2f} MB)")
            
            # Load the image with Wand
            try:
                with WandImage(filename=str(image_path)) as img:
                    # Convert to RGB if necessary (for PNG with alpha channel)
                    if img.alpha_channel:
                        img.background_color = 'white'
                        img.alpha_channel = 'remove'
                    
                    # Convert to JPEG bytes
                    img.format = 'jpeg'
                    img.compression_quality = 85
                    
                    # Get image data as bytes and create QImage
                    img_buffer = io.BytesIO()
                    img.save(file=img_buffer)
                    qimg = QImage.fromData(img_buffer.getvalue())
                    pixmap = QPixmap.fromImage(qimg)
                    
                    # Scale the pixmap to fit the preview widget while maintaining aspect ratio
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            preview_widget.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        preview_widget.setPixmap(scaled_pixmap)
                        path_label.setText(str(image_path))
                        self.logger.debug(f"Successfully loaded preview for {image_path.name}")
                    else:
                        raise ValueError("Failed to create valid QPixmap from image")
                        
            except (IOError, ValueError) as img_error:
                self.logger.error(f"Error loading image {image_path}: {img_error}", exc_info=True)
                raise RuntimeError(f"Unsupported or corrupted image: {image_path.name}") from img_error
                
        except FileNotFoundError as e:
            error_msg = f"File not found: {e}"
            self.logger.error(error_msg)
            if hasattr(path_label, 'setText'):
                path_label.setText(error_msg)
            if hasattr(preview_widget, 'clear'):
                preview_widget.clear()
            
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            self.logger.error(error_msg)
            if hasattr(path_label, 'setText'):
                path_label.setText(error_msg)
            
        except Exception as e:
            error_msg = f"Error loading preview: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            if hasattr(path_label, 'setText'):
                path_label.setText("Error: Could not load preview")
                
            # Try to show a placeholder or clear the preview
            try:
                if hasattr(preview_widget, 'clear'):
                    preview_widget.clear()
            except Exception as cleanup_error:
                self.logger.error(f"Error during preview cleanup: {cleanup_error}", exc_info=True)

def get_theme_stylesheet():
    """Return the stylesheet for the current theme."""
    return """
    /* Progress bar */
    QProgressBar {
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        background-color: #2d2d2d;
        text-align: center;
        height: 12px;
    }
    
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 2px;
        width: 10px;
        margin: 0.5px;
    }
    
    QProgressBar:disabled {
        background-color: #2a2a2a;
    }
    
    QProgressBar::chunk:disabled {
        background-color: #2e7d32;
    }
    
    /* Progress label */
    QLabel#progressLabel {
        color: #aaaaaa;
        font-size: 11px;
        padding: 2px 0;
    }
    """
