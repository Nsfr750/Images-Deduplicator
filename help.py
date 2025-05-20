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
        
        usage_text = """
        Usage Guide:
        
        1. Select Folder:
           - Click "Browse" to select a folder containing images
           - The app supports PNG, JPG, JPEG, GIF, BMP, TIFF, and TIF formats
           
        2. Compare Images:
           - Click "Compare Images" to find duplicates
           - The app uses image hashing to identify duplicates
           - Progress bar shows comparison progress
           
        3. Preview Images:
           - Select a duplicate from the list to preview both images
           - Left side shows the duplicate image
           - Right side shows the original image
           - Quality score shows similarity between images
        """
        
        usage_label = ttk.Label(usage_frame, text=usage_text, justify=tk.LEFT)
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
        
        1. Quality Threshold:
           - Lower values (0.8-0.9) find more similar images
           - Higher values (0.95-1.0) find exact duplicates
           - Adjust based on your needs
           
        2. Large Collections:
           - Process images in chunks for better performance
           - Use progress bar to track progress
           - Close and reopen app for large collections
           
        3. Image Formats:
           - Convert all images to same format before comparison
           - Use quality threshold to handle format differences
        """
        
        tips_label = ttk.Label(tips_frame, text=tips_text, justify=tk.LEFT)
        tips_label.pack(padx=10, pady=10)
        
        # Add close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
