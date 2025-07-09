from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCore import Qt

def setup_styles(app, theme='light'):
    """
    Setup application-wide styles and palette.
    
    Args:
        app: The QApplication instance
        theme: The theme to apply ('light' or 'dark')
    """
    # Set the Fusion style which looks modern on all platforms
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Create a color palette based on the selected theme
    if theme.lower() == 'dark':
        setup_dark_theme(app)
    else:
        setup_light_theme(app)

def setup_light_theme(app):
    """Set up the light theme."""
    palette = QPalette()
    
    # Base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    
    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    disabled_color = QColor(120, 120, 120)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)
    
    # Set the application palette
    app.setPalette(palette)
    
    # Set the application style sheet
    app.setStyleSheet("""
        /* Global styles */
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            color: #333333;
            background-color: #f0f0f0;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
            border-color: #999999;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QPushButton:disabled {
            color: #787878;
            background-color: #f5f5f5;
            border-color: #dddddd;
        }
        
        /* Line edits */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 5px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0078d7;
        }
        
        /* List views */
        QListView, QListWidget, QTreeView, QTreeWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 3px;
            outline: none;
        }
        
        QListView::item:selected, QListWidget::item:selected,
        QTreeView::item:selected, QTreeWidget::item:selected {
            background-color: #0078d7;
            color: #ffffff;
        }
        
        /* Tabs */
        QTabBar::tab {
            background: #e0e0e0;
            border: 1px solid #cccccc;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom-color: #ffffff;
        }
        
        /* Progress bar */
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 3px;
            text-align: center;
            background-color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            width: 10px;
        }
        
        /* Checkboxes and radio buttons */
        QCheckBox::indicator, QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        
        /* Group boxes */
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #e0e0e0;
            border-top: 1px solid #cccccc;
        }
        
        /* Tool tips */
        QToolTip {
            background-color: #ffffdc;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 5px;
            border-radius: 3px;
        }
    """)

def setup_dark_theme(app):
    """Set up the dark theme."""
    palette = QPalette()
    
    # Base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    
    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    disabled_color = QColor(127, 127, 127)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)
    
    # Set the application palette
    app.setPalette(palette)
    
    # Set the application style sheet for dark theme
    app.setStyleSheet("""
        /* Global styles */
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            color: #f0f0f0;
            background-color: #353535;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #404040;
            color: #f0f0f0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #505050;
            border-color: #777777;
        }
        
        QPushButton:pressed {
            background-color: #303030;
        }
        
        QPushButton:disabled {
            color: #7f7f7f;
            background-color: #2a2a2a;
            border-color: #3a3a3a;
        }
        
        /* Line edits */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #2a2a2a;
            color: #f0f0f0;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
            selection-background-color: #0078d7;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0078d7;
        }
        
        /* List views */
        QListView, QListWidget, QTreeView, QTreeWidget {
            background-color: #2a2a2a;
            color: #f0f0f0;
            border: 1px solid #555555;
            border-radius: 3px;
            outline: none;
        }
        
        QListView::item:selected, QListWidget::item:selected,
        QTreeView::item:selected, QTreeWidget::item:selected {
            background-color: #0078d7;
            color: #ffffff;
        }
        
        QListView::item:hover, QListWidget::item:hover,
        QTreeView::item:hover, QTreeWidget::item:hover {
            background-color: #3a3a3a;
        }
        
        /* Tabs */
        QTabBar::tab {
            background: #404040;
            color: #f0f0f0;
            border: 1px solid #555555;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #2a2a2a;
            border-bottom-color: #2a2a2a;
        }
        
        QTabBar::tab:hover {
            background: #505050;
        }
        
        /* Progress bar */
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
            background-color: #2a2a2a;
            color: #f0f0f0;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            width: 10px;
        }
        
        /* Checkboxes and radio buttons */
        QCheckBox::indicator, QRadioButton::indicator {
            width: 16px;
            height: 16px;
            background-color: #2a2a2a;
            border: 1px solid #555555;
        }
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {
            background-color: #0078d7;
            border: 1px solid #0078d7;
        }
        
        /* Group boxes */
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 15px;
            color: #f0f0f0;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #2a2a2a;
            color: #f0f0f0;
            border-top: 1px solid #555555;
        }
        
        /* Tool tips */
        QToolTip {
            background-color: #2a2a2a;
            color: #f0f0f0;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 3px;
        }
        
        /* Scroll bars */
        QScrollBar:vertical {
            border: none;
            background-color: #2a2a2a;
            width: 14px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #505050;
            min-height: 20px;
            border-radius: 2px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """)
    
    # Set the application font
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
