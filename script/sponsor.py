"""
Sponsor dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap, QPalette, QColor

class SponsorDialog(QDialog):
    """Sponsor dialog with links to support the project."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle("Support the Project")
        self.setMinimumSize(600, 200)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Apply Fusion style
        QApplication.setStyle("Fusion")
        
        # Create dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        # Apply the palette
        self.setPalette(dark_palette)
        
        # Set application style
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 12pt;
                margin: 10px 0;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 12px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 180px;
                margin: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #777;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            #closeButton {
                background-color: #3a3a3a;
                min-width: 120px;
            }
            #closeButton:hover {
                background-color: #4a4a4a;
            }
            #buttonContainer {
                background-color: #353535;
                border-radius: 6px;
                padding: 15px;
                margin: 10px;
                border: 1px solid #444;
            }
            #headerLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #4a9cff;
                padding: 10px;
                border-bottom: 1px solid #444;
                margin-bottom: 15px;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("❤️ Support Image Deduplicator")
        header.setObjectName("headerLabel")
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
        button_layout.setSpacing(10)
        
        # Sponsor buttons with icons and colors
        buttons = [
            ("💖 Sponsor on GitHub", "https://github.com/sponsors/Nsfr750", "#2d2d2d"),
            ("💬 Join Discord", "https://discord.gg/q5Pcgrju", "#5865F2"),
            ("☕ Buy Me a Coffee", "https://paypal.me/3dmega", "#FFDD00"),
            ("🎗️ Join Patreon", "https://www.patreon.com/Nsfr750", "#FF424D")
        ]
        
        for text, url, color in buttons:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'#000000' if color == '#FFDD00' else '#ffffff'};
                    border: 1px solid {color};
                    padding: 10px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: transparent;
                    color: {color};
                }}
            """)
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
