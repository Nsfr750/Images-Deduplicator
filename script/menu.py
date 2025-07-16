from ast import copy_location
from PyQt6.QtWidgets import (QMenuBar, QMenu, QStatusBar)
from PyQt6.QtGui import QAction, QActionGroup, QIcon
from PyQt6.QtCore import Qt
from script.translations import t, LANGUAGES

class MenuManager:
    """Manages the application's menu bar and menu items."""
    
    def __init__(self, parent, lang='en'):
        self.parent = parent
        self.lang = lang
        self.menubar = QMenuBar()
        self.language_actions = {}  # Store language actions for easy access
        self.setup_menu_bar()
        
    def setup_menu_bar(self):
        """Set up the menu bar."""
        # File menu
        self.file_menu = self.menubar.addMenu(t('file', self.lang))
        self.setup_file_menu()
        
        # Language menu
        self.lang_menu = self.menubar.addMenu(t('language', self.lang))
        self.setup_language_menu()
        
        # Help menu
        self.help_menu = self.menubar.addMenu(t('help', self.lang))
        self.setup_help_menu()
        
        # Sponsor menu
        self.setup_sponsor_menu()
        
    def setup_file_menu(self):
        """Set up the File menu."""
        # Exit action
        self.action_exit = QAction(t('exit', self.lang), self.parent)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.triggered.connect(self.parent.close)
        self.file_menu.addAction(self.action_exit)
        
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
        self.action_about = QAction(t('about', self.lang), self.parent)
        self.action_about.triggered.connect(self.parent.show_about)
        self.help_menu.addAction(self.action_about)
        
        # Help action
        self.action_help = QAction(t('help', self.lang), self.parent)
        self.action_help.triggered.connect(self.parent.show_help)
        self.help_menu.addAction(self.action_help)
        
        # Settings action
        self.action_settings = QAction(t('settings', self.lang), self.parent)
        self.action_settings.triggered.connect(self.parent.show_settings)
        self.help_menu.addAction(self.action_settings)
        
        # Add separator
        self.help_menu.addSeparator()
        
        # View logs action
        self.action_view_logs = QAction(t('view_logs', self.lang), self.parent)
        self.action_view_logs.triggered.connect(self.parent.show_log_viewer)
        self.help_menu.addAction(self.action_view_logs)
        
        # Add separator
        self.help_menu.addSeparator()
        
        # Check for updates action
        self.action_check_updates = QAction(t('check_for_updates', self.lang), self.parent)
        self.action_check_updates.triggered.connect(lambda: self.parent.check_for_updates(False))
        self.help_menu.addAction(self.action_check_updates)
        
    def setup_sponsor_menu(self):
        """Set up the Sponsor menu."""
        # Create sponsor action with a heart emoji
        self.action_sponsor = QAction("❤️ " + t('sponsor', self.lang), self.parent)
        self.action_sponsor.triggered.connect(self.parent.show_sponsor)
        self.menubar.addAction(self.action_sponsor)
        
    def update_language(self, lang):
        """Update menu text when language changes."""
        self.lang = lang
        
        # Update menu titles
        self.file_menu.setTitle(t('file', self.lang))
        self.lang_menu.setTitle(t('language', self.lang))
        self.edit_menu.setTitle(t('edit', self.lang))
        self.help_menu.setTitle(t('help', self.lang))
        
        # Update menu items
        for menu in [self.file_menu, self.lang_menu, self.edit_menu, self.help_menu]:
            for action in menu.actions():
                if action.text() != "":  # Skip separators
                    action.setText(t(action.text(), self.lang))
        
        # Update sponsor action
        self.action_sponsor.setText("❤️ " + t('sponsor', self.lang))
        
        # Update language menu items
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
        }
        
        for lang_code in LANGUAGES:
            action = self.language_actions[lang_code]  # Get the action from the dictionary
            action.setText(lang_names.get(lang_code, lang_code))
            action.setChecked(lang_code == self.lang)
        
    def get_menubar(self):
        """Get the menu bar."""
        return self.menubar
