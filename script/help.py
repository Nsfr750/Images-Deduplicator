"""
Help dialog for the Image Deduplicator application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QTabWidget, QWidget,
    QHBoxLayout, QFrame, QScrollArea, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QTextCursor

from script.translations import t, LANGUAGES
from script.version import get_version

class HelpDialog(QDialog):
    """Help dialog showing usage information and language selection."""
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t('help', lang))
        self.setMinimumSize(700, 500)
        
        # Set application style
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 12px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #f8f8f8;
                border-bottom: 1px solid #f8f8f8;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Language selection
        lang_frame = QWidget()
        lang_layout = QHBoxLayout(lang_frame)
        lang_layout.setContentsMargins(0, 0, 0, 10)
        
        lang_label = QLabel(t('language', self.lang) + ":")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([code.upper() for code in LANGUAGES])
        self.lang_combo.setCurrentText(self.lang.upper())
        self.lang_combo.currentTextChanged.connect(self.change_language)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
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
        close_button = QPushButton(t('help_close', self.lang))
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        
        # Add widgets to layout
        layout.addWidget(lang_frame)
        layout.addWidget(self.tabs, 1)
        
        # Center the close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Set tab order
        self.setTabOrder(self.lang_combo, self.tabs)
        self.setTabOrder(self.tabs, close_button)
    
    def setup_usage_tab(self):
        """Setup the usage tab content."""
        layout = QVBoxLayout(self.usage_tab)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: Arial; font-size: 11pt;")
        
        # Format text with HTML for better readability
        html_content = f"""
        <h2>{t('help_usage_title', self.lang, version=get_version())}</h2>
        
        <p>{t('help_usage_intro', self.lang)}</p>
        
        <h3>{t('help_features_title', self.lang)}</h3>
        <ul>
            <li>{t('help_feature_1', self.lang)}</li>
            <li>{t('help_feature_2', self.lang)}</li>
            <li>{t('help_feature_3', self.lang)}</li>
            <li>{t('help_feature_4', self.lang)}</li>
        </ul>
        
        <h3>{t('help_usage_title_2', self.lang)}</h3>
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
        
        <h3>{t('help_supported_formats', self.lang)}</h3>
        <ul>
            <li>{t('help_formats_1', self.lang)}</li>
            <li>{t('help_formats_2', self.lang)}</li>
        </ul>
        
        <p>{t('help_visit_website', self.lang)}<br>
        <a href="https://github.com/Nsfr750/Images-Deduplicator">https://github.com/Nsfr750/Images-Deduplicator</a></p>
        """
        
        text_edit.setHtml(html_content)
        text_edit.setOpenExternalLinks(True)
        
        layout.addWidget(text_edit)
    
    def setup_features_tab(self):
        """Setup the features tab content."""
        layout = QVBoxLayout(self.features_tab)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: Arial; font-size: 11pt;")
        
        html_content = f"""
        <h2>{t('help_features_title_full', self.lang)}</h2>
        
        <h3>{t('help_features_image_title', self.lang)}</h3>
        <ul>
            <li>{t('help_features_image_1', self.lang)}</li>
            <li>{t('help_features_image_2', self.lang)}</li>
            <li>{t('help_features_image_3', self.lang)}</li>
        </ul>
        
        <h3>{t('help_features_batch_title', self.lang)}</h3>
        <ul>
            <li>{t('help_features_batch_1', self.lang)}</li>
            <li>{t('help_features_batch_2', self.lang)}</li>
            <li>{t('help_features_batch_3', self.lang)}</li>
        </ul>
        
        <h3>{t('help_features_quality_title', self.lang)}</h3>
        <ul>
            <li>{t('help_features_quality_1', self.lang)}</li>
            <li>{t('help_features_quality_2', self.lang)}</li>
            <li>{t('help_features_quality_3', self.lang)}</li>
        </ul>
        """
        
        text_edit.setHtml(html_content)
        layout.addWidget(text_edit)
    
    def setup_tips_tab(self):
        """Setup the tips tab content."""
        layout = QVBoxLayout(self.tips_tab)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: Arial; font-size: 11pt;")
        
        html_content = f"""
        <h2>{t('help_tips_title', self.lang)}</h2>
        
        <h3>{t('help_tips_large_title', self.lang)}</h3>
        <ul>
            <li>{t('help_tips_large_1', self.lang)}</li>
            <li>{t('help_tips_large_2', self.lang)}</li>
            <li>{t('help_tips_large_3', self.lang)}</li>
        </ul>
        
        <h3>{t('help_tips_formats_title', self.lang)}</h3>
        <ul>
            <li>{t('help_tips_formats_1', self.lang)}</li>
            <li>{t('help_tips_formats_2', self.lang)}</li>
            <li>{t('help_tips_formats_3', self.lang)}</li>
        </ul>
        
        <h3>{t('help_tips_perf_title', self.lang)}</h3>
        <ul>
            <li>{t('help_tips_perf_1', self.lang)}</li>
            <li>{t('help_tips_perf_2', self.lang)}</li>
            <li>{t('help_tips_perf_3', self.lang)}</li>
        </ul>
        """
        
        text_edit.setHtml(html_content)
        layout.addWidget(text_edit)
    
    def change_language(self, lang_code):
        """Change the UI language."""
        self.lang = lang_code.lower()
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.setWindowTitle(t('help', self.lang))
        
        # Update tab names
        self.tabs.setTabText(0, t('usage', self.lang))
        self.tabs.setTabText(1, t('help_features', self.lang))
        self.tabs.setTabText(2, t('help_tips', self.lang))
        
        # Update tab contents
        self.setup_usage_tab()
        self.setup_features_tab()
        self.setup_tips_tab()
        
        # Update close button
        for btn in self.findChildren(QPushButton):
            if btn.text().replace('&', '') in [t('help_close', 'en'), t('help_close', 'es'), t('help_close', 'fr'), 
                                             t('help_close', 'de'), t('help_close', 'pt'), t('help_close', 'it')]:
                btn.setText(t('help_close', self.lang))
                break

# For backward compatibility with Tkinter version
class Help:
    @staticmethod
    def show_help(parent):
        dialog = HelpDialog(parent)
        dialog.exec()
