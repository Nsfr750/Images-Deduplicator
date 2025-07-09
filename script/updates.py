"""
Update checking functionality for the Images-Deduplicator application.
"""
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl, QSize, Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout,
    QWidget, QSizePolicy, QApplication, QMessageBox
)
from PyQt6.QtGui import QDesktopServices, QTextCursor

# Get the application directory
APP_DIR = Path(__file__).parent.parent
UPDATES_FILE = APP_DIR / 'updates.json'

# Configure logging
logger = logging.getLogger(__name__)

from script import translations, version

# Get the current version
CURRENT_VERSION = version.__version__

class UpdateChecker(QObject):
    """Handles checking for application updates in a background thread."""
    
    update_available = pyqtSignal(dict)  # Emitted when an update is found
    no_updates = pyqtSignal()  # Emitted when no updates are available
    error_occurred = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, current_version: str, config_path: Optional[Path] = None):
        """Initialize the update checker.
        
        Args:
            current_version: The current version of the application.
            config_path: Path to the configuration file (optional).
        """
        super().__init__()
        self.current_version = current_version
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
            error_msg = f"Failed to check for updates: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v: str) -> list:
            return [int(x) for x in v.split('.')]
            
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            # Pad with zeros if versions have different lengths
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
            
        except (ValueError, AttributeError):
            # Fallback to string comparison if version format is invalid
            return (v1 > v2) - (v1 < v2)


class UpdateDialog(QDialog):
    """Dialog to show update information and options."""
    
    def __init__(self, update_info: Dict[str, Any], parent=None):
        """Initialize the update dialog.
        
        Args:
            update_info: Dictionary containing update information.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle("Update Available")
        self.setMinimumSize(600, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"New Version {self.update_info['version']} is available!")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(self.update_info['notes'])
        
        # Move cursor to the top
        cursor = notes_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        notes_text.setTextCursor(cursor)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Download Now")
        download_btn.clicked.connect(self.download_update)
        
        later_btn = QPushButton("Remind Me Later")
        later_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(download_btn)
        button_layout.addWidget(later_btn)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(notes_label)
        layout.addWidget(notes_text, 1)
        layout.addLayout(button_layout)
    
    def download_update(self):
        """Open the download URL in the default browser and close the dialog."""
        QDesktopServices.openUrl(QUrl(self.update_info['url']))
        self.accept()


def check_for_updates(parent, current_version: str, force_check: bool = False) -> None:
    """Check for application updates and show a dialog if an update is available.
    
    Args:
        parent: Parent widget for dialogs.
        current_version: Current application version.
        force_check: If True, skip the cache and force a check.
    """
    # Create a worker thread for the update check
    class UpdateWorker(QObject):
        finished = pyqtSignal()
        
        def __init__(self, current_version):
            super().__init__()
            self.checker = UpdateChecker(current_version)
        
        def run(self):
            try:
                self.checker.check_for_updates(force_check)
            finally:
                self.finished.emit()
    
    # Create and configure the worker
    worker = UpdateWorker(current_version)
    worker_thread = QThread()
    
    # Move worker to the thread
    worker.moveToThread(worker_thread)
    
    # Connect signals
    worker_thread.started.connect(worker.run)
    worker.finished.connect(worker_thread.quit)
    worker.finished.connect(worker.deleteLater)
    worker_thread.finished.connect(worker_thread.deleteLater)
    
    # Connect update checker signals
    def show_update_dialog(update_info):
        dialog = UpdateDialog(update_info, parent)
        dialog.exec()
    
    def show_no_updates():
        QMessageBox.information(
            parent,
            "No Updates",
            "You are using the latest version.",
            QMessageBox.StandardButton.Ok
        )
    
    def show_error(error_msg):
        QMessageBox.warning(
            parent,
            "Update Error",
            error_msg,
            QMessageBox.StandardButton.Ok
        )
    
    worker.checker.update_available.connect(show_update_dialog)
    worker.checker.no_updates.connect(show_no_updates)
    worker.checker.error_occurred.connect(show_error)
    
    # Start the thread
    worker_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    check_for_updates(None, CURRENT_VERSION)
    sys.exit(app.exec())
