"""
About dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from script.version import get_version, get_versions

class AboutDialog(QDialog):
    """About dialog showing application information and version details."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle('About Image Deduplicator')
        self.setMinimumSize(500, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # App title and version
        title = QLabel('Image Deduplicator')
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Get version information
        versions = get_versions()
        
        version_text = f"Version: {versions['app_version']}"
        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Dependencies
        deps = versions['dependencies']
        deps_text = (
            f"PyQt6: {deps['PyQt6']}\n"
            f"Pillow: {deps['Pillow']}\n"
            f"ImageHash: {deps['imagehash']}"
        )
        deps_label = QLabel(deps_text)
        deps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = QLabel(
            'A desktop application for finding and managing duplicate images\n'
            'in your folders using perceptual hashing technology.'
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Copyright
        copyright_label = QLabel(' 2025 Nsfr750')
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Close button
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.accept)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(version_label)
        layout.addWidget(deps_label)
        layout.addSpacing(20)
        layout.addWidget(description)
        layout.addStretch()
        layout.addWidget(copyright_label)
        layout.addSpacing(10)
        
        # Center the close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

# For backward compatibility with Tkinter version
class TkAbout:
    @staticmethod
    def show_about(root):
        about_dialog = QDialog(root)
        about_dialog.setWindowTitle('About Image Deduplicator')
        about_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(about_dialog)
        
        title = QLabel('Image Deduplicator')
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version = QLabel(f"Version: {get_version()}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        description = QLabel(
            'A desktop application for finding and managing\n'
            'duplicate images in your folders.'
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        copyright_label = QLabel(' 2025 Nsfr750')
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        close_button = QPushButton('Close')
        close_button.clicked.connect(about_dialog.accept)
        
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(description)
        layout.addStretch()
        layout.addWidget(copyright_label)
        layout.addSpacing(10)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        about_dialog.exec()
