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
from script.language_manager import LanguageManager  # Import LanguageManager

class SettingsDialog(QDialog):
    """Dialog for all application settings."""
    
    settings_updated = pyqtSignal(dict)  # Signal emitted when settings are saved
    
    def __init__(self, parent=None, language_manager=None, config=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        # Initialize language manager
        self.lang_manager = language_manager if language_manager else LanguageManager()
        self.lang = self.lang_manager.current_language
        self.config = config or {}
        
        # Connect language changed signal
        if self.lang_manager:
            self.lang_manager.language_changed.connect(self.on_language_changed)
        
        self.setWindowTitle(self.translate("settings"))
        self.setMinimumSize(600, 600)  # Increased height for new options
        
        # Initialize UI
        self.setup_ui()
        self.load_settings()
    
    def translate(self, key, **kwargs):
        """Helper method to get translated text."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return key  # Fallback to key if no translation available
    
    def on_language_changed(self, lang_code):
        """Handle language change."""
        self.lang = lang_code
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Update all UI text with current translations."""
        self.setWindowTitle(self.translate("settings"))
        
        # Appearance Group
        self.appearance_group.setTitle(self.translate("appearance"))
        self.language_label.setText(self.translate("language") + ":")
        self.theme_label.setText(self.translate("theme") + ":")
        
        # Update theme combo items
        current_theme = self.theme_combo.currentData()
        self.theme_combo.clear()
        self.theme_combo.addItem(self.translate("dark_theme"), "dark")
        
        # Set current theme if it exists
        index = self.theme_combo.findData(current_theme or "dark")
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Comparison Group
        self.comparison_group.setTitle(self.translate("comparison_settings"))
        self.threshold_label.setText(self.translate("similarity_threshold") + ":")
        self.recursive_check.setText(self.translate("search_subdirectories"))
        self.quality_check.setText(self.translate("keep_better_quality"))
        self.quality_check.setToolTip(self.translate(
            "keep_better_quality_tooltip"
        ))
        
        # File Handling Group
        self.file_handling_group.setTitle(self.translate("file_handling"))
        self.preserve_metadata_check.setText(self.translate("preserve_metadata"))
        self.preserve_metadata_check.setToolTip(self.translate(
            "preserve_metadata_tooltip"
        ))
        
        # Update buttons
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText(self.translate("save"))
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self.translate("cancel"))
        
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
        # Add available languages from language manager if available
        if hasattr(self, 'lang_manager') and self.lang_manager:
            for lang_code, lang_name in self.lang_manager.available_languages.items():
                self.language_combo.addItem(lang_name, lang_code)
        else:
            # Fallback to default languages
            self.language_combo.addItem("English", "en")
            self.language_combo.addItem("Italiano", "it")
            
        # Set current language
        current_lang = self.lang if hasattr(self, 'lang') else 'en'
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
            
        self.language_combo.currentIndexChanged.connect(self.on_language_changed_combo)
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
        layout.addWidget(self.appearance_group)
        
        # Comparison Settings Group
        self.comparison_group = QGroupBox()
        comparison_layout = QFormLayout()
        
        # Similarity threshold slider
        threshold_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(70, 100)  # 70% to 100%
        self.threshold_slider.setValue(90)  # Default value
        self.threshold_slider.valueChanged.connect(self.update_threshold_display)
        
        self.threshold_value = QLabel("90%")
        self.threshold_value.setMinimumWidth(40)
        
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value)
        
        self.threshold_label = QLabel()
        comparison_layout.addRow(self.threshold_label, threshold_layout)
        
        # Recursive search option
        self.recursive_check = QCheckBox()
        self.recursive_check.setChecked(True)
        comparison_layout.addRow(QLabel(), self.recursive_check)
        
        # Keep better quality option
        self.quality_check = QCheckBox()
        self.quality_check.setChecked(True)
        comparison_layout.addRow(QLabel(), self.quality_check)
        
        self.comparison_group.setLayout(comparison_layout)
        layout.addWidget(self.comparison_group)
        
        # File Handling Group
        self.file_handling_group = QGroupBox()
        file_layout = QVBoxLayout()
        
        # Preserve metadata option
        self.preserve_metadata_check = QCheckBox()
        self.preserve_metadata_check.setChecked(True)
        file_layout.addWidget(self.preserve_metadata_check)
        
        self.file_handling_group.setLayout(file_layout)
        layout.addWidget(self.file_handling_group)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Initial UI translation
        self.retranslate_ui()
    
    def on_language_changed_combo(self, index):
        """Handle language change from combo box."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            lang_code = self.language_combo.currentData()
            if lang_code and lang_code != self.lang_manager.current_language:
                self.lang_manager.set_language(lang_code)
    
    def load_settings(self):
        """Load settings from config."""
        try:
            # Load language
            if 'language' in self.config:
                lang_code = self.config['language']
                index = self.language_combo.findData(lang_code)
                if index >= 0:
                    self.language_combo.setCurrentIndex(index)
            
            # Load other settings
            if 'similarity_threshold' in self.config:
                self.threshold_slider.setValue(int(self.config['similarity_threshold']))
            
            if 'recursive_search' in self.config:
                self.recursive_check.setChecked(self.config['recursive_search'])
            
            if 'keep_better_quality' in self.config:
                self.quality_check.setChecked(self.config['keep_better_quality'])
            
            if 'preserve_metadata' in self.config:
                self.preserve_metadata_check.setChecked(self.config['preserve_metadata'])
            
            if 'theme' in self.config:
                index = self.theme_combo.findData(self.config['theme'])
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
                    
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def get_settings(self):
        """Get the current settings from the dialog."""
        settings = {
            'language': self.language_combo.currentData(),
            'similarity_threshold': self.threshold_slider.value(),
            'recursive_search': self.recursive_check.isChecked(),
            'keep_better_quality': self.quality_check.isChecked(),
            'preserve_metadata': self.preserve_metadata_check.isChecked(),
            'theme': self.theme_combo.currentData()
        }
        return settings
    
    def accept(self):
        """Handle dialog accept (OK button)."""
        settings = self.get_settings()
        self.settings_updated.emit(settings)
        super().accept()
