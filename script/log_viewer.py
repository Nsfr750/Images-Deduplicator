"""
Log Viewer Dialog for Image Deduplicator

This module provides a log viewer dialog that displays application logs.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QFileDialog,
    QMessageBox, QApplication, QComboBox, QGroupBox, QLabel
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QTextDocument
import os
import logging
from pathlib import Path
from datetime import datetime
from script.translations import t


class LogViewer(QDialog):
    """
    A dialog for viewing and managing application logs.
    
    Features:
    - Displays log messages with different colors based on log level
    - Filters logs by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Auto-scrolls to the latest log entry
    - Allows saving logs to a file
    - Provides controls for clearing and refreshing the log view
    """
    
    def __init__(self, parent=None, log_file=None, lang='en'):
        """
        Initialize the log viewer dialog.
        
        Args:
            parent: Parent widget
            log_file: Path to the log file to display (optional)
            lang: Language code for translations (default: 'en')
        """
        super().__init__(parent)
        self.log_file = log_file
        self.lang = lang
        self.log_content = ""
        self.level_combo = None
        self.setWindowTitle(t('log_viewer', self.lang))
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        
        # Set up a timer to periodically check for new log entries
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_logs)
        self.update_timer.start(1000)  # Check every second
        
        # Initial load
        self.refresh_logs()
    
    def setup_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_group = QGroupBox(t('filter_logs', self.lang, default="Filter Logs"))
        filter_layout = QHBoxLayout()
        
        # Create dropdown for log level filter
        self.level_combo = QComboBox(self)
        self.level_combo.addItem(t('all_levels', self.lang, default="All Levels"), "ALL")
        self.level_combo.addItem("DEBUG", "DEBUG")
        self.level_combo.addItem("INFO", "INFO")
        self.level_combo.addItem("WARNING", "WARNING")
        self.level_combo.addItem("ERROR", "ERROR")
        self.level_combo.addItem("CRITICAL", "CRITICAL")
        self.level_combo.currentIndexChanged.connect(self.on_level_changed)
        
        filter_layout.addWidget(QLabel(t('log_level', self.lang, default="Log Level:")))
        filter_layout.addWidget(self.level_combo)
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setFontFamily("Courier New")
        self.log_display.setFontPointSize(10)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton(t('refresh', self.lang, default="&Refresh"))
        self.refresh_btn.clicked.connect(self.refresh_logs)
        
        self.clear_btn = QPushButton(t('clear_logs', self.lang, default="C&lear"))
        self.clear_btn.clicked.connect(self.clear_logs)
        
        self.save_btn = QPushButton(t('save_logs', self.lang, default="&Save As..."))
        self.save_btn.clicked.connect(self.save_logs)
        
        self.close_btn = QPushButton(t('close', self.lang, default="&Close"))
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.close_btn)
        
        # Add widgets to main layout
        layout.addWidget(filter_group)
        layout.addWidget(self.log_display)
        layout.addLayout(button_layout)
    
    def on_level_changed(self, index):
        """Handle log level filter change."""
        self.update_log_display()
    
    def refresh_logs(self):
        """Refresh the log display with current log content."""
        if not self.log_file or not os.path.exists(self.log_file):
            self.log_display.setPlainText(t('no_log_file', self.lang))
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
                
            if new_content != self.log_content:
                self.log_content = new_content
                self.update_log_display()
                
        except Exception as e:
            self.log_display.setPlainText(
                t('error_reading_log', self.lang).format(error=str(e))
            )
    
    def update_log_display(self):
        """Update the log display with filtered and formatted content."""
        if not hasattr(self, 'log_display') or not hasattr(self, 'level_combo'):
            return
            
        # Save scrollbar position
        scrollbar = self.log_display.verticalScrollBar()
        was_at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # Get selected log level
        selected_level = self.level_combo.currentData()
        if selected_level == "ALL":
            selected_level = None
            
        # Clear and update content
        self.log_display.clear()
        
        # Set up text formats for different log levels
        format_info = QTextCharFormat()
        format_info.setForeground(QColor(0, 0, 0))  # Black for INFO
        
        format_warning = QTextCharFormat()
        format_warning.setForeground(QColor(200, 120, 0))  # Orange for WARNING
        
        format_error = QTextCharFormat()
        format_error.setForeground(QColor(200, 0, 0))  # Red for ERROR/CRITICAL
        
        format_debug = QTextCharFormat()
        format_debug.setForeground(QColor(100, 100, 100))  # Gray for DEBUG
        
        # Process each line and apply formatting
        cursor = self.log_display.textCursor()
        
        for line in self.log_content.splitlines():
            if not line.strip():
                continue
                
            # Add newline for proper formatting
            line = line + '\n'
            
            # Get log level from line
            log_level = None
            if ' - CRITICAL - ' in line:
                log_level = 'CRITICAL'
            elif ' - ERROR - ' in line:
                log_level = 'ERROR'
            elif ' - WARNING - ' in line:
                log_level = 'WARNING'
            elif ' - INFO - ' in line:
                log_level = 'INFO'
            elif ' - DEBUG - ' in line:
                log_level = 'DEBUG'
            
            # Skip line if it doesn't match selected level
            if selected_level and log_level != selected_level:
                continue
            
            # Apply appropriate format based on log level
            if log_level in ['ERROR', 'CRITICAL']:
                cursor.insertText(line, format_error)
            elif log_level == 'WARNING':
                cursor.insertText(line, format_warning)
            elif log_level == 'DEBUG':
                cursor.insertText(line, format_debug)
            else:  # INFO
                cursor.insertText(line, format_info)
        
        # Restore scroll position or scroll to bottom if previously at bottom
        if was_at_bottom:
            self.log_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_logs(self):
        """Clear the log file after user confirmation."""
        if not self.log_file or not os.path.exists(self.log_file):
            return
            
        reply = QMessageBox.question(
            self,
            t('clear_logs', self.lang),
            t('confirm_clear_logs', self.lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.refresh_logs()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    t('error', self.lang, default="Error"),
                    t('failed_clear_logs', self.lang, default="Failed to clear log file: {error}").format(error=str(e))
                )
    
    def save_logs(self):
        """Save the current log content to a file."""
        if not self.log_content:
            QMessageBox.information(
                self,
                t('information', self.lang, default="Information"),
                t('no_logs_to_save', self.lang, default="No log content to save.")
            )
            return
        
        # Suggest a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"image_dedup_log_{timestamp}.log"
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t('save_log_file', self.lang, default="Save Log File"),
            default_filename,
            t('log_files', self.lang, default="Log Files (*.log);;All Files (*)")
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_content)
                
                QMessageBox.information(
                    self,
                    t('success', self.lang, default="Success"),
                    t('logs_saved', self.lang).format(path=file_path)
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    t('error', self.lang, default="Error"),
                    t('failed_save_logs', self.lang).format(error=str(e))
                )
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop the update timer
        self.update_timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    # Example usage
    import sys
    
    app = QApplication(sys.argv)
    
    # For testing, you can pass a log file path
    log_file = "image_dedup.log"  # Replace with actual log file path
    
    viewer = LogViewer(log_file=log_file)
    viewer.show()
    
    sys.exit(app.exec())
