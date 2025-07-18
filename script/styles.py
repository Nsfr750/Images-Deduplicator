"""
Theme and style management for the application.
"""
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

# Import the enhanced logger
from script.logger import logger

def setup_dark_theme(app):
    """Set up the dark theme palette."""
    try:
        dark_palette = QPalette()
        
        # Base colors
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        # Set disabled colors using the correct method signature
        disabled_color = QColor(127, 127, 127)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, disabled_color)
        
        app.setPalette(dark_palette)
        logger.debug("Dark theme palette applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying dark theme: {str(e)}", exc_info=True)
        raise

def get_theme_stylesheet(theme):
    """
    Get the stylesheet for the specified theme.
    
    Args:
        theme: Theme name (only 'dark' is supported)
        
    Returns:
        str: The stylesheet for the theme
    """
    if theme != 'dark':
        logger.warning(f"Theme '{theme}' is not supported. Using 'dark' theme.")
    
    return """
    /* Main window and general styling */
    QMainWindow, QDialog, QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Text and labels */
    QLabel, QCheckBox, QRadioButton, QGroupBox, QMenuBar, QMenu, QStatusBar {
        color: #ffffff;
    }
    
    /* Push buttons */
    QPushButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px 15px;
    }
    
    QPushButton:hover {
        background-color: #4a4a4a;
        border: 1px solid #777777;
    }
    
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #777777;
        border: 1px solid #3a3a3a;
    }
    
    /* Line edits and text edits */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QComboBox QAbstractItemView {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px;
    }
    
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled,
    QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
        background-color: #2a2a2a;
        color: #777777;
        border: 1px solid #3a3a3a;
    }
    
    /* Scroll bars */
    QScrollBar:vertical {
        border: none;
        background: #2b2b2b;
        width: 10px;
    }
    
    QScrollBar::handle:vertical {
        background: #3a3a3a;
        min-height: 20px;
        border-radius: 5px;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    
    /* Tabs */
    QTabBar::tab {
        background: #3a3a3a;
        color: #ffffff;
        padding: 8px 20px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        border: 1px solid #555555;
        border-bottom: none;
    }
    
    QTabBar::tab:selected {
        background: #2b2b2b;
        border-bottom: 1px solid #2b2b2b;
    }
    
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;
        border-top: none;
    }
    
    /* Group boxes */
    QGroupBox {
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 1.5em;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    
    /* Progress bar */
    QProgressBar {
        border: 1px solid #555555;
        border-radius: 4px;
        text-align: center;
        background: #2a2a2a;
    }
    
    QProgressBar::chunk {
        background-color: #2a82da;
        width: 10px;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        border: 1px solid #555555;
        height: 8px;
        background: #3a3a3a;
        margin: 2px 0;
    }
    
    QSlider::handle:horizontal {
        background: #2a82da;
        border: 1px solid #555555;
        width: 18px;
        margin: -5px 0;
        border-radius: 3px;
    }
    
    /* Checkboxes and radio buttons */
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        background: #3a3a3a;
    }
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background: #2a82da;
        border: 1px solid #2a82da;
    }
    
    /* Combo box */
    QComboBox::drop-down {
        border: none;
        background: transparent;
    }
    
    QComboBox::down-arrow {
        image: url(none);
        width: 0;
        height: 0;
        border-left: 4px solid none;
        border-right: 4px solid none;
        border-top: 5px solid #ffffff;
    }
    
    /* Menu bar */
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
        border-bottom: 1px solid #555555;
    }
    
    QMenuBar::item {
        background: transparent;
        padding: 5px 10px;
    }
    
    QMenuBar::item:selected {
        background: #3a3a3a;
    }
    
    /* Menus */
    QMenu {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
    }
    
    QMenu::item:selected {
        background-color: #2a82da;
    }
    
    /* Tool tips */
    QToolTip {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555555;
    }
    
    /* Status bar */
    QStatusBar {
        background-color: #2b2b2b;
        color: #ffffff;
        border-top: 1px solid #555555;
    }
    
    /* Scroll area */
    QScrollArea {
        border: 1px solid #555555;
    }
    
    /* Tree view */
    QTreeView {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }
    
    QTreeView::item:selected {
        background-color: #2a82da;
        color: #ffffff;
    }
    
    QTreeView::item:hover {
        background-color: #3a3a3a;
    }
    
    /* Table view */
    QTableView {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }
    
    QTableView::item:selected {
        background-color: #2a82da;
        color: #ffffff;
    }
    
    QTableView::item:hover {
        background-color: #3a3a3a;
    }
    
    /* Header view */
    QHeaderView::section {
        background-color: #3a3a3a;
        color: #ffffff;
        padding: 5px;
        border: 1px solid #555555;
    }
    
    /* Toolbar */
    QToolBar {
        background-color: #2b2b2b;
        border-bottom: 1px solid #555555;
        spacing: 3px;
    }
    
    /* Dock widget */
    QDockWidget {
        border: 1px solid #555555;
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
    }
    
    QDockWidget::title {
        text-align: left;
        padding: 5px;
        background: #3a3a3a;
    }
    
    /* Splitter */
    QSplitter::handle {
        background: #3a3a3a;
        width: 1px;
        height: 1px;
    }
    
    /* Tool button */
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 3px;
    }
    
    QToolButton:hover {
        background-color: #3a3a3a;
        border: 1px solid #555555;
    }
    
    QToolButton:pressed {
        background-color: #2a2a2a;
    }
    
    /* Spin box buttons */
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        width: 16px;
        border: 1px solid #555555;
        background: #3a3a3a;
    }
    
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
        image: url(none);
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid #ffffff;
    }
    
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
        image: url(none);
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #ffffff;
    }
    
    /* Calendar widget */
    QCalendarWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #3a3a3a;
    }
    
    QCalendarWidget QToolButton {
        background-color: transparent;
        color: #ffffff;
    }
    
    QCalendarWidget QMenu {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    
    QCalendarWidget QSpinBox {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    
    QCalendarWidget QAbstractItemView:enabled {
        color: #ffffff;
        background-color: #2b2b2b;
        selection-background-color: #2a82da;
        selection-color: #ffffff;
    }
    
    /* Message box */
    QMessageBox {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QMessageBox QLabel {
        color: #ffffff;
    }
    
    /* Input dialog */
    QInputDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* File dialog */
    QFileDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QFileDialog QLabel, QFileDialog QTreeView, QFileDialog QListView {
        color: #ffffff;
    }
    
    /* Color dialog */
    QColorDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Font dialog */
    QFontDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Print dialog */
    QPrintDialog, QPageSetupDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Progress dialog */
    QProgressDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Wizard */
    QWizard {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    /* Scroll area viewport */
    QAbstractScrollArea {
        background: #2b2b2b;
    }
    
    /* Focus rectangle */
    QWidget:focus, QMenuBar:focus {
        border: 1px solid #2a82da;
    }
    
    /* Disabled text color */
    QLabel:disabled, QCheckBox:disabled, QRadioButton:disabled, QGroupBox:disabled {
        color: #777777;
    }
    """

def apply_style(app, style_name='Fusion'):
    """
    Apply the specified style to the application.
    
    Args:
        app: QApplication instance
        style_name: Name of the style to apply (only 'Fusion' is supported)
    """
    if style_name != 'Fusion':
        logger.warning(f"Style '{style_name}' is not supported. Using 'Fusion' instead.")
    
    # Always use Fusion style
    fusion = QStyleFactory.create('Fusion')
    if fusion:
        app.setStyle(fusion)
    else:
        logger.error("Failed to create Fusion style. Using default style.")

def apply_theme(app, theme):
    """
    Apply the specified theme to the application.
    
    Args:
        app: QApplication instance
        theme: Theme name (only 'dark' is supported)
    """
    try:
        if theme.lower() == 'dark':
            setup_dark_theme(app)
            logger.info("Dark theme applied successfully")
        else:
            logger.warning(f"Unsupported theme: {theme}. Only 'dark' theme is currently supported.")
            
        # Apply the Fusion style for a more consistent look across platforms
        apply_style(app, 'Fusion')
        
    except Exception as e:
        logger.error(f"Error applying theme '{theme}': {str(e)}", exc_info=True)
        # Fall back to default theme if there's an error
        try:
            app.setStyle('Fusion')
            logger.info("Fell back to default Fusion style")
        except Exception as fallback_error:
            logger.error(f"Failed to apply fallback style: {str(fallback_error)}", exc_info=True)

def setup_styles(app):
    """
    Set up the application styles and themes.
    
    Args:
        app: QApplication instance
        
    Returns:
        dict: Default configuration for appearance settings
    """
    try:
        # Default appearance settings
        default_config = {
            'theme': 'dark',  # Default theme
            'style': 'Fusion',  # Default style
            'font_size': 10,   # Default font size
            'font_family': 'Segoe UI'  # Default font family (Windows)
        }
        
        # Set the default style
        apply_style(app, default_config['style'])
        
        # Apply the default theme
        apply_theme(app, default_config['theme'])
        
        # Set the default font
        font = app.font()
        font.setFamily(default_config['font_family'])
        font.setPointSize(default_config['font_size'])
        app.setFont(font)
        
        logger.info("Application styles initialized successfully")
        logger.debug(f"Using style: {default_config['style']}")
        logger.debug(f"Using theme: {default_config['theme']}")
        logger.debug(f"Using font: {default_config['font_family']} {default_config['font_size']}pt")
        
        return default_config
        
    except Exception as e:
        logger.error(f"Error setting up application styles: {str(e)}", exc_info=True)
        # Return default config even if there's an error
        return {
            'theme': 'dark',
            'style': 'Fusion',
            'font_size': 10,
            'font_family': 'Segoe UI'
        }
