"""
Update checking functionality for the Images-Deduplicator application.
"""
import json
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl, QSize, Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout,
    QWidget, QSizePolicy, QApplication, QMessageBox, QDialogButtonBox
)
from PyQt6.QtGui import QDesktopServices, QTextCursor, QTextDocument

# Import logger and language manager
from script.logger import logger
from script.language_manager import LanguageManager
from script import version

# Get the application directory
APP_DIR = Path(__file__).parent.parent
UPDATES_FILE = APP_DIR / 'config' / 'updates.json'

# Get the current version
CURRENT_VERSION = version.__version__

class UpdateChecker(QObject):
    """Handles checking for application updates in a background thread."""
    
    update_available = pyqtSignal(dict)  # Emitted when an update is found
    no_updates = pyqtSignal()  # Emitted when no updates are available
    error_occurred = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, current_version: str, language_manager: Optional[LanguageManager] = None, config_path: Optional[Path] = None):
        """Initialize the update checker.
        
        Args:
            current_version: The current version of the application.
            language_manager: Instance of LanguageManager for translations.
            config_path: Path to the configuration file (optional).
        """
        super().__init__()
        self.current_version = current_version
        self.lang_manager = language_manager or LanguageManager()
        self.config_path = config_path or UPDATES_FILE
        self.config = self._load_config()
        self.update_url = "https://api.github.com/repos/Nsfr750/Images-Deduplicator/releases/latest"
    
    def _load_config(self) -> dict:
        """Load the update configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading update config: {e}")
        return {
            'last_checked': None,
            'last_version': None,
            'dont_ask_until': None
        }
    
    def _save_config(self) -> None:
        """Save the update configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving update config: {e}")
    
    def translate(self, key: str, **kwargs) -> str:
        """Helper method to get translated text."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return key
    
    def check_for_updates(self, force_check: bool = False) -> None:
        """Check for available updates in a background thread.
        
        Args:
            force_check: If True, skip the cache and force a check.
        """
        try:
            logger.info("Checking for updates...")
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            release = response.json()
            
            latest_version = release['tag_name'].lstrip('v')
            self.config['last_checked'] = release['published_at']
            self.config['last_version'] = latest_version
            self._save_config()
            
            if self._version_compare(latest_version, self.current_version) > 0:
                logger.info(f"Update available: {latest_version}")
                self.update_available.emit({
                    'version': latest_version,
                    'url': release['html_url'],
                    'notes': release['body'],
                    'published_at': release['published_at']
                })
            else:
                logger.info("No updates available")
                self.no_updates.emit()
                
        except requests.RequestException as e:
            error_msg = self.translate("update_check_failed", error=str(e))
            logger.error(f"Update check failed: {e}")
            self.error_occurred.emit(error_msg)
    
    @staticmethod
    def _version_compare(v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        from packaging import version as pkg_version
        try:
            v1_parsed = pkg_version.parse(v1)
            v2_parsed = pkg_version.parse(v2)
            
            if v1_parsed > v2_parsed:
                return 1
            elif v1_parsed < v2_parsed:
                return -1
            return 0
        except Exception as e:
            logger.error(f"Error comparing versions {v1} and {v2}: {e}")
            return 0


def check_for_updates(parent, current_version: str, language_manager: Optional[LanguageManager] = None, 
                     force_check: bool = False) -> None:
    """Check for application updates and show a dialog if an update is available.
    
    Args:
        parent: Parent widget for dialogs.
        current_version: Current application version.
        language_manager: Instance of LanguageManager for translations.
        force_check: If True, skip the cache and force a check.
    """
    lang_manager = language_manager or LanguageManager()
    
    def show_update_dialog(update_info):
        """Show a dialog with update information."""
        try:
            dialog = QDialog(parent)
            dialog.setWindowTitle(lang_manager.translate('update_available_title'))
            dialog.setMinimumWidth(600)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title_label = QLabel(lang_manager.translate('update_available_title'))
            title_font = title_label.font()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            # Current version
            current_version_label = QLabel(
                lang_manager.translate('current_version').format(version=current_version)
            )
            
            # New version
            new_version = update_info.get('version', 'unknown')
            new_version_label = QLabel(
                lang_manager.translate('new_version_available').format(version=new_version)
            )
            new_version_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            
            # Release notes
            release_notes_label = QLabel(lang_manager.translate('release_notes'))
            release_notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            
            # Release notes text area
            release_notes = QTextEdit()
            release_notes.setReadOnly(True)
            release_notes.setPlainText(update_info.get('notes', lang_manager.translate('no_release_notes')))
            release_notes.setMinimumHeight(150)
            
            # Buttons
            button_box = QDialogButtonBox()
            
            # Download button
            download_btn = QPushButton(lang_manager.translate('download_update'))
            download_btn.setIcon(dialog.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
            download_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(update_info.get('url', ''))))
            button_box.addButton(download_btn, QDialogButtonBox.ButtonRole.AcceptRole)
            
            # Remind me later button
            later_btn = QPushButton(lang_manager.translate('remind_later'))
            later_btn.clicked.connect(dialog.reject)
            button_box.addButton(later_btn, QDialogButtonBox.ButtonRole.RejectRole)
            
            # Add widgets to layout
            layout.addWidget(title_label)
            layout.addWidget(current_version_label)
            layout.addWidget(new_version_label)
            layout.addSpacing(10)
            layout.addWidget(release_notes_label)
            layout.addWidget(release_notes)
            layout.addSpacing(10)
            layout.addWidget(button_box)
            
            # Set dialog properties
            dialog.setLayout(layout)
            dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            
            # Show the dialog
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing update dialog: {e}", exc_info=True)
            # Fallback to simple message box
            QMessageBox.information(
                parent,
                lang_manager.translate('update_available_title'),
                lang_manager.translate('update_available').format(
                    current=current_version,
                    latest=update_info.get('version', 'unknown')
                )
            )
    
    def show_no_updates():
        """Show a message that no updates are available."""
        QMessageBox.information(
            parent,
            lang_manager.translate('no_updates_title'),
            lang_manager.translate('no_updates_message').format(version=current_version)
        )
    
    def show_error(error_msg):
        """Show an error message."""
        logger.error(f"Update check error: {error_msg}")
        QMessageBox.warning(
            parent,
            lang_manager.translate('update_error_title'),
            error_msg
        )
    
    # Create the update checker
    checker = UpdateChecker(current_version, language_manager=lang_manager)
    
    # Connect signals
    checker.update_available.connect(show_update_dialog)
    checker.no_updates.connect(show_no_updates)
    checker.error_occurred.connect(show_error)
    
    # Run the check in a separate thread
    thread = QThread()
    checker.moveToThread(thread)
    
    # Connect thread signals
    thread.started.connect(lambda: checker.check_for_updates(force_check))
    checker.update_available.connect(thread.quit)
    checker.no_updates.connect(thread.quit)
    checker.error_occurred.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    
    # Start the thread
    thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lang_manager = LanguageManager()  # Create default language manager
    check_for_updates(None, CURRENT_VERSION, lang_manager, force_check=True)
    sys.exit(app.exec())
