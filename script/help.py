"""
Help dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QTabWidget, QWidget,
    QHBoxLayout, QFrame, QScrollArea, QSizePolicy, QComboBox, QLineEdit,
    QGroupBox, QGridLayout, QToolButton, QStyle, QMenu
)
from PyQt6.QtCore import Qt, QSize, QEvent, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QDesktopServices, QAction

from script.translations import t, LANGUAGES
from script.version import get_version, __version__
from script.language_manager import LanguageManager  # Import LanguageManager

import re
from difflib import SequenceMatcher

class HelpDialog(QDialog):
    """Help dialog showing usage information and language selection."""
    
    # Signal for language change
    language_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, language_manager=None, lang='en'):
        super().__init__(parent)
        
        # Initialize language manager
        self.lang_manager = language_manager if language_manager else LanguageManager(default_lang=lang)
        self.lang = self.lang_manager.current_language
        
        # Connect language changed signal
        if self.lang_manager:
            self.lang_manager.language_changed.connect(self.on_language_changed)
            
        self.setWindowTitle(self.translate('help'))
        self.setMinimumSize(800, 600)
        
        # Search state
        self.search_history = []
        self.search_options = {
            'case_sensitive': False,
            'whole_words': False,
            'highlight': True,
            'fuzzy': False
        }
        
        # Timer for debouncing search
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)  # 300ms debounce
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        # Set application style
        self.setup_ui()
        
    def translate(self, key, **kwargs):
        """Helper method to get translated text."""
        if hasattr(self, 'lang_manager') and self.lang_manager:
            return self.lang_manager.translate(key, **kwargs)
        return t(key, self.lang, **kwargs)
    
    def on_language_changed(self, lang_code):
        """Handle language change."""
        self.lang = lang_code
        self.retranslate_ui()
        
    def retranslate_ui(self):
        """Retranslate the UI elements."""
        self.setWindowTitle(self.translate('help'))
        self.tabs.setTabText(0, self.translate('usage'))
        self.tabs.setTabText(1, self.translate('help_features'))
        self.tabs.setTabText(2, self.translate('help_tips'))
        
        # Update buttons
        self.close_button.setText(self.translate('help_close'))
        
        # Update search UI
        self.search_input.setPlaceholderText(self.translate('search_help'))
        self.case_sensitive_action.setText(self.translate('search_case_sensitive'))
        self.whole_words_action.setText(self.translate('search_whole_words'))
        self.highlight_action.setText(self.translate('search_highlight'))
        self.fuzzy_action.setText(self.translate('search_fuzzy'))
        
        # Update content
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with search and language selection
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_icon = QToolButton()
        search_icon.setText("🔍")
        search_icon.setFixedWidth(30)
        search_icon.setStyleSheet("QToolButton { padding: 0; }")
        
        # Search input with history
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translate('search_help'))
        self.search_input.textChanged.connect(self.search_text_changed)
        self.search_input.setVisible(True)  # Ensure search input is visible
        
        # Search history dropdown
        self.search_history_combo = QComboBox()
        self.search_history_combo.setEditable(True)
        self.search_history_combo.setFixedWidth(200)
        self.search_history_combo.activated.connect(self.history_selected)
        self.search_history_combo.setVisible(True)  # Ensure combo box is visible
        
        # Search options button
        self.search_options_button = QToolButton()
        self.search_options_button.setText("⚙️")
        self.search_options_button.setObjectName("searchOptionsButton")
        self.search_options_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.search_options_button.setMenu(self.create_search_options_menu())
        self.search_options_button.setVisible(True)  # Ensure options button is visible
        
        # Clear search button
        self.clear_search_button = QPushButton("×")
        self.clear_search_button.setObjectName("clearSearchButton")
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setVisible(True)  # Ensure clear button is visible
        
        # Match count label
        self.match_count_label = QLabel()
        self.match_count_label.setObjectName("matchCount")
        self.match_count_label.setVisible(True)  # Ensure match count is visible
        
        # Add search components to layout
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_history_combo)
        search_layout.addWidget(self.search_options_button)
        search_layout.addWidget(self.match_count_label)
        search_layout.addWidget(self.clear_search_button)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lang_label = QLabel(self.translate('language') + ":")
        
        # Create language buttons
        self.english_button = QPushButton("English")
        self.english_button.setCheckable(True)
        self.english_button.setChecked(self.lang == 'en')
        self.english_button.clicked.connect(lambda: self.change_language('en'))
        
        self.italian_button = QPushButton("Italiano")
        self.italian_button.setCheckable(True)
        self.italian_button.setChecked(self.lang == 'it')
        self.italian_button.clicked.connect(lambda: self.change_language('it'))
        
        # Style the active button
        button_style = """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #444;
                padding: 5px 12px;
                border-radius: 4px;
                margin: 0 2px;
            }
            QPushButton:checked {
                background-color: #357abd;
                border-color: #2c6599;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """
        self.english_button.setStyleSheet(button_style)
        self.italian_button.setStyleSheet(button_style)
        
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.english_button)
        lang_layout.addWidget(self.italian_button)
        lang_layout.addStretch()
        
        # Add search layout to header
        header_layout.addLayout(search_layout)
        header_layout.addStretch()
        header_layout.addLayout(lang_layout)
        header_frame.setVisible(True)  # Ensure header frame is visible
        
        # Add header to main layout
        main_layout.addWidget(header_frame)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.usage_tab = QWidget()
        self.features_tab = QWidget()
        self.tips_tab = QWidget()
        
        self.tabs.addTab(self.usage_tab, self.translate('usage'))
        self.tabs.addTab(self.features_tab, self.translate('help_features'))
        self.tabs.addTab(self.tips_tab, self.translate('help_tips'))
        
        # Setup tab contents
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
        
        # Close button
        self.close_button = QPushButton(self.translate('help_close'))
        self.close_button.clicked.connect(self.accept)
        self.close_button.setFixedWidth(100)
        
        # Add widgets to layout
        main_layout.addWidget(self.tabs, 1)
        
        # Center the close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Set tab order
        self.setTabOrder(self.search_input, self.english_button)
        self.setTabOrder(self.english_button, self.italian_button)
        self.setTabOrder(self.italian_button, self.tabs)
        self.setTabOrder(self.tabs, self.close_button)
    
    def create_search_options_menu(self):
        """Create the search options menu."""
        menu = QMenu()
        
        # Case sensitivity
        self.case_sensitive_action = QAction(self.translate('search_case_sensitive'), self)
        self.case_sensitive_action.setCheckable(True)
        self.case_sensitive_action.setChecked(self.search_options['case_sensitive'])
        self.case_sensitive_action.triggered.connect(self.update_search_options)
        menu.addAction(self.case_sensitive_action)
        
        # Whole words
        self.whole_words_action = QAction(self.translate('search_whole_words'), self)
        self.whole_words_action.setCheckable(True)
        self.whole_words_action.setChecked(self.search_options['whole_words'])
        self.whole_words_action.triggered.connect(self.update_search_options)
        menu.addAction(self.whole_words_action)
        
        # Highlight
        self.highlight_action = QAction(self.translate('search_highlight'), self)
        self.highlight_action.setCheckable(True)
        self.highlight_action.setChecked(self.search_options['highlight'])
        self.highlight_action.triggered.connect(self.update_search_options)
        menu.addAction(self.highlight_action)
        
        # Fuzzy matching
        self.fuzzy_action = QAction(self.translate('search_fuzzy'), self)
        self.fuzzy_action.setCheckable(True)
        self.fuzzy_action.setChecked(self.search_options['fuzzy'])
        self.fuzzy_action.triggered.connect(self.update_search_options)
        menu.addAction(self.fuzzy_action)
        
        return menu
    
    def update_search_options(self):
        """Update search options when user changes them."""
        self.search_options['case_sensitive'] = self.case_sensitive_action.isChecked()
        self.search_options['whole_words'] = self.whole_words_action.isChecked()
        self.search_options['highlight'] = self.highlight_action.isChecked()
        self.search_options['fuzzy'] = self.fuzzy_action.isChecked()
        
        # Re-perform search with new options
        search_text = self.search_input.text()
        if search_text:
            self.perform_search()
    
    def search_text_changed(self, text):
        """Handle search text changes."""
        # Start timer for debounced search
        self.search_timer.start()
    
    def perform_search(self):
        """Perform the actual search with current options."""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
            
        # Add to history
        if search_text not in self.search_history:
            self.search_history.insert(0, search_text)
            self.search_history_combo.clear()
            self.search_history_combo.addItems(self.search_history[:10])
            self.search_history_combo.setCurrentText(search_text)
        
        # Update match count
        matches = self.find_matches(search_text)
        self.match_count_label.setText(f"{len(matches)} {self.translate('matches')}")
        
        # Perform actual search
        self.filter_content(search_text)
    
    def find_matches(self, search_text):
        """Find matches in current tab content based on search options."""
        # Split search terms
        terms = [term.strip() for term in search_text.split(',') if term.strip()]
        
        # Get current tab content
        current_tab = self.tabs.currentIndex()
        content = self.get_original_content(current_tab)
        
        # Initialize matches list
        matches = []
        
        # Process each search term
        for term in terms:
            if self.search_options['case_sensitive']:
                search_term = term
                content_text = content
            else:
                search_term = term.lower()
                content_text = content.lower()
            
            # Find matches based on options
            if self.search_options['whole_words']:
                # Match whole words only
                pattern = r'\b' + re.escape(search_term) + r'\b'
                matches.extend(re.finditer(pattern, content_text))
            else:
                # Regular search
                if self.search_options['fuzzy']:
                    # Fuzzy matching
                    words = content_text.split()
                    for word in words:
                        ratio = SequenceMatcher(None, word, search_term).ratio()
                        if ratio > 0.7:  # 70% similarity threshold
                            matches.append(word)
                else:
                    # Exact match
                    matches.extend(content_text.find(search_term))
        
        return matches
    
    def history_selected(self, index):
        """Handle selection from search history."""
        if index >= 0:
            self.search_input.setText(self.search_history_combo.itemText(index))
            self.perform_search()
    
    def clear_search(self):
        """Clear the search."""
        self.search_input.clear()
        self.search_history_combo.setCurrentIndex(-1)
        self.match_count_label.clear()
        self.clear_search_highlights()
    
    def filter_content(self, search_text):
        """Filter content based on search text."""
        search_text = search_text.lower()
        
        # Get current tab index
        current_tab = self.tabs.currentIndex()
        
        # Clear previous search highlights
        self.clear_search_highlights()
        
        if not search_text:
            return
            
        # Get the current tab's content
        if current_tab == 0:  # Usage tab
            content = self.usage_tab.findChild(QTextBrowser).toPlainText()
        elif current_tab == 1:  # Features tab
            content = self.features_tab.findChild(QTextBrowser).toPlainText()
        elif current_tab == 2:  # Tips tab
            content = self.tips_tab.findChild(QTextBrowser).toPlainText()
        
        # Split content into sections (by headings)
        sections = content.split('\n\n')
        matching_sections = []
        
        # Search through each section
        for section in sections:
            if search_text in section.lower():
                matching_sections.append(section)
        
        # If no matches found, show a message
        if not matching_sections:
            self.show_no_results_message()
            return
            
        # Create a new QTextBrowser with search results
        results_text = QTextBrowser()
        results_text.setReadOnly(True)
        results_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        # Format search results with highlighting
        html_content = """
            <style>
                .highlight { background-color: #333333; }
                .section-title { font-weight: bold; margin-bottom: 10px; }
                .section-content { margin-bottom: 20px; }
            </style>
        """
        
        # Add matching sections with highlighted text
        for section in matching_sections:
            # Split section into title and content
            lines = section.split('\n')
            title = lines[0]
            content = '\n'.join(lines[1:])
            
            # Highlight search terms
            highlighted_content = self.highlight_search_terms(content, search_text)
            
            html_content += f"""
                <div class="section-title">{title}</div>
                <div class="section-content">{highlighted_content}</div>
            """
        
        results_text.setHtml(html_content)
        
        # Replace current content with search results
        if current_tab == 0:
            self.usage_tab.findChild(QTextBrowser).setHtml(html_content)
        elif current_tab == 1:
            self.features_tab.findChild(QTextBrowser).setHtml(html_content)
        elif current_tab == 2:
            self.tips_tab.findChild(QTextBrowser).setHtml(html_content)
    
    def highlight_search_terms(self, text, search_term):
        """Highlight all occurrences of search term in text."""
        if not self.search_options['highlight']:
            return text
            
        highlighted = []
        start = 0
        
        while True:
            index = text.lower().find(search_term, start)
            if index == -1:
                break
                
            # Get the text before the match
            before = text[start:index]
            # Get the matching text
            match = text[index:index + len(search_term)]
            # Get the text after the match
            after = text[index + len(search_term):]
            
            # Add to highlighted text
            highlighted.append(before)
            highlighted.append(f'<span class="highlight">{match}</span>')
            
            # Update start position
            start = index + len(search_term)
        
        # Add remaining text
        highlighted.append(text[start:])
        
        return ''.join(highlighted)
    
    def clear_search_highlights(self):
        """Clear any existing search highlights."""
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:
            self.usage_tab.findChild(QTextBrowser).setHtml(self.get_original_content(0))
        elif current_tab == 1:
            self.features_tab.findChild(QTextBrowser).setHtml(self.get_original_content(1))
        elif current_tab == 2:
            self.tips_tab.findChild(QTextBrowser).setHtml(self.get_original_content(2))
    
    def get_original_content(self, tab_index):
        """Get the original content for a tab."""
        if tab_index == 0:  # Usage tab
            return self.get_usage_content()
        elif tab_index == 1:  # Features tab
            return self.get_features_content()
        elif tab_index == 2:  # Tips tab
            return self.get_tips_content()
        return ""
    
    def show_no_results_message(self):
        """Show a message when no results are found."""
        current_tab = self.tabs.currentIndex()
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.setHtml(f"""
                <style>
                    .no-results { 
                        font-size: 14pt; 
                        color: #666; 
                        text-align: center; 
                        padding: 20px;
                    }
                </style>
                <div class="no-results">
                    {self.translate('help_no_results')}
                </div>
            """)
    
    def get_current_text_edit(self):
        """Get the current text edit widget based on active tab."""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            return self.usage_tab.findChild(QTextBrowser)
        elif current_tab == 1:
            return self.features_tab.findChild(QTextBrowser)
        elif current_tab == 2:
            return self.tips_tab.findChild(QTextBrowser)
        return None
    
    def setup_usage_tab(self):
        """Setup the usage tab content."""
        # Create scroll area for better content management
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget to hold the scroll area's contents
        content_widget = QWidget()
        
        # Create the main layout for the content widget
        content_layout = QVBoxLayout(content_widget)  # Set parent widget here
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Title and introduction
        title = QLabel(self.translate('help_usage_title', version=get_version()))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        intro = QLabel(self.translate('help_usage_intro'))
        intro.setWordWrap(True)
        intro.setStyleSheet("""
            font-size: 14px;
            margin-bottom: 20px;
            color: #e0e0e0;
        """)
        
        # Add title and intro to content layout
        content_layout.addWidget(title)
        content_layout.addWidget(intro)
        
        # Features section
        features_group = QGroupBox(self.translate('help_features_title'))
        features_layout = QVBoxLayout(features_group)  # Set parent widget here
        
        features_text = QTextBrowser()
        features_text.setReadOnly(True)
        features_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        features_content = """
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;"><b>{}</b></li>
            <li style="margin-bottom: 10px;"><b>{}</b></li>
            <li style="margin-bottom: 10px;"><b>{}</b></li>
            <li style="margin-bottom: 10px;"><b>{}</b></li>
        </ul>
        """.format(
            self.translate('help_feature_1'),
            self.translate('help_feature_2'),
            self.translate('help_feature_3'),
            self.translate('help_feature_4')
        )
        
        features_text.setHtml(features_content)
        features_layout.addWidget(features_text)
        
        # Add features group to content layout
        content_layout.addWidget(features_group)
        
        # Usage steps section
        steps_group = QGroupBox(self.translate('help_usage_title_2'))
        steps_layout = QVBoxLayout(steps_group)  # Set parent widget here
        
        steps_text = QTextBrowser()
        steps_text.setReadOnly(True)
        steps_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        steps_content = """
        <ol style="list-style-type: decimal; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{}</li>
            <li style="margin-bottom: 10px;">{}</li>
            <li style="margin-bottom: 10px;">{}</li>
            <li style="margin-bottom: 10px;">{}</li>
            <li style="margin-bottom: 10px;">{}<ul style="list-style-type: square; margin-left: 30px;">
                <li><b>{}</b></li>
                <li><b>{}</b></li>
                <li><b>{}</b></li>
            </ul></li>
        </ol>
        """.format(
            self.translate('help_usage_step_1'),
            self.translate('help_usage_step_2'),
            self.translate('help_usage_step_3'),
            self.translate('help_usage_step_4'),
            self.translate('help_usage_step_5'),
            self.translate('help_usage_select_all'),
            self.translate('help_usage_delete_selected'),
            self.translate('help_usage_delete_all')
        )
        
        steps_text.setHtml(steps_content)
        steps_layout.addWidget(steps_text)
        
        # Add steps group to content layout
        content_layout.addWidget(steps_group)
        
        # Supported formats section
        formats_group = QGroupBox(self.translate('help_supported_formats'))
        formats_layout = QVBoxLayout(formats_group)  # Set parent widget here
        
        formats_text = QTextBrowser()
        formats_text.setReadOnly(True)
        formats_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        formats_content = """
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{}</li>
            <li style="margin-bottom: 10px;">{}</li>
        </ul>
        """.format(
            self.translate('help_formats_1'),
            self.translate('help_formats_2')
        )
        
        formats_text.setHtml(formats_content)
        formats_layout.addWidget(formats_text)
        
        # Add formats group to content layout
        content_layout.addWidget(formats_group)
        
        # Add stretch to push content to the top
        content_layout.addStretch()
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        
        # Create a layout for the tab and add the scroll area
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Set the layout on the tab widget
        self.usage_tab.setLayout(tab_layout)
    
    def setup_features_tab(self):
        """Setup the features tab content."""
        # Create scroll area for better content management
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Title
        title = QLabel(self.translate('help_features_title_full'))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        # Image Comparison section
        image_group = QGroupBox(self.translate('help_features_image_title'))
        image_layout = QVBoxLayout(image_group)
        
        image_text = QTextBrowser()
        image_text.setReadOnly(True)
        image_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        image_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_features_image_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_image_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_image_3')}</li>
        </ul>
        """
        
        image_text.setHtml(image_content)
        image_layout.addWidget(image_text)
        
        # Batch Operations section
        batch_group = QGroupBox(self.translate('help_features_batch_title'))
        batch_layout = QVBoxLayout(batch_group)
        
        batch_text = QTextBrowser()
        batch_text.setReadOnly(True)
        batch_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        batch_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_features_batch_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_batch_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_batch_3')}</li>
        </ul>
        """
        
        batch_text.setHtml(batch_content)
        batch_layout.addWidget(batch_text)
        
        # Quality Control section
        quality_group = QGroupBox(self.translate('help_features_quality_title'))
        quality_layout = QVBoxLayout(quality_group)
        
        quality_text = QTextBrowser()
        quality_text.setReadOnly(True)
        quality_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        quality_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_features_quality_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_quality_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_features_quality_3')}</li>
        </ul>
        """
        
        quality_text.setHtml(quality_content)
        quality_layout.addWidget(quality_text)
        
        # Version 1.7.0 Improvements section
        version_group = QGroupBox("Version 1.7.0 Improvements")
        version_layout = QVBoxLayout(version_group)
        
        version_text = QTextBrowser()
        version_text.setReadOnly(True)
        version_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
            color: #e0e0e0;
        """)
        
        version_content = """
        <h3>PyQt6 Signal Handling Improvements</h3>
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">Fixed signal import error in workers.py</li>
            <li style="margin-bottom: 10px;">Updated WorkerSignals class to use pyqtSignal consistently</li>
            <li style="margin-bottom: 10px;">Improved thread safety in signal handling</li>
        </ul>
        <h3>Maintenance Updates</h3>
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">Updated project dependencies</li>
            <li style="margin-bottom: 10px;">Improved code documentation</li>
            <li style="margin-bottom: 10px;">Enhanced error handling</li>
        </ul>
        """
        
        version_text.setHtml(version_content)
        version_layout.addWidget(version_text)
        
        # Add all groups to content layout
        content_layout.addWidget(title)
        content_layout.addWidget(version_group)
        content_layout.addWidget(image_group)
        content_layout.addWidget(batch_group)
        content_layout.addWidget(quality_group)
        content_layout.addStretch()
        
        # Set content widget and scroll area
        scroll.setWidget(content_widget)
        
        # Create layout for features tab and set it
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)
        self.features_tab.setLayout(layout)
    
    def setup_tips_tab(self):
        """Setup the tips tab content."""
        # Create scroll area for better content management
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Title
        title = QLabel(self.translate('help_tips_title'))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        # Large Collections section
        large_group = QGroupBox(self.translate('help_tips_large_title'))
        large_layout = QVBoxLayout(large_group)
        
        large_text = QTextBrowser()
        large_text.setReadOnly(True)
        large_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        large_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_tips_large_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_large_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_large_3')}</li>
        </ul>
        """
        
        large_text.setHtml(large_content)
        large_layout.addWidget(large_text)
        
        # Image Formats section
        formats_group = QGroupBox(self.translate('help_tips_formats_title'))
        formats_layout = QVBoxLayout(formats_group)
        
        formats_text = QTextBrowser()
        formats_text.setReadOnly(True)
        formats_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        formats_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_tips_formats_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_formats_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_formats_3')}</li>
        </ul>
        """
        
        formats_text.setHtml(formats_content)
        formats_layout.addWidget(formats_text)
        
        # Performance section
        perf_group = QGroupBox(self.translate('help_tips_perf_title'))
        perf_layout = QVBoxLayout(perf_group)
        
        perf_text = QTextBrowser()
        perf_text.setReadOnly(True)
        perf_text.setStyleSheet("""
            font-family: Arial;
            font-size: 12pt;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 15px;
        """)
        
        perf_content = f"""
        <ul style="list-style-type: disc; margin-left: 20px;">
            <li style="margin-bottom: 10px;">{self.translate('help_tips_perf_1')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_perf_2')}</li>
            <li style="margin-bottom: 10px;">{self.translate('help_tips_perf_3')}</li>
        </ul>
        """
        
        perf_text.setHtml(perf_content)
        perf_layout.addWidget(perf_text)
        
        # Add all groups to content layout
        content_layout.addWidget(title)
        content_layout.addWidget(large_group)
        content_layout.addWidget(formats_group)
        content_layout.addWidget(perf_group)
        content_layout.addStretch()
        
        # Set content widget and scroll area
        scroll.setWidget(content_widget)
        
        # Create layout for tips tab and set it
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tips_tab.setLayout(layout)
    
    def change_language(self, lang_code):
        """Change the UI language."""
        if lang_code == self.lang:
            return  # No change needed
            
        self.lang_manager.set_language(lang_code)
        self.lang = lang_code
        
        # Update button states
        self.english_button.setChecked(lang_code == 'en')
        self.italian_button.setChecked(lang_code == 'it')
        
        # Update UI
        self.retranslate_ui()
        
        # Update search options menu
        self.search_options_button.setMenu(self.create_search_options_menu())
        
        # Update search input placeholder
        self.search_input.setPlaceholderText(self.translate('search_help'))
        
        # Update close button text
        self.close_button.setText(self.translate('help_close'))
        
        # Update tab names
        self.tabs.setTabText(0, self.translate('usage'))
        self.tabs.setTabText(1, self.translate('help_features'))
        self.tabs.setTabText(2, self.translate('help_tips'))
        
        # Update language label
        self.lang_label.setText(self.translate('language') + ":")
        
        # Update tab contents
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
        
        # Re-apply search if there was one
        if hasattr(self, 'last_search') and self.last_search:
            self.perform_search()
    
    def get_usage_content(self):
        """Get the original content for the usage tab."""
        content = f"""
        <h1>{self.translate('help_usage_title', version=get_version())}</h1>
        <p>{self.translate('help_usage_intro')}</p>
        
        <h2>{self.translate('help_features_title')}</h2>
        <ul>
            <li><b>{self.translate('help_feature_1')}</b></li>
            <li><b>{self.translate('help_feature_2')}</b></li>
            <li><b>{self.translate('help_feature_3')}</b></li>
            <li><b>{self.translate('help_feature_4')}</b></li>
        </ul>
        
        <h2>{self.translate('help_usage_title_2')}</h2>
        <ol>
            <li>{self.translate('help_usage_step_1')}</li>
            <li>{self.translate('help_usage_step_2')}</li>
            <li>{self.translate('help_usage_step_3')}</li>
            <li>{self.translate('help_usage_step_4')}</li>
            <li>{self.translate('help_usage_step_5')}
                <ul>
                    <li><b>{self.translate('help_usage_select_all')}</b></li>
                    <li><b>{self.translate('help_usage_delete_selected')}</b></li>
                    <li><b>{self.translate('help_usage_delete_all')}</b></li>
                </ul>
            </li>
        </ol>
        
        <h2>{self.translate('help_supported_formats')}</h2>
        <ul>
            <li>{self.translate('help_formats_1')}</li>
            <li>{self.translate('help_formats_2')}</li>
        </ul>
        
        <h2>{self.translate('help_visit_website')}</h2>
        <p>
            <a href="https://github.com/Nsfr750/Images-Deduplicator" 
               style="color: #4a90e2; text-decoration: none;"
               onclick="window.open(this.href); return false;">
                https://github.com/Nsfr750/Images-Deduplicator
            </a>
        </p>
        """
        return content
    
    def get_features_content(self):
        """Get the original content for the features tab."""
        content = f"""
        <h1>{self.translate('help_features_title_full')}</h1>
        
        <h2>{self.translate('help_features_image_title')}</h2>
        <ul>
            <li>{self.translate('help_features_image_1')}</li>
            <li>{self.translate('help_features_image_2')}</li>
            <li>{self.translate('help_features_image_3')}</li>
        </ul>
        
        <h2>{self.translate('help_features_batch_title')}</h2>
        <ul>
            <li>{self.translate('help_features_batch_1')}</li>
            <li>{self.translate('help_features_batch_2')}</li>
            <li>{self.translate('help_features_batch_3')}</li>
        </ul>
        
        <h2>{self.translate('help_features_quality_title')}</h2>
        <ul>
            <li>{self.translate('help_features_quality_1')}</li>
            <li>{self.translate('help_features_quality_2')}</li>
            <li>{self.translate('help_features_quality_3')}</li>
        </ul>
        """
        return content
    
    def get_tips_content(self):
        """Get the original content for the tips tab."""
        content = f"""
        <h1>{self.translate('help_tips_title')}</h1>
        
        <h2>{self.translate('help_tips_large_title')}</h2>
        <ul>
            <li>{self.translate('help_tips_large_1')}</li>
            <li>{self.translate('help_tips_large_2')}</li>
            <li>{self.translate('help_tips_large_3')}</li>
        </ul>
        
        <h2>{self.translate('help_tips_formats_title')}</h2>
        <ul>
            <li>{self.translate('help_tips_formats_1')}</li>
            <li>{self.translate('help_tips_formats_2')}</li>
            <li>{self.translate('help_tips_formats_3')}</li>
        </ul>
        
        <h2>{self.translate('help_tips_perf_title')}</h2>
        <ul>
            <li>{self.translate('help_tips_perf_1')}</li>
            <li>{self.translate('help_tips_perf_2')}</li>
            <li>{self.translate('help_tips_perf_3')}</li>
        </ul>
        """
        return content

# For backward compatibility with Tkinter version
class Help:
    @staticmethod
    def show_help(parent=None):
        dialog = HelpDialog(parent)
        dialog.exec()
