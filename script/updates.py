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


class UpdateDialog(QDialog):
    """Dialog to show update information and options."""
    
    def __init__(self, update_info: Dict[str, Any], language_manager: Optional[LanguageManager] = None, parent=None):
        """Initialize the update dialog.
        
        Args:
            update_info: Dictionary containing update information.
            language_manager: Instance of LanguageManager for translations.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.update_info = update_info
        self.lang_manager = language_manager or LanguageManager()
        
        self.setWindowTitle(self.translate("update_available_title"))
        self.setMinimumSize(600, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.setup_ui()
    
    def translate(self, key: str, **kwargs) -> str:
        """Helper method to get translated text."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return key
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.translate("update_available_title"))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Version info
        version_text = self.translate(
            "update_version_info",
            current_version=CURRENT_VERSION,
            new_version=self.update_info['version']
        )
        version_label = QLabel(version_text)
        layout.addWidget(version_label)
        
        # Release notes
        notes_label = QLabel(self.translate("release_notes") + ":")
        layout.addWidget(notes_label)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(True)
        self.notes_edit.setHtml(self.update_info['notes'] or self.translate("no_release_notes"))
        layout.addWidget(self.notes_edit)
        
        # Button box
        button_box = QDialogButtonBox()
        
        # Download button
        self.download_btn = QPushButton(self.translate("download_update"))
        self.download_btn.clicked.connect(self.download_update)
        button_box.addButton(self.download_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        
        # Later button
        self.later_btn = QPushButton(self.translate("remind_later"))
        self.later_btn.clicked.connect(self.reject)
        button_box.addButton(self.later_btn, QDialogButtonBox.ButtonRole.RejectRole)
        
        # Skip this version button
        self.skip_btn = QPushButton(self.translate("skip_version"))
        self.skip_btn.clicked.connect(self.skip_version)
        button_box.addButton(self.skip_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(button_box)
    
    def download_update(self):
        """Open the download URL in the default browser and close the dialog."""
        QDesktopServices.openUrl(QUrl(self.update_info['url']))
        self.accept()
    
    def skip_version(self):
        """Skip this version and close the dialog."""
        # Here you could add logic to remember to skip this version
        self.reject()


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
        dialog = UpdateDialog(update_info, lang_manager, parent)
        dialog.exec()
    
    def show_no_updates():
        if force_check:
            QMessageBox.information(
                parent,
                lang_manager.translate("no_updates_available_title"),
                lang_manager.translate("no_updates_available_message", version=current_version)
            )
    
    def show_error(message):
        QMessageBox.warning(
            parent,
            lang_manager.translate("update_check_failed_title"),
            message
        )
    
    # Create and configure the update checker
    checker = UpdateChecker(current_version, lang_manager)
    
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
