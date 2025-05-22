import tkinter as tk
from tkinter import ttk

def setup_styles():
    """Setup custom styles for the application"""
    style = ttk.Style()
    
    # Modern button style
    style.configure("TButton", 
                   padding=10,
                   font=('Segoe UI', 10))
    
    # Progress bar style
    style.configure("TProgressbar",
                   thickness=20)
    
    # Scale style
    style.configure("TScale",
                   sliderlength=20)
    
    # Listbox style
    style.configure("TListbox",
                   background='#ffffff',
                   foreground='#333333',
                   font=('Segoe UI', 10))
    
    # Label style
    style.configure("TLabel",
                   font=('Segoe UI', 10),
                   foreground='#333333')
    
    # Frame style
    style.configure("TFrame",
                   background='#ffffff')
    
    # Entry style
    style.configure("TEntry",
                   fieldbackground='#ffffff',
                   foreground='#333333',
                   font=('Segoe UI', 10))
    
    # Checkbutton style
    style.configure("TCheckbutton",
                   font=('Segoe UI', 10),
                   foreground='#333333')
    
    # Configure color scheme
    style.theme_use("clam")
    style.configure("." ,
                   background='#ffffff',
                   foreground='#333333')
    
    return style
