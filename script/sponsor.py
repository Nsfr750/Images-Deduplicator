"""
Sponsor dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap

class SponsorDialog(QDialog):
    """Sponsor dialog with links to support the project."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle("Support the Project")
        self.setMinimumSize(600, 200)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Set application style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 12pt;
                margin: 10px 0;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 180px;
                margin: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            #closeButton {
                background-color: #6c757d;
                min-width: 120px;
            }
            #closeButton:hover {
                background-color: #5a6268;
            }
            #buttonContainer {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                border: 1px solid #dee2e6;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("❤️ Support Image Deduplicator")
        header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2c3e50;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = QLabel(
            "This application is developed and maintained by a single developer.\n"
            "Your support helps keep the project alive and allows for new features and improvements."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        
        # Button container
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QVBoxLayout(button_container)
        
        # Sponsor buttons
        buttons = [
            ("💖 Sponsor on GitHub", "https://github.com/sponsors/Nsfr750"),
            ("💬 Join Discord", "https://discord.gg/q5Pcgrju"),
            ("☕ Buy Me a Coffee", "https://paypal.me/3dmega"),
            ("🎗️ Join Patreon", "https://www.patreon.com/Nsfr750")
        ]
        
        for text, url in buttons:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=url: self.open_url(u))
            button_layout.addWidget(btn)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.accept)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(description)
        layout.addWidget(button_container, 1)
        
        # Center the close button
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(close_button)
        button_row.addStretch()
        
        layout.addLayout(button_row)
        layout.addSpacing(10)
    
    def open_url(self, url):
        """Open the specified URL in the default web browser."""
        QDesktopServices.openUrl(QUrl(url))

# For backward compatibility with Tkinter version
class Sponsor:
    def __init__(self, root):
        self.root = root
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        dialog = SponsorDialog(self.root)
        dialog.exec()
