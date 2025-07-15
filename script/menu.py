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
        self.setup_menu_bar()
        
    def setup_menu_bar(self):
        """Set up the menu bar."""
        # File menu
        self.file_menu = self.menubar.addMenu(t('file', self.lang))
        self.setup_file_menu()
        
        # Language menu
        self.lang_menu = self.menubar.addMenu(t('language', self.lang))
        self.setup_language_menu()
        
        # Edit menu
        self.edit_menu = self.menubar.addMenu(t('edit', self.lang))
        self.setup_edit_menu()
        
        # Help menu
        self.help_menu = self.menubar.addMenu(t('help', self.lang))
        self.setup_help_menu()
        
        # Sponsor menu
        self.setup_sponsor_menu()
        
    def setup_file_menu(self):
        """Set up the File menu."""
        # Exit action
        exit_action = QAction(t('exit', self.lang), self.parent)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.parent.close)
        self.file_menu.addAction(exit_action)
        
    def setup_language_menu(self):
        """Set up the Language menu."""
        lang_group = QActionGroup(self.parent)
        lang_group.setExclusive(True)
        
        # Language code to name mapping
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
            'es': 'Español',
            'pt': 'Português',
            'fr': 'Français',
            'de': 'Deutsch',
        }
        
        for lang_code in LANGUAGES:
            action = QAction(lang_names.get(lang_code, lang_code), self.parent, checkable=True)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, l=lang_code: self.parent.set_language(l))
            
            if lang_code == self.lang:
                action.setChecked(True)
                
            lang_group.addAction(action)
            self.lang_menu.addAction(action)
            
    def setup_edit_menu(self):
        """Set up the Edit menu."""
        self.settings_action = QAction(t('settings', self.lang), self.parent)
        self.settings_action.triggered.connect(self.parent.show_settings)
        self.edit_menu.addAction(self.settings_action)
        
    def setup_help_menu(self):
        """Set up the Help menu."""
        # About action
        about_action = QAction(t('about', self.lang), self.parent)
        about_action.triggered.connect(self.parent.show_about)
        self.help_menu.addAction(about_action)
        
        # Help action
        help_action = QAction(t('help', self.lang) + '...', self.parent)
        help_action.triggered.connect(self.parent.show_help)
        self.help_menu.addAction(help_action)
        
        # View Logs action
        view_logs_action = QAction(t('view_logs', self.lang, default="View Logs"), self.parent)
        view_logs_action.triggered.connect(self.parent.show_log_viewer)
        self.help_menu.addAction(view_logs_action)
        
        # Add separator
        self.help_menu.addSeparator()
        
        # Check for updates action
        update_action = QAction(t('check_for_updates', self.lang), self.parent)
        update_action.triggered.connect(self.parent.check_for_updates)
        self.help_menu.addAction(update_action)
        
    def setup_sponsor_menu(self):
        """Set up the Sponsor menu."""
        # Create sponsor action with a heart emoji
        self.sponsor_action = QAction("❤️ " + t('sponsor', self.lang), self.parent)
        self.sponsor_action.triggered.connect(self.parent.show_sponsor)
        self.menubar.addAction(self.sponsor_action)
        
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
        self.sponsor_action.setText("❤️ " + t('sponsor', self.lang))
        
        # Update language menu items
        lang_names = {
            'en': 'English',
            'it': 'Italiano',
            'es': 'Español',
            'pt': 'Português',
            'fr': 'Français',
            'de': 'Deutsch',
        }
        
        for action in self.lang_menu.actions():
            lang_code = action.data()
            action.setText(lang_names.get(lang_code, lang_code))
            action.setChecked(lang_code == self.lang)
        
    def get_menubar(self):
        """Get the menu bar."""
        return self.menubar
