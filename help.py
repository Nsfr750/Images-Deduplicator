import tkinter as tk
from tkinter import ttk, messagebox

class Help:
    @staticmethod
    def show_help(parent):
        """Show help window with usage information"""
        help_window = tk.Toplevel(parent)
        help_window.title("Image Deduplicator Help")
        help_window.geometry("600x400")
        
        # Create a notebook for different help sections
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Usage tab
        usage_frame = ttk.Frame(notebook)
        notebook.add(usage_frame, text="Usage")
        
        HELP_TEXT = """
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
"""
        
        usage_label = ttk.Label(usage_frame, text=HELP_TEXT, justify=tk.LEFT)
        usage_label.pack(padx=10, pady=10)
        
        # Features tab
        features_frame = ttk.Frame(notebook)
        notebook.add(features_frame, text="Features")
        
        features_text = """
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
        """
        
        features_label = ttk.Label(features_frame, text=features_text, justify=tk.LEFT)
        features_label.pack(padx=10, pady=10)
        
        # Tips tab
        tips_frame = ttk.Frame(notebook)
        notebook.add(tips_frame, text="Tips")
        
        tips_text = """
        Tips:
        
        1. Large Collections:
           - Process images in chunks for better performance
           - Use progress bar to track progress
           - Close and reopen app for large collections
           
        2. Image Formats:
           - Convert all images to same format before comparison
           - Use quality threshold to handle format differences
        """
        
        tips_label = ttk.Label(tips_frame, text=tips_text, justify=tk.LEFT)
        tips_label.pack(padx=10, pady=10)
        
        # Add close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
