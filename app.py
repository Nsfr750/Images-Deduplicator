import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Button, Tk, Label, Menu, simpledialog
from PIL import Image, ImageTk
import imagehash
from about import About
from sponsor import Sponsor
from version import get_version
from help import Help
import queue
import traceback
from pathlib import Path
import glob
import threading
from version import get_version

class ImageDeduplicatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Image Deduplicator v{get_version()}")
        self.root.geometry("1000x800")
        self.root.minsize(1000, 800)

        self.folder_path = tk.StringVar()
        self.copied_files = []
        self.duplicates = {}
        self.comparison_queue = queue.Queue()
        self.comparison_in_progress = False
        self.image_quality_threshold = 0.95
        self.duplicate_photo = None
        self.original_photo = None
        self.duplicate_preview = None
        self.original_preview = None
        self.progress_label = None
        self.progress_bar = None

        self.create_widgets()
        self.setup_styles()
        self.create_menu()

    def create_widgets(self):
        # Progress frame
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Progress label with better styling
        self.progress_label = ttk.Label(self.progress_frame, 
                                      text="",
                                      font=('Segoe UI', 10, 'bold'))
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar with better styling
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          mode='determinate', 
                                          style='TProgressbar')
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_bar['maximum'] = 1000

        # Create results frame with scrollbar
        results_frame = ttk.Frame(self.root)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        # Create listbox for duplicates with better styling
        self.duplicates_listbox = tk.Listbox(results_frame, 
                                            selectmode=tk.EXTENDED,
                                            font=('Segoe UI', 10))
        self.duplicates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.duplicates_listbox.bind('<<ListboxSelect>>', self.preview_image)
        
        # Add scrollbar to listbox
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.duplicates_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.duplicates_listbox.configure(yscrollcommand=scrollbar.set)

        # Create delete buttons frame
        delete_buttons_frame = ttk.Frame(self.root)
        delete_buttons_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Create buttons frame with select all and delete buttons
        buttons_frame = ttk.Frame(delete_buttons_frame)
        buttons_frame.pack(side=tk.LEFT, padx=5)
        
        self.select_all_button = ttk.Button(buttons_frame, 
                                           text="Select All",
                                           command=self.select_all_duplicates,
                                           style='TButton')
        self.select_all_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_selected_button = ttk.Button(buttons_frame, 
                                                text="Delete Selected",
                                                command=self.delete_selected,
                                                state=tk.DISABLED,
                                                style='TButton')
        self.delete_selected_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_all_button = ttk.Button(buttons_frame, 
                                           text="Delete All Duplicates",
                                           command=self.delete_all_duplicates,
                                           state=tk.DISABLED,
                                           style='TButton')
        self.delete_all_button.pack(side=tk.LEFT, padx=2)

        # Preview frames with reduced spacing
        preview_frame = ttk.Frame(self.root)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=5)

        # Adjust padding to accommodate scrollbar
        preview_frame.pack_configure(pady=(0, 5), padx=5, expand=True)
        
        # Add a separator between preview frames
        ttk.Separator(preview_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Duplicate preview with reduced spacing
        duplicate_preview_frame = ttk.LabelFrame(preview_frame, 
                                               text="Duplicate Image Preview",
                                               style='TFrame')
        duplicate_preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.duplicate_preview = tk.Canvas(duplicate_preview_frame, 
                                          width=400, 
                                          height=300,
                                          bg='#f8f9fa')
        self.duplicate_preview.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Original preview with reduced spacing
        original_preview_frame = ttk.LabelFrame(preview_frame, 
                                              text="Original Image Preview",
                                              style='TFrame')
        original_preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.original_preview = tk.Canvas(original_preview_frame, 
                                         width=400, 
                                         height=300,
                                         bg='#f8f9fa')
        self.original_preview.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Folder selection with better layout
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Left side of folder frame
        folder_left = ttk.Frame(folder_frame)
        folder_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        folder_label = ttk.Label(folder_left, text="Select Folder:")
        folder_label.pack(side=tk.LEFT, padx=5)
        
        folder_entry = ttk.Entry(folder_left, 
                                textvariable=self.folder_path, 
                                width=50,
                                style='TEntry')
        folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Right side of folder frame
        folder_right = ttk.Frame(folder_frame)
        folder_right.pack(side=tk.LEFT)
        
        self.browse_button = ttk.Button(folder_right, 
                                       text="Browse",
                                       command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # Recursive search option
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(folder_right, 
                                        text="Search subfolders",
                                        variable=self.recursive_var)
        recursive_check.pack(side=tk.LEFT, padx=5)

        # Buttons for actions with better layout
        action_frame = ttk.Frame(self.root)
        action_frame.pack(pady=10, padx=10, fill=tk.X)

        # Initialize buttons
        self.compare_button = None
        self.delete_button = None

        # Create buttons with better styling
        self.compare_button = ttk.Button(action_frame, 
                                       text="Compare Images",
                                       command=self.compare_images,
                                       style='TButton')
        self.compare_button.pack(side=tk.LEFT, padx=5)



    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Folder", command=self.browse_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Compare Images", command=self.compare_images)
        tools_menu.add_command(label="Delete Selected", command=self.delete_selected)
        tools_menu.add_command(label="Delete All Duplicates", command=self.delete_all_duplicates)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=lambda: Help.show_help(self.root))
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Show Sponsor", command=self.open_sponsor)
        menubar.add_cascade(label="Help", menu=help_menu)

    def open_sponsor(self):
        sponsor = Sponsor(self.root)
        sponsor.show_sponsor()

    def show_about(self):
        About.show_about(self.root)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            messagebox.showinfo("Folder Selected", f"Selected folder: {folder_selected}")

    def compare_images(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return

        if self.comparison_in_progress:
            messagebox.showwarning("Warning", "Comparison is already in progress.")
            return

        self.comparison_in_progress = True
        if self.compare_button:
            self.compare_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Processing images...")
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100

        # Start comparison in a separate thread
        threading.Thread(target=self._compare_images_thread, args=(folder, self.recursive_var.get()), daemon=True).start()

    def _compare_images_thread(self, folder, recursive=True):
        try:
            # Get all image files using recursive search
            supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.psd', '.webp', '.svg')
            image_files = []
            
            # Normalize folder path to ensure correct path handling
            folder = os.path.abspath(folder)
            
            if recursive:
                # Use os.walk for more reliable recursive search
                for root, _, files in os.walk(folder):
                    for f in files:
                        if f.lower().endswith(supported_extensions):
                            full_path = os.path.join(root, f)
                            if os.path.isfile(full_path):
                                image_files.append(full_path)
            else:
                # Get files from current directory only
                try:
                    for f in os.listdir(folder):
                        if f.lower().endswith(supported_extensions):
                            full_path = os.path.join(folder, f)
                            if os.path.isfile(full_path):
                                image_files.append(full_path)
                except OSError as e:
                    raise Exception(f"Error accessing folder {folder}: {str(e)}")

            # Remove duplicates and sort for consistent processing
            image_files = list(set(image_files))
            image_files.sort()

            total_files = len(image_files)
            if total_files < 2:
                error_msg = f"Found {total_files} image(s) in the selected folder. Need at least 2 images to compare."
                if total_files == 1:
                    error_msg += f"\nFound image: {os.path.basename(image_files[0])}"
                elif total_files == 0:
                    error_msg += "\nNo images found with supported extensions: " + ", ".join(supported_extensions)
                self.root.after(0, self._comparison_complete, error_msg)
                return

            # Process images in chunks
            chunk_size = 10
            images = {}
            duplicates = {}
            processed_count = 0

            for i in range(0, len(image_files), chunk_size):
                chunk = image_files[i:i + chunk_size]
                for filepath in chunk:
                    try:
                        # Skip if file doesn't exist or is not a file
                        if not os.path.isfile(filepath):
                            continue

                        # Skip if file is too large (prevent memory issues)
                        if os.path.getsize(filepath) > 100 * 1024 * 1024:  # 100MB limit
                            print(f"Skipping large file {filepath}")
                            continue

                        image = Image.open(filepath)
                        hash_value = imagehash.average_hash(image)
                        
                        # Check for duplicates based on hash
                        if hash_value in images:
                            original_path = images[hash_value]
                            duplicates[filepath] = original_path
                        else:
                            images[hash_value] = filepath
                        
                        processed_count += 1
                        progress = (processed_count / total_files) * 100
                        self.root.after(0, self._update_progress, progress)
                    except Exception as e:
                        print(f"Skipping file {filepath}: {str(e)}")
                        continue

            self.root.after(0, self._comparison_complete, f"Found {len(duplicates)} duplicate images.")
            self.root.after(0, self._update_duplicates, duplicates)

        except Exception as e:
            self.root.after(0, self._comparison_error, f"Error during comparison: {str(e)}")
        finally:
            self.root.after(0, self._reset_ui)

    def _update_progress(self, progress):
        self.progress_bar['value'] = progress

    def _comparison_complete(self, message):
        self.progress_label.config(text=message)
        self.comparison_in_progress = False
        self.compare_button.config(state=tk.NORMAL)

    def _comparison_error(self, message):
        self.progress_label.config(text=message)
        self.comparison_in_progress = False
        self.compare_button.config(state=tk.NORMAL)

    def _reset_ui(self):
        self.progress_bar['value'] = 0

    def _update_duplicates(self, duplicates):
        self.duplicates = duplicates
        self.display_duplicates()

    def display_duplicates(self):
        self.duplicates_listbox.delete(0, tk.END)
        
        for duplicate, original in self.duplicates.items():
            self.duplicates_listbox.insert(tk.END, f"Duplicate: {duplicate} | Original: {original}")
        
        # Update button states
        if self.duplicates:
            self.delete_selected_button.config(state=tk.NORMAL)
            self.delete_all_button.config(state=tk.NORMAL)
        else:
            self.delete_selected_button.config(state=tk.DISABLED)
            self.delete_all_button.config(state=tk.DISABLED)

    def preview_image(self, event):
        selected_indices = self.duplicates_listbox.curselection()
        if selected_indices:
            # Update delete button state based on selection
            self.delete_selected_button.config(state=tk.NORMAL if selected_indices else tk.DISABLED)
            
            # Only show preview for the last selected item
            item = self.duplicates_listbox.get(selected_indices[-1])
            duplicate_path = item.split(" | ")[0].replace("Duplicate: ", "")
            original_path = item.split(" | ")[1].replace("Original: ", "")

            try:
                # Load and preview duplicate image
                duplicate_img = Image.open(duplicate_path)
                duplicate_img.thumbnail((400, 300))
                self.duplicate_photo = ImageTk.PhotoImage(duplicate_img)
                
                # Load and preview original image
                original_img = Image.open(original_path)
                original_img.thumbnail((400, 300))
                self.original_photo = ImageTk.PhotoImage(original_img)

                # Update preview canvases
                if self.duplicate_preview:
                    self.duplicate_preview.delete("all")
                    self.duplicate_preview.create_image(0, 0, anchor=tk.NW, image=self.duplicate_photo)
                    self.duplicate_preview.image = self.duplicate_photo
                
                if self.original_preview:
                    self.original_preview.delete("all")
                    self.original_preview.create_image(0, 0, anchor=tk.NW, image=self.original_photo)
                    self.original_preview.image = self.original_photo

            except Exception as e:
                error_msg = f"Error loading image: {str(e)}\n\nDetailed error:\n{traceback.format_exc()}"
                messagebox.showerror("Error", error_msg)
                return

    def select_all_duplicates(self):
        """Select all duplicates in the listbox"""
        self.duplicates_listbox.selection_set(0, tk.END)
        self.delete_selected_button.config(state=tk.NORMAL)  # Enable delete selected button

    def delete_all_duplicates(self):
        """Delete all duplicates at once"""
        if not self.duplicates:
            messagebox.showwarning("Warning", "No duplicates found.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL duplicates?"):
            failed_deletions = []
            for duplicate in self.duplicates.keys():
                try:
                    os.remove(duplicate)
                except Exception as e:
                    failed_deletions.append(f"{duplicate}: {str(e)}")
            
            if failed_deletions:
                error_msg = "\n".join(failed_deletions)
                messagebox.showerror("Error", f"Failed to delete some duplicates:\n\n{error_msg}")
            
            # Clear duplicates and update UI
            self.duplicates = {}
            self.display_duplicates()
            self.delete_selected_button.config(state=tk.DISABLED)
            self.delete_all_button.config(state=tk.DISABLED)
            
            success_count = len(self.duplicates_listbox.get(0, tk.END))
            if success_count > 0:
                messagebox.showinfo("Info", f"Successfully deleted {success_count} duplicates.")
            else:
                messagebox.showinfo("Info", "All duplicates have been deleted.")

    def delete_selected(self):
        selected_indices = self.duplicates_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No items selected")
            return

        num_selected = len(selected_indices)
        if num_selected > 1:
            message = f"Are you sure you want to delete {num_selected} selected duplicates?"
        else:
            message = "Are you sure you want to delete the selected duplicate?"

        if messagebox.askyesno("Confirm Delete", message):
            deleted_count = 0
            failed_count = 0
            failed_items = []
            
            for index in selected_indices:
                try:
                    item = self.duplicates_listbox.get(index)
                    duplicate_path = item.split(" | ")[0].replace("Duplicate: ", "")
                    os.remove(duplicate_path)
                    deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_items.append(f"{duplicate_path}: {str(e)}")

            # Update duplicates dictionary
            self.duplicates = {
                k: v for k, v in self.duplicates.items()
                if k not in [self.duplicates_listbox.get(i).split(" | ")[0].replace("Duplicate: ", "") 
                           for i in selected_indices]
            }
            
            self.display_duplicates()
            
            if failed_count > 0:
                error_message = "\n".join(failed_items)
                messagebox.showerror("Error", f"Failed to delete {failed_count} items:\n\n{error_message}")
            else:
                if deleted_count > 1:
                    messagebox.showinfo("Info", f"Successfully deleted {deleted_count} duplicates.")
                else:
                    messagebox.showinfo("Info", "Successfully deleted the duplicate.")

    def setup_styles(self):
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
        
        self.root.configure(bg='#ffffff')


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDeduplicatorApp(root)
    root.mainloop()
