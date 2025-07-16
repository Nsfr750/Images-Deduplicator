"""
Help dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QTabWidget, QWidget,
    QHBoxLayout, QFrame, QScrollArea, QSizePolicy, QComboBox, QLineEdit,
    QGroupBox, QGridLayout, QToolButton, QStyle, QMenu
)
from PyQt6.QtCore import Qt, QSize, QEvent, QUrl, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QDesktopServices, QAction

from script.translations import t, LANGUAGES
from script.version import get_version

import re
from difflib import SequenceMatcher

class HelpDialog(QDialog):
    """Help dialog showing usage information and language selection."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('help', lang))
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
        self.setStyleSheet("""
            /* Base styles */
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #357abd;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2c6599;
            }
            
            /* Tabs */
            QTabBar::tab {
                background: #222222;
                color: #ffffff;
                padding: 8px 12px;
                border: 1px solid #333333;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #1a1a1a;
                border-bottom: 1px solid #1a1a1a;
                color: #357abd;
            }
            
            /* Text Browser (main content) */
            QTextBrowser {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
                padding: 15px;
                min-height: 200px;
                font-size: 14px;
                font-family: Arial, sans-serif;
            }
            QTextBrowser a {
                color: #286CBD;
                text-decoration: none;
            }
            QTextBrowser a:hover {
                color: #2c6599;
            }
            QTextBrowser h1, QTextBrowser h2, QTextBrowser h3 {
                color: #286CBD;
                margin-bottom: 10px;
            }
            QTextBrowser h4 {
                color: #666666;
                margin-bottom: 8px;
            }
            QTextBrowser ul, QTextBrowser ol {
                margin-left: 20px;
                color: #ffffff;
            }
            QTextBrowser li {
                margin-bottom: 5px;
                color: #ffffff;
            }
            QTextBrowser p {
                color: #ffffff;
                margin-bottom: 10px;
            }
            QTextBrowser div {
                color: #ffffff;
            }
            QTextBrowser span {
                color: #ffffff;
            }
            QTextBrowser .highlight {
                background-color: #333333;
                color: #ffffff;
            }
            QTextBrowser .no-results {
                color: #666666;
            }
            
            /* Input fields */
            QLineEdit {
                background-color: #222222;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #333333;
                border-radius: 4px;
                margin: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #357abd;
            }
            
            /* Combo boxes */
            QComboBox {
                background-color: #222222;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #333333;
                border-radius: 4px;
                font-size: 14px;
            }
            
            /* Group boxes */
            QGroupBox {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #333333;
                background-color: #222222;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #DAD9A2;
            }
            
            /* Tool buttons */
            QToolButton {
                background-color: #222222;
                border: none;
                padding: 5px;
                color: #ffffff;
            }
            QToolButton:hover {
                background-color: #333333;
            }
            
            /* Search options button */
            #searchOptionsButton {
                padding: 5px;
                border: 1px solid #333333;
                background: #222222;
                color: #ffffff;
            }
            
            /* Clear search button */
            #clearSearchButton {
                background: #ff4444;
                border: none;
                border-radius: 10px;
                padding: 2px 6px;
                color: #ffffff;
            }
            #clearSearchButton:hover {
                background: #cc0000;
            }
            
            /* Match count */
            #matchCount {
                color: #666666;
                margin-left: 10px;
            }
            
            /* Scrollbar styling */
            QScrollBar:vertical {
                background: #222222;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
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
        self.search_input.setPlaceholderText(t('search_help', self.lang))
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
        
        self.lang_label = QLabel(t('language', self.lang) + ":")
        
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
        layout.addWidget(header_frame)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.usage_tab = QWidget()
        self.features_tab = QWidget()
        self.tips_tab = QWidget()
        
        self.tabs.addTab(self.usage_tab, t('usage', self.lang))
        self.tabs.addTab(self.features_tab, t('help_features', self.lang))
        self.tabs.addTab(self.tips_tab, t('help_tips', self.lang))
        
        # Setup tab contents
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
        
        # Close button
        self.close_button = QPushButton(t('help_close', self.lang))
        self.close_button.clicked.connect(self.accept)
        self.close_button.setFixedWidth(100)
        
        # Add widgets to layout
        layout.addWidget(self.tabs, 1)
        
        # Center the close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Set tab order
        self.setTabOrder(self.search_input, self.english_button)
        self.setTabOrder(self.english_button, self.italian_button)
        self.setTabOrder(self.italian_button, self.tabs)
        self.setTabOrder(self.tabs, self.close_button)
    
    def create_search_options_menu(self):
        """Create the search options menu."""
        menu = QMenu()
        
        # Case sensitivity
        self.case_sensitive_action = QAction(t('search_case_sensitive', self.lang), self)
        self.case_sensitive_action.setCheckable(True)
        self.case_sensitive_action.setChecked(self.search_options['case_sensitive'])
        self.case_sensitive_action.triggered.connect(self.update_search_options)
        menu.addAction(self.case_sensitive_action)
        
        # Whole words
        self.whole_words_action = QAction(t('search_whole_words', self.lang), self)
        self.whole_words_action.setCheckable(True)
        self.whole_words_action.setChecked(self.search_options['whole_words'])
        self.whole_words_action.triggered.connect(self.update_search_options)
        menu.addAction(self.whole_words_action)
        
        # Highlight
        self.highlight_action = QAction(t('search_highlight', self.lang), self)
        self.highlight_action.setCheckable(True)
        self.highlight_action.setChecked(self.search_options['highlight'])
        self.highlight_action.triggered.connect(self.update_search_options)
        menu.addAction(self.highlight_action)
        
        # Fuzzy matching
        self.fuzzy_action = QAction(t('search_fuzzy', self.lang), self)
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
        self.match_count_label.setText(f"{len(matches)} {t('matches', self.lang)}")
        
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
                    {t('help_no_results', self.lang)}
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
        title = QLabel(t('help_usage_title', self.lang, version=get_version()))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        intro = QLabel(t('help_usage_intro', self.lang))
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
        features_group = QGroupBox(t('help_features_title', self.lang))
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
            t('help_feature_1', self.lang),
            t('help_feature_2', self.lang),
            t('help_feature_3', self.lang),
            t('help_feature_4', self.lang)
        )
        
        features_text.setHtml(features_content)
        features_layout.addWidget(features_text)
        
        # Add features group to content layout
        content_layout.addWidget(features_group)
        
        # Usage steps section
        steps_group = QGroupBox(t('help_usage_title_2', self.lang))
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
            t('help_usage_step_1', self.lang),
            t('help_usage_step_2', self.lang),
            t('help_usage_step_3', self.lang),
            t('help_usage_step_4', self.lang),
            t('help_usage_step_5', self.lang),
            t('help_usage_select_all', self.lang),
            t('help_usage_delete_selected', self.lang),
            t('help_usage_delete_all', self.lang)
        )
        
        steps_text.setHtml(steps_content)
        steps_layout.addWidget(steps_text)
        
        # Add steps group to content layout
        content_layout.addWidget(steps_group)
        
        # Supported formats section
        formats_group = QGroupBox(t('help_supported_formats', self.lang))
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
            t('help_formats_1', self.lang),
            t('help_formats_2', self.lang)
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
        title = QLabel(t('help_features_title_full', self.lang))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        # Image Comparison section
        image_group = QGroupBox(t('help_features_image_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_features_image_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_image_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_image_3', self.lang)}</li>
        </ul>
        """
        
        image_text.setHtml(image_content)
        image_layout.addWidget(image_text)
        
        # Batch Operations section
        batch_group = QGroupBox(t('help_features_batch_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_features_batch_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_batch_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_batch_3', self.lang)}</li>
        </ul>
        """
        
        batch_text.setHtml(batch_content)
        batch_layout.addWidget(batch_text)
        
        # Quality Control section
        quality_group = QGroupBox(t('help_features_quality_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_features_quality_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_quality_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_features_quality_3', self.lang)}</li>
        </ul>
        """
        
        quality_text.setHtml(quality_content)
        quality_layout.addWidget(quality_text)
        
        # Add all groups to content layout
        content_layout.addWidget(title)
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
        title = QLabel(t('help_tips_title', self.lang))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #286CBD;
        """)
        
        # Large Collections section
        large_group = QGroupBox(t('help_tips_large_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_tips_large_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_large_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_large_3', self.lang)}</li>
        </ul>
        """
        
        large_text.setHtml(large_content)
        large_layout.addWidget(large_text)
        
        # Image Formats section
        formats_group = QGroupBox(t('help_tips_formats_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_tips_formats_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_formats_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_formats_3', self.lang)}</li>
        </ul>
        """
        
        formats_text.setHtml(formats_content)
        formats_layout.addWidget(formats_text)
        
        # Performance section
        perf_group = QGroupBox(t('help_tips_perf_title', self.lang))
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
            <li style="margin-bottom: 10px;">{t('help_tips_perf_1', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_perf_2', self.lang)}</li>
            <li style="margin-bottom: 10px;">{t('help_tips_perf_3', self.lang)}</li>
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
            
        self.lang = lang_code
        
        # Update button states
        self.english_button.setChecked(lang_code == 'en')
        self.italian_button.setChecked(lang_code == 'it')
        
        # Update UI
        self.setWindowTitle(t('help', self.lang))
        self.retranslate_ui()
        
        # Update search options menu
        self.search_options_button.setMenu(self.create_search_options_menu())
        
        # Update search input placeholder
        self.search_input.setPlaceholderText(t('search_help', self.lang))
        
        # Update close button text
        self.close_button.setText(t('help_close', self.lang))
        
        # Update tab names
        self.tabs.setTabText(0, t('usage', self.lang))
        self.tabs.setTabText(1, t('help_features', self.lang))
        self.tabs.setTabText(2, t('help_tips', self.lang))
        
        # Update language label
        self.lang_label.setText(t('language', self.lang) + ":")
        
        # Update tab contents
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
        
        # Re-apply search if there was one
        if hasattr(self, 'last_search') and self.last_search:
            self.perform_search()
    
    def retranslate_ui(self):
        """Update all UI text elements to the current language."""
        # Update header elements
        self.search_input.setPlaceholderText(t('search_help', self.lang))
        self.lang_label.setText(t('language', self.lang) + ":")
        self.close_button.setText(t('help_close', self.lang))
        
        # Update search options menu
        self.case_sensitive_action.setText(t('search_case_sensitive', self.lang))
        self.whole_words_action.setText(t('search_whole_words', self.lang))
        self.highlight_action.setText(t('search_highlight', self.lang))
        self.fuzzy_action.setText(t('search_fuzzy', self.lang))
        
        # Update match count label
        search_text = self.search_input.text()
        if search_text:
            matches = self.find_matches(search_text)
            self.match_count_label.setText(f"{len(matches)} {t('matches', self.lang)}")
        
        # Update tab titles
        self.tabs.setTabText(0, t('usage', self.lang))
        self.tabs.setTabText(1, t('help_features', self.lang))
        self.tabs.setTabText(2, t('help_tips', self.lang))
        
        # Update tab content
        self.usage_tab.findChild(QTextBrowser).setHtml(self.get_usage_content())
        self.features_tab.findChild(QTextBrowser).setHtml(self.get_features_content())
        self.tips_tab.findChild(QTextBrowser).setHtml(self.get_tips_content())
        
        # Update any existing search results
        if search_text:
            self.filter_content(search_text)
    
    def get_usage_content(self):
        """Get the original content for the usage tab."""
        content = f"""
        <h1>{t('help_usage_title', self.lang, version=get_version())}</h1>
        <p>{t('help_usage_intro', self.lang)}</p>
        
        <h2>{t('help_features_title', self.lang)}</h2>
        <ul>
            <li><b>{t('help_feature_1', self.lang)}</b></li>
            <li><b>{t('help_feature_2', self.lang)}</b></li>
            <li><b>{t('help_feature_3', self.lang)}</b></li>
            <li><b>{t('help_feature_4', self.lang)}</b></li>
        </ul>
        
        <h2>{t('help_usage_title_2', self.lang)}</h2>
        <ol>
            <li>{t('help_usage_step_1', self.lang)}</li>
            <li>{t('help_usage_step_2', self.lang)}</li>
            <li>{t('help_usage_step_3', self.lang)}</li>
            <li>{t('help_usage_step_4', self.lang)}</li>
            <li>{t('help_usage_step_5', self.lang)}
                <ul>
                    <li><b>{t('help_usage_select_all', self.lang)}</b></li>
                    <li><b>{t('help_usage_delete_selected', self.lang)}</b></li>
                    <li><b>{t('help_usage_delete_all', self.lang)}</b></li>
                </ul>
            </li>
        </ol>
        
        <h2>{t('help_supported_formats', self.lang)}</h2>
        <ul>
            <li>{t('help_formats_1', self.lang)}</li>
            <li>{t('help_formats_2', self.lang)}</li>
        </ul>
        
        <h2>{t('help_visit_website', self.lang)}</h2>
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
        <h1>{t('help_features_title_full', self.lang)}</h1>
        
        <h2>{t('help_features_image_title', self.lang)}</h2>
        <ul>
            <li>{t('help_features_image_1', self.lang)}</li>
            <li>{t('help_features_image_2', self.lang)}</li>
            <li>{t('help_features_image_3', self.lang)}</li>
        </ul>
        
        <h2>{t('help_features_batch_title', self.lang)}</h2>
        <ul>
            <li>{t('help_features_batch_1', self.lang)}</li>
            <li>{t('help_features_batch_2', self.lang)}</li>
            <li>{t('help_features_batch_3', self.lang)}</li>
        </ul>
        
        <h2>{t('help_features_quality_title', self.lang)}</h2>
        <ul>
            <li>{t('help_features_quality_1', self.lang)}</li>
            <li>{t('help_features_quality_2', self.lang)}</li>
            <li>{t('help_features_quality_3', self.lang)}</li>
        </ul>
        """
        return content
    
    def get_tips_content(self):
        """Get the original content for the tips tab."""
        content = f"""
        <h1>{t('help_tips_title', self.lang)}</h1>
        
        <h2>{t('help_tips_large_title', self.lang)}</h2>
        <ul>
            <li>{t('help_tips_large_1', self.lang)}</li>
            <li>{t('help_tips_large_2', self.lang)}</li>
            <li>{t('help_tips_large_3', self.lang)}</li>
        </ul>
        
        <h2>{t('help_tips_formats_title', self.lang)}</h2>
        <ul>
            <li>{t('help_tips_formats_1', self.lang)}</li>
            <li>{t('help_tips_formats_2', self.lang)}</li>
            <li>{t('help_tips_formats_3', self.lang)}</li>
        </ul>
        
        <h2>{t('help_tips_perf_title', self.lang)}</h2>
        <ul>
            <li>{t('help_tips_perf_1', self.lang)}</li>
            <li>{t('help_tips_perf_2', self.lang)}</li>
            <li>{t('help_tips_perf_3', self.lang)}</li>
        </ul>
        """
        return content

# For backward compatibility with Tkinter version
class Help:
    @staticmethod
    def show_help(parent):
        dialog = HelpDialog(parent)
        dialog.exec()
