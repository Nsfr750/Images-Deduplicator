"""
Settings dialog for Image Deduplicator.
"""
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QCheckBox, QSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    settings_updated = pyqtSignal(dict)  # Signal emitted when settings are saved
    
    def __init__(self, parent=None, lang='en', config=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
            lang: Current language code
            config: Current configuration dictionary
        """
        super().__init__(parent)
        self.lang = lang
        self.config = config or {}
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumSize(500, 400)
        
        self.init_ui()
        self.load_settings()
    
    def tr(self, text):
        """Simple translation helper."""
        # This is a placeholder - in a real app, you'd use your translation system
        translations = {
            'Settings': {'en': 'Settings', 'it': 'Impostazioni'},
            'Language': {'en': 'Language', 'it': 'Lingua'},
            'Theme': {'en': 'Theme', 'it': 'Tema'},
            'Light': {'en': 'Light', 'it': 'Chiaro'},
            'Dark': {'en': 'Dark', 'it': 'Scuro'},
            'System': {'en': 'System', 'it': 'Sistema'},
            'Default Image Folder': {'en': 'Default Image Folder', 'it': 'Cartella Immagini Predefinita'},
            'Browse': {'en': 'Browse...', 'it': 'Sfoglia...'},
            'Save': {'en': 'Save', 'it': 'Salva'},
            'Cancel': {'en': 'Cancel', 'it': 'Annulla'},
            'Settings saved': {'en': 'Settings saved successfully', 'it': 'Impostazioni salvate con successo'},
        }
        return translations.get(text, {}).get(self.lang, text)
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Language settings
        lang_group = QGroupBox(self.tr("Language"))
        lang_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Italiano", "it")
        
        lang_layout.addRow(QLabel(self.tr("Language")), self.language_combo)
        lang_group.setLayout(lang_layout)
        
        # Theme settings
        theme_group = QGroupBox(self.tr("Theme"))
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self.tr("System"), "system")
        self.theme_combo.addItem(self.tr("Light"), "light")
        self.theme_combo.addItem(self.tr("Dark"), "dark")
        
        theme_layout.addRow(QLabel(self.tr("Theme")), self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        # Default folder settings
        folder_group = QGroupBox(self.tr("Default Image Folder"))
        folder_layout = QHBoxLayout()
        
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        browse_btn = QPushButton(self.tr("Browse..."))
        browse_btn.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_btn)
        folder_group.setLayout(folder_layout)
        
        # Add all groups to main layout
        layout.addWidget(lang_group)
        layout.addWidget(theme_group)
        layout.addWidget(folder_group)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton(self.tr("Save"))
        self.save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings into the UI."""
        # Language
        current_lang = self.config.get('language', 'en')
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # Theme
        current_theme = self.config.get('theme', 'system')
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Default folder
        default_folder = self.config.get('default_folder', '')
        self.folder_edit.setText(default_folder)
    
    def browse_folder(self):
        """Open a folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Default Image Folder"),
            self.folder_edit.text() or str(Path.home())
        )
        
        if folder:
            self.folder_edit.setText(folder)
    
    def save_settings(self):
        """Save settings and close the dialog."""
        try:
            # Get values from UI
            settings = {
                'language': self.language_combo.currentData(),
                'theme': self.theme_combo.currentData(),
                'default_folder': self.folder_edit.text()
            }
            
            # Emit signal with new settings
            self.settings_updated.emit(settings)
            
            # Show success message
            QMessageBox.information(
                self,
                self.tr("Settings"),
                self.tr("Settings saved"),
                QMessageBox.StandardButton.Ok
            )
            
            # Close the dialog
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"Error saving settings: {str(e)}"
            )
