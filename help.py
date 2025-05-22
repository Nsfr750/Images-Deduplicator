import tkinter as tk
from tkinter import ttk, messagebox
from translations import t, LANGUAGES

LANG = 'en'  # Default, will be changed dynamically

class Help:
    @staticmethod
    def show_help(parent):
        """Show help window with usage information and language selection"""
        global LANG
        help_window = tk.Toplevel(parent)
        help_window.title(t('help_title', LANG))
        help_window.geometry("600x400")

        # Language selection dropdown
        lang_var = tk.StringVar(value=LANG)
        lang_frame = ttk.Frame(help_window)
        lang_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        lang_menu = ttk.Combobox(lang_frame, textvariable=lang_var, values=[code.upper() for code in LANGUAGES], state="readonly", width=8)
        lang_menu.pack(side=tk.LEFT, padx=5)

        # Notebook for help sections
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        usage_frame = ttk.Frame(notebook)
        features_frame = ttk.Frame(notebook)
        tips_frame = ttk.Frame(notebook)

        notebook.add(usage_frame, text=t('usage', LANG))
        notebook.add(features_frame, text=t('features', LANG))
        notebook.add(tips_frame, text=t('tips', LANG))

        # Labels for each tab
        usage_label = ttk.Label(usage_frame, justify=tk.LEFT)
        usage_label.pack(padx=10, pady=10)
        features_label = ttk.Label(features_frame, justify=tk.LEFT)
        features_label.pack(padx=10, pady=10)
        tips_label = ttk.Label(tips_frame, justify=tk.LEFT)
        tips_label.pack(padx=10, pady=10)

        # Close button
        close_button = ttk.Button(help_window, text=t('close', LANG), command=help_window.destroy)
        close_button.pack(pady=10)

        def refresh_texts():
            help_window.title(t('help_title', lang_var.get().lower()))
            notebook.tab(0, text=t('usage', lang_var.get().lower()))
            notebook.tab(1, text=t('features', lang_var.get().lower()))
            notebook.tab(2, text=t('tips', lang_var.get().lower()))
            usage_label.config(text=(t('help_text', lang_var.get().lower()) if 'help_text' in t.__code__.co_varnames or hasattr(t, 'help_text') else """
Image Deduplicator v1.3.0

This application helps you find and manage duplicate images in your folders.

Features:
- Find duplicate images using perceptual hashing
- Select and delete duplicates
- Search subfolders
- Modern user interface with improved layout
- "Select All" functionality for duplicates

Usage:
1. Select a folder containing images
2. Enable "Search subfolders" if you want to scan nested directories
3. Click "Compare Images" to find duplicates
4. Use "Select All" to choose all duplicates at once
5. Review duplicates in the preview window
6. Select multiple duplicates using Ctrl or Shift
7. Delete selected duplicates using the "Delete Selected" button
8. Delete all duplicates using the "Delete All Duplicates" button in the delete buttons section

Supported image formats:
- PNG
- JPG
- JPEG
- GIF
- BMP
- TIFF
- TIF
- WEBP
- SVG
- >PSD


For more information, visit:
https://github.com/Nsfr750/Images-Deduplicator
"""))
            features_label.config(text="""
Features:

1. Image Comparison:
   - Uses perceptual hashing for accurate duplicate detection
   - Handles different image formats and sizes
   - Shows quality comparison between images

2. Batch Operations:
   - Delete selected duplicates
   - Delete all duplicates at once

3. Quality Control:
   - Adjustable quality threshold
   - Visual preview of duplicates
   - Quality score display
""")
            tips_label.config(text="""
Tips:

1. Large Collections:
   - Process images in chunks for better performance
   - Use progress bar to track progress
   - Close and reopen app for large collections

2. Image Formats:
   - Convert all images to same format before comparison
   - Use quality threshold to handle format differences
""")
            close_button.config(text=t('close', lang_var.get().lower()))

        def on_language_change(event=None):
            global LANG
            LANG = lang_var.get().lower()
            refresh_texts()

        lang_menu.bind('<<ComboboxSelected>>', on_language_change)
        refresh_texts()
