from ast import copy_location
from PyQt6.QtWidgets import (QMenuBar, QMenu, QStatusBar, QWidget, QPushButton, QHBoxLayout)
from PyQt6.QtGui import QAction, QActionGroup, QIcon
from PyQt6.QtCore import Qt
from script.translations import t, LANGUAGES
from script.language_manager import LanguageManager  # Import LanguageManager

class MenuManager:
    """Manages the application's menu bar and menu items."""
    
    def __init__(self, parent, language_manager=None, lang='en'):
        self.parent = parent
        self.lang_manager = language_manager if language_manager else LanguageManager(default_lang=lang)
        self.lang = self.lang_manager.current_language
        self.menubar = QMenuBar()
        self.language_actions = {}  # Store language actions for easy access
        self.setup_menu_bar()
        
        # Connect language change signal if using LanguageManager
        if self.lang_manager:
            self.lang_manager.language_changed.connect(self.on_language_changed)
    
    def translate(self, key, **kwargs):
        """Helper method to get translated text."""
        if self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return t(key, self.lang, **kwargs)
    
    def on_language_changed(self, lang_code):
        """Handle language change event."""
        self.lang = lang_code
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Retranslate all menu items to the current language."""
        # Update menu titles
        self.file_menu.setTitle(self.translate('file'))
        self.edit_menu.setTitle(self.translate('edit'))
        self.lang_menu.setTitle(self.translate('language'))
        self.help_menu.setTitle(self.translate('help'))
        
        # Update file menu items
        self.action_save_report.setText(self.translate('save_report'))
        self.action_exit.setText(self.translate('exit'))
        
        # Update edit menu items
        self.action_undo.setText(self.translate('edit_menu.undo'))
        
        # Update help menu items
        self.action_about.setText(self.translate('about'))
        self.action_help.setText(self.translate('help'))
        self.action_check_updates.setText(self.translate('check_for_updates'))
        self.action_view_logs.setText(self.translate('view_logs'))
        self.action_settings.setText(self.translate('settings'))
        
        # Update language actions
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
        }
        for lang_code, action in self.language_actions.items():
            action.setText(lang_names.get(lang_code, lang_code))
        
        # Update sponsor button
        self.sponsor_button.setText("❤️ " + self.translate('sponsor'))
        
    def setup_menu_bar(self):
        """Set up the menu bar."""
        # File menu
        self.file_menu = self.menubar.addMenu(self.translate('file'))
        self.setup_file_menu()
        
        # Edit menu
        self.edit_menu = self.menubar.addMenu(self.translate('edit'))
        self.setup_edit_menu()
        
        # Language menu
        self.lang_menu = self.menubar.addMenu(self.translate('language'))
        self.setup_language_menu()
        
        # Help menu
        self.help_menu = self.menubar.addMenu(self.translate('help'))
        self.setup_help_menu()
        
        # Sponsor menu
        self.setup_sponsor_menu()
        
    def setup_file_menu(self):
        """Set up the File menu."""
        # Save Report action
        self.action_save_report = QAction(self.translate('save_report'), self.parent)
        self.action_save_report.setShortcut('Ctrl+S')
        self.action_save_report.triggered.connect(self.parent.save_duplicates_report)
        self.file_menu.addAction(self.action_save_report)
        
        # Add separator
        self.file_menu.addSeparator()
        
        # Exit action
        self.action_exit = QAction(self.translate('exit'), self.parent)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.triggered.connect(self.parent.close)
        self.file_menu.addAction(self.action_exit)
        
    def setup_edit_menu(self):
        """Set up the Edit menu."""
        # Undo action
        self.action_undo = QAction(self.translate('edit_menu.undo'), self.parent)
        self.action_undo.setShortcut('Ctrl+Z')
        self.action_undo.triggered.connect(self.parent.undo_last_operation)
        self.action_undo.setEnabled(False)  # Will be enabled when there are operations to undo
        self.edit_menu.addAction(self.action_undo)
        
        # Store a reference to the action for later enabling/disabling
        self.parent.undo_action = self.action_undo
        
    def setup_language_menu(self):
        """Set up the Language menu."""
        lang_group = QActionGroup(self.parent)
        lang_group.setExclusive(True)
        
        # Language code to name mapping
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
        }
        
        self.language_actions = {}  # Initialize the dictionary
        for lang_code in LANGUAGES:
            action = QAction(lang_names.get(lang_code, lang_code), self.parent, checkable=True)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, l=lang_code: self.parent.set_language(l))
            
            if lang_code == self.lang:
                action.setChecked(True)
                
            lang_group.addAction(action)
            self.lang_menu.addAction(action)
            self.language_actions[lang_code] = action  # Store the action
               
    def setup_help_menu(self):
        """Set up the Help menu."""
        # About action
        self.action_about = QAction(self.translate('about'), self.parent)
        self.action_about.triggered.connect(self.parent.show_about)
        self.help_menu.addAction(self.action_about)
        
        # Help action
        self.action_help = QAction(self.translate('help'), self.parent)
        self.action_help.triggered.connect(self.parent.show_help)
        self.help_menu.addAction(self.action_help)
        
        # Add separator
        self.help_menu.addSeparator()
        
        # Check for updates action
        self.action_check_updates = QAction(self.translate('check_for_updates'), self.parent)
        self.action_check_updates.triggered.connect(self.parent.check_for_updates)
        self.help_menu.addAction(self.action_check_updates)
        
        # View logs action
        self.action_view_logs = QAction(self.translate('view_logs'), self.parent)
        self.action_view_logs.triggered.connect(self.parent.show_log_viewer)
        self.help_menu.addAction(self.action_view_logs)
        
        # Add separator
        self.help_menu.addSeparator()
        
        # Settings action
        self.action_settings = QAction(self.translate('settings'), self.parent)
        self.action_settings.triggered.connect(self.parent.show_settings)
        self.help_menu.addAction(self.action_settings)
    
    def setup_sponsor_menu(self):
        """Set up the Sponsor menu item in the menu bar."""
        # Create a right-aligned widget for the sponsor button
        container = QWidget()
        container.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 10, 0)
        
        self.sponsor_button = QPushButton("❤️ " + self.translate('sponsor'), container)
        self.sponsor_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sponsor_button.clicked.connect(self.parent.show_sponsor)
        
        layout.addWidget(self.sponsor_button)
        
        # Add the container to the menu bar
        self.menubar.setCornerWidget(container)
        
    def get_menubar(self):
        """Get the menu bar."""
        return self.menubar
