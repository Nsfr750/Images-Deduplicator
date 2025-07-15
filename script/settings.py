"""
Settings panel for Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider, QLabel, 
    QPushButton, QSpinBox, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt
from script.translations import t

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    def __init__(self, parent=None, lang='en', config=None):
        super().__init__(parent)
        self.lang = lang
        self.config = config
        self.setWindowTitle(t('settings_title', lang))
        self.setMinimumSize(400, 300)
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Image Comparison Settings Group
        comparison_group = QGroupBox(t('settings_comparison', self.lang))
        comparison_layout = QVBoxLayout()
        
        # Similarity Slider
        similarity_layout = QHBoxLayout()
        self.similarity_slider = QSlider(Qt.Orientation.Horizontal)
        self.similarity_slider.setRange(1, 100)
        self.similarity_slider.setTickInterval(10)
        self.similarity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.similarity_label = QLabel()
        self.update_similarity_label()
        
        similarity_layout.addWidget(QLabel(t('settings_similarity', self.lang)))
        similarity_layout.addWidget(self.similarity_slider)
        similarity_layout.addWidget(self.similarity_label)
        
        self.similarity_slider.valueChanged.connect(self.update_similarity_label)
        
        # Recursive Search Checkbox
        self.recursive_check = QCheckBox(t('settings_recursive', self.lang))
        self.recursive_check.setChecked(True)
        
        comparison_layout.addLayout(similarity_layout)
        comparison_layout.addWidget(self.recursive_check)
        comparison_group.setLayout(comparison_layout)
        
        layout.addWidget(comparison_group)
        
        # Button Box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_similarity_label(self):
        """Update the similarity percentage label."""
        value = self.similarity_slider.value()
        self.similarity_label.setText(f"{value}%")

    def load_settings(self):
        """Load settings from config."""
        if self.config:
            comparison = self.config.get('comparison', {})
            self.similarity_slider.setValue(comparison.get('similarity_threshold', 85))
            self.recursive_check.setChecked(comparison.get('recursive_search', True))

    def accept(self):
        """Save settings and close dialog."""
        if self.config:
            comparison = self.config.get('comparison', {})
            comparison['similarity_threshold'] = self.similarity_slider.value()
            comparison['recursive_search'] = self.recursive_check.isChecked()
            self.config['comparison'] = comparison
            self.parent().save_config()
        super().accept()

    def reject(self):
        """Handle dialog reject (Cancel button)."""
        super().reject()
