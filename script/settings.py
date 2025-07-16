"""
Settings panel for Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider, QLabel, 
    QPushButton, QSpinBox, QDialogButtonBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt
from script.translations import t

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    def __init__(self, parent=None, lang='en', config=None):
        super().__init__(parent)
        self.lang = lang
        self.config = config or {}
        self.setWindowTitle(t('settings_title', lang))
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Appearance Group
        appearance_group = QGroupBox(t('settings_appearance', self.lang))
        appearance_layout = QVBoxLayout()
        
        # Style Selection (only Fusion is supported)
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel(t('settings_style', self.lang)))
        
        self.style_combo = QComboBox()
        self.style_combo.addItem('Fusion', 'Fusion')
        self.style_combo.setEnabled(False)  # Disable since only Fusion is supported
        
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        appearance_layout.addLayout(style_layout)
        
        # Add appearance group to layout
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Comparison Settings Group
        comparison_group = QGroupBox(t('settings_comparison', self.lang))
        comparison_layout = QVBoxLayout()
        
        # Similarity Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel(t('settings_similarity', self.lang)))
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(70, 100)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.setTickInterval(5)
        self.threshold_slider.setSingleStep(1)
        
        self.threshold_value = QLabel()
        self.threshold_value.setMinimumWidth(30)
        
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value)
        comparison_layout.addLayout(threshold_layout)
        
        # Recursive Search
        self.recursive_check = QCheckBox(t('settings_recursive', self.lang))
        comparison_layout.addWidget(self.recursive_check)
        
        # Add comparison group to layout
        comparison_group.setLayout(comparison_layout)
        layout.addWidget(comparison_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        # Connect signals
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_value.setText(f"{v}%")
        )

    def load_settings(self):
        """Load settings from config."""
        # Load style (only Fusion is supported)
        style = self.config.get('appearance', {}).get('style', 'Fusion')
        index = self.style_combo.findData(style)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        
        # Load comparison settings
        comparison = self.config.get('comparison', {})
        self.threshold_slider.setValue(comparison.get('similarity_threshold', 85))
        self.recursive_check.setChecked(comparison.get('recursive_search', True))

    def get_settings(self):
        """Get the current settings from the dialog."""
        return {
            'appearance': {
                'theme': 'dark',  # Always use dark theme
                'style': self.style_combo.currentData()
            },
            'comparison': {
                'similarity_threshold': self.threshold_slider.value(),
                'recursive_search': self.recursive_check.isChecked()
            }
        }

    def accept(self):
        """Handle dialog acceptance."""
        # Get current settings
        settings = self.get_settings()
        
        # Update config
        self.config.update(settings)
        
        # Save config if parent has save_config method
        if hasattr(self.parent(), 'save_config'):
            # Apply style (theme is always dark)
            self.parent().apply_style(settings['appearance']['style'], save=False)
            
            # Save config
            self.parent().config = self.config
            self.parent().save_config()
        
        super().accept()
