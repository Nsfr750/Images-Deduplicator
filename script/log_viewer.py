"""
Log viewer dialog for Image Deduplicator.
"""
import os
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QTimer, QFile, QTextStream
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QFileDialog, QMessageBox, QApplication, QSizePolicy
)

# Import logger and translations from our centralized modules
from script.logger import logger
from script.translations import t

class LogViewer(QDialog):
    """A dialog for viewing application logs."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('log_viewer', self.lang))
        self.setMinimumSize(800, 600)
        
        # Create widgets
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Buttons with translations
        self.refresh_btn = QPushButton(t('refresh', self.lang))
        self.clear_btn = QPushButton(t('clear_log', self.lang))
        self.save_btn = QPushButton(t('save_as', self.lang))
        self.close_btn = QPushButton(t('close', self.lang))
        
        # Setup layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.text_edit)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.load_log_file)
        self.clear_btn.clicked.connect(self.clear_log_file)
        self.save_btn.clicked.connect(self.save_log_file)
        self.close_btn.clicked.connect(self.accept)
        
        # Load the log file
        self.load_log_file()
        
        # Set up auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_log_file)
        self.timer.start(5000)  # Refresh every 5 seconds
    
    def load_log_file(self):
        """Load the log file contents into the text edit."""
        log_file = Path("logs") / "image_dedup.log"
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
                
                # Scroll to the bottom
                self.text_edit.verticalScrollBar().setValue(
                    self.text_edit.verticalScrollBar().maximum()
                )
            else:
                self.text_edit.setPlainText(t('log_file_not_found', self.lang))
        except Exception as e:
            logger.error(f"Error loading log file: {e}")
            self.text_edit.setPlainText(t('error_loading_log', self.lang).format(error=str(e)))
    
    def clear_log_file(self):
        """Clear the log file after user confirmation."""
        reply = QMessageBox.question(
            self, 
            t('confirm_deletion', self.lang),
            t('confirm_clear_log', self.lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            log_file = Path("logs") / "image_dedup.log"
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.load_log_file()
                QMessageBox.information(
                    self,
                    t('success', self.lang),
                    t('log_cleared', self.lang)
                )
                logger.info("Log file cleared by user")
            except Exception as e:
                logger.error(f"Error clearing log file: {e}")
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('error_clearing_log', self.lang)
                )
    
    def save_log_file(self):
        """Save the current log content to a file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            t('save_log_as', self.lang),
            "",
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
            except Exception as e:
                logger.error(f"Error saving log file: {e}")
                QMessageBox.critical(
                    self,
                    t('error', self.lang),
                    t('error_saving_file', self.lang).format(error=str(e))
                )
    
    def closeEvent(self, event):
        """Handle the close event."""
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    # Example usage
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())
