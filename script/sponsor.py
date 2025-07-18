"""
Sponsor dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, 
    QWidget, QSizePolicy, QApplication, QGridLayout, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QPixmap, QPalette, QColor, QIcon

from script.language_manager import LanguageManager
from typing import Optional

class SponsorDialog(QDialog):
    """Sponsor dialog with links to support the project."""
    
    def __init__(self, parent=None, language_manager: Optional[LanguageManager] = None):
        super().__init__(parent)
        
        # Initialize language manager
        self.lang_manager = language_manager or LanguageManager()
        
        # Connect language changed signal
        if self.lang_manager:
            self.lang_manager.language_changed.connect(self.on_language_changed)
        
        self.setWindowTitle(self.translate("support_project"))
        self.setMinimumSize(700, 350)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Initialize UI
        self.setup_ui()
    
    def translate(self, key: str, **kwargs) -> str:
        """Helper method to get translated text."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return key
    
    def on_language_changed(self, lang_code: str) -> None:
        """Handle language change."""
        self.retranslate_ui()
    
    def retranslate_ui(self) -> None:
        """Retranslate the UI elements."""
        self.setWindowTitle(self.translate("support_project"))
        self.header_label.setText(self.translate("support_project_header"))
        self.description_label.setText(self.translate("support_project_description"))
        
        # Update buttons
        self.patreon_btn.setText(self.translate("support_on_patreon"))
        self.paypal_btn.setText(self.translate("donate_via_paypal"))
        self.buymeacoffee_btn.setText(self.translate("buy_me_coffee"))
        self.bitcoin_btn.setText(self.translate("bitcoin_donation"))
        self.ethereum_btn.setText(self.translate("ethereum_donation"))
        self.close_btn.setText(self.translate("close"))
    
    def apply_dark_theme(self):
        """Apply dark theme to the dialog."""
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
                min-width: 200px;
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
                margin-top: 20px;
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
                font-size: 18pt;
                font-weight: bold;
                color: #4a9cff;
                padding: 10px;
                text-align: center;
                margin-bottom: 15px;
            }
            #descriptionLabel {
                text-align: center;
                margin-bottom: 20px;
                padding: 0 20px;
            }
        """)
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel()
        self.header_label.setObjectName("headerLabel")
        
        # Description
        self.description_label = QLabel()
        self.description_label.setObjectName("descriptionLabel")
        self.description_label.setWordWrap(True)
        
        # Buttons container
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QGridLayout(button_container)
        
        # Support buttons
        self.patreon_btn = QPushButton()
        self.patreon_btn.setIcon(QIcon(":/icons/patreon.png"))
        self.patreon_btn.clicked.connect(lambda: self.open_url("https://www.patreon.com/Nsfr750"))
        
        self.paypal_btn = QPushButton()
        self.paypal_btn.setIcon(QIcon(":/icons/paypal.png"))
        self.paypal_btn.clicked.connect(lambda: self.open_url("https://www.paypal.me/3dmega"))
        
        self.buymeacoffee_btn = QPushButton()
        self.buymeacoffee_btn.setIcon(QIcon(":/icons/coffee.png"))
        self.buymeacoffee_btn.clicked.connect(lambda: self.open_url("https://www.buymeacoffee.com/nsfr750"))
        
        self.bitcoin_btn = QPushButton()
        self.bitcoin_btn.setIcon(QIcon(":/icons/bitcoin.png"))
        self.bitcoin_btn.clicked.connect(lambda: self.show_address("Bitcoin", "bc1q..."))
        
        self.ethereum_btn = QPushButton()
        self.ethereum_btn.setIcon(QIcon(":/icons/ethereum.png"))
        self.ethereum_btn.clicked.connect(lambda: self.show_address("Ethereum", "0x..."))
        
        # Add buttons to layout
        button_layout.addWidget(self.patreon_btn, 0, 0)
        button_layout.addWidget(self.paypal_btn, 0, 1)
        button_layout.addWidget(self.buymeacoffee_btn, 0, 2)
        button_layout.addWidget(self.bitcoin_btn, 1, 0, 1, 3)
        button_layout.addWidget(self.ethereum_btn, 2, 0, 1, 3)
        
        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.accept)
        
        # Add widgets to main layout
        layout.addWidget(self.header_label)
        layout.addWidget(self.description_label)
        layout.addWidget(button_container, 1)
        layout.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Set initial translations
        self.retranslate_ui()
    
    def open_url(self, url: str) -> None:
        """Open a URL in the default browser."""
        QDesktopServices.openUrl(QUrl(url))
    
    def show_address(self, currency: str, address: str) -> None:
        """Show cryptocurrency address with copy option."""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self,
            self.translate("copy_address"),
            f"{currency} {self.translate('address')}:",
            text=address
        )
        
        if ok and text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(
                self,
                self.translate("address_copied"),
                f"{currency} {self.translate('address_copied_to_clipboard')}"
            )


# For backward compatibility with Tkinter version
class Sponsor:
    def __init__(self, root):
        self.root = root
    
    def show_sponsor(self):
        """Show the sponsor dialog."""
        dialog = SponsorDialog()
        dialog.exec()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create a default language manager for testing
    lang_manager = LanguageManager()
    
    # Create and show the sponsor dialog
    dialog = SponsorDialog(language_manager=lang_manager)
    dialog.show()
    
    sys.exit(app.exec())
