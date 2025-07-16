"""
Settings dialog for Image Deduplicator.
Handles all application settings including UI, comparison, and quality settings.
"""
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QCheckBox, QSlider, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

from script.logger import logger

class SettingsDialog(QDialog):
    """Dialog for all application settings."""
    
    settings_updated = pyqtSignal(dict)  # Signal emitted when settings are saved
    
    def __init__(self, parent=None, lang='en', config=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.lang = lang
        self.config = config or {}
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumSize(600, 600)  # Increased height for new options
        
        # Initialize UI
        self.setup_ui()
        self.load_settings()
    
    def retranslate_ui(self):
        """Update all UI text with current translations."""
        self.setWindowTitle(self.tr("Settings"))
        
        # Appearance Group
        self.appearance_group.setTitle(self.tr("Appearance"))
        self.language_label.setText(self.tr("Language:"))
        self.theme_label.setText(self.tr("Theme:"))
        
        # Update theme combo items
        current_theme = self.theme_combo.currentData()
        self.theme_combo.clear()
        self.theme_combo.addItem(self.tr("Dark"), "dark")
        
        # Set current theme if it exists
        index = self.theme_combo.findData(current_theme or "dark")
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Comparison Group
        self.comparison_group.setTitle(self.tr("Comparison Settings"))
        self.threshold_label.setText(self.tr("Similarity Threshold:"))
        self.recursive_check.setText(self.tr("Search subdirectories"))
        self.quality_check.setText(self.tr("Keep better quality images"))
        self.quality_check.setToolTip(self.tr(
            "When enabled, keeps the highest quality image from duplicates. "
            "Quality is determined by resolution and file size."
        ))
        
        # File Handling Group
        self.file_handling_group.setTitle(self.tr("File Handling"))
        self.preserve_metadata_check.setText(self.tr("Preserve metadata when keeping best quality"))
        self.preserve_metadata_check.setToolTip(self.tr(
            "When enabled, preserves EXIF, IPTC, and XMP metadata "
            "from the original image when keeping the best quality version."
        ))
        
        # Update threshold value display
        self.update_threshold_display()
    
    def update_threshold_display(self):
        """Update the threshold percentage display."""
        self.threshold_value.setText(f"{self.threshold_slider.value()}%")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Appearance Group
        self.appearance_group = QGroupBox()
        appearance_layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        self.language_label = QLabel()
        lang_layout.addWidget(self.language_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem(self.tr("English"), "en")
        self.language_combo.addItem(self.tr("Italiano"), "it")
        lang_layout.addWidget(self.language_combo, 1)
        appearance_layout.addLayout(lang_layout)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        self.theme_label = QLabel()
        theme_layout.addWidget(self.theme_label)
        
        self.theme_combo = QComboBox()
        theme_layout.addWidget(self.theme_combo, 1)
        appearance_layout.addLayout(theme_layout)
        
        self.appearance_group.setLayout(appearance_layout)
        
        # Comparison Group
        self.comparison_group = QGroupBox()
        comparison_layout = QVBoxLayout()
        
        # Similarity threshold
        threshold_layout = QHBoxLayout()
        self.threshold_label = QLabel()
        threshold_layout.addWidget(self.threshold_label)
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(70, 100)
        self.threshold_slider.setTickInterval(5)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.valueChanged.connect(self.update_threshold_display)
        
        self.threshold_value = QLabel()
        threshold_layout.addWidget(self.threshold_slider, 1)
        threshold_layout.addWidget(self.threshold_value)
        comparison_layout.addLayout(threshold_layout)
        
        # Recursive search
        self.recursive_check = QCheckBox()
        comparison_layout.addWidget(self.recursive_check)
        
        # Keep better quality option
        self.quality_check = QCheckBox()
        comparison_layout.addWidget(self.quality_check)
        
        self.comparison_group.setLayout(comparison_layout)
        
        # File Handling Group
        self.file_handling_group = QGroupBox()
        file_handling_layout = QVBoxLayout()
        
        # Metadata preservation
        self.preserve_metadata_check = QCheckBox()
        file_handling_layout.addWidget(self.preserve_metadata_check)
        
        # Add a note about metadata support
        metadata_note = QLabel(self.tr(
            "Note: Metadata preservation is supported for JPEG, PNG, TIFF, and WebP formats."
        ))
        metadata_note.setWordWrap(True)
        metadata_note.setStyleSheet("color: #888; font-style: italic;")
        file_handling_layout.addWidget(metadata_note)
        
        self.file_handling_group.setLayout(file_handling_layout)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Add all to main layout
        layout.addWidget(self.appearance_group)
        layout.addWidget(self.comparison_group)
        layout.addWidget(self.file_handling_group)
        layout.addStretch()
        layout.addWidget(self.button_box)
        
        # Set up translations
        self.retranslate_ui()
    
    def load_settings(self):
        """Load settings from config."""
        # Appearance
        current_lang = self.config.get('language', 'en')
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        current_theme = self.config.get('theme', 'dark')
        self.theme_combo.clear()
        self.theme_combo.addItem(self.tr("Dark"), "dark")
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        # Comparison settings
        self.threshold_slider.setValue(int(self.config.get('similarity_threshold', 85)))
        self.recursive_check.setChecked(bool(self.config.get('recursive', True)))
        self.quality_check.setChecked(bool(self.config.get('keep_better_quality', True)))
        
        # File handling settings
        self.preserve_metadata_check.setChecked(bool(self.config.get('preserve_metadata', True)))
    
    def get_settings(self):
        """Get the current settings as a dictionary."""
        return {
            # Appearance
            'language': self.language_combo.currentData(),
            'theme': self.theme_combo.currentData(),
            
            # Comparison settings
            'similarity_threshold': self.threshold_slider.value(),
            'recursive': self.recursive_check.isChecked(),
            'keep_better_quality': self.quality_check.isChecked(),
            
            # File handling settings
            'preserve_metadata': self.preserve_metadata_check.isChecked(),
        }
    
    def changeEvent(self, event):
        """Handle language change events."""
        if event.type() == QEvent.Type.LocaleChange:
            self.retranslate_ui()
        super().changeEvent(event)
    
    def accept(self):
        """Handle dialog acceptance."""
        settings = self.get_settings()
        self.settings_updated.emit(settings)
        super().accept()
