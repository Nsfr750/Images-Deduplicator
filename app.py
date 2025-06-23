import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Button, Tk, Label, Menu, simpledialog
from PIL import Image, ImageTk
import imagehash
from about import About
from sponsor import Sponsor
from version import get_version, __version__
from help import Help
import queue
import traceback
from pathlib import Path
import glob
import threading
from updates import UpdateChecker, check_for_updates
from translations import t, LANGUAGES

class ImageDeduplicatorApp:
    def set_language(self, lang_code):
        self.lang = lang_code
        self.update_ui_language()

    def update_ui_language(self):
        # Update window title
        self.root.title(t('app_title', self.lang, version=get_version()))
        # Rebuild menu
        self.create_menu()
        # Update all labels/buttons
        self.select_all_button.config(text=t('select_all', self.lang))
        self.delete_selected_button.config(text=t('delete_selected', self.lang))
        self.delete_all_button.config(text=t('delete_all_duplicates', self.lang))
        self.browse_button.config(text=t('browse', self.lang))
        self.compare_button.config(text=t('compare_images', self.lang))
        # Update folder label
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Label) and subchild.cget('text') in [t('select_folder', l) for l in LANGUAGES]:
                        subchild.config(text=t('select_folder', self.lang))
        # Update checkbutton
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Checkbutton):
                        subchild.config(text=t('search_subfolders', self.lang))
        # Update preview frames
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.LabelFrame):
                        if 'duplicate' in subchild.cget('text').lower():
                            subchild.config(text=t('duplicate_image_preview', self.lang))
                        elif 'original' in subchild.cget('text').lower():
                            subchild.config(text=t('original_image_preview', self.lang))
        # If progress label is showing a known phrase, update it
        if self.progress_label.cget('text') in [t('processing_images', l) for l in LANGUAGES]:
            self.progress_label.config(text=t('processing_images', self.lang))

    def __init__(self, root):
        self.root = root
        self.lang = 'en'
        self.root.title(t('app_title', self.lang, version=get_version()))
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
        self.update_checker = None

        self.create_widgets()
        self.setup_styles()
        self.create_menu()

        # Initialize update checker
        self.update_checker = UpdateChecker(__version__)

        # Check for updates on startup
        self.root.after(1000, self.check_for_updates_on_startup)

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
                                           text=t('select_all', self.lang),
                                           command=self.select_all_duplicates,
                                           style='TButton')
        self.select_all_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_selected_button = ttk.Button(buttons_frame, 
                                                text=t('delete_selected', self.lang),
                                                command=self.delete_selected,
                                                state=tk.DISABLED,
                                                style='TButton')
        self.delete_selected_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_all_button = ttk.Button(buttons_frame, 
                                           text=t('delete_all_duplicates', self.lang),
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
                                               text=t('duplicate_image_preview', self.lang),
                                               style='TFrame')
        duplicate_preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.duplicate_preview = tk.Canvas(duplicate_preview_frame, 
                                          width=400, 
                                          height=300,
                                          bg='#f8f9fa')
        self.duplicate_preview.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Original preview with reduced spacing
        original_preview_frame = ttk.LabelFrame(preview_frame, 
                                              text=t('original_image_preview', self.lang),
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
        
        folder_label = ttk.Label(folder_left, text=t('select_folder', self.lang))
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
                                       text=t('browse', self.lang),
                                       command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # Recursive search option
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(folder_right, 
                                        text=t('search_subfolders', self.lang),
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
                                       text=t('compare_images', self.lang),
                                       command=self.compare_images,
                                       style='TButton')
        self.compare_button.pack(side=tk.LEFT, padx=5)



    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label=t('exit', self.lang), command=self.root.quit)
        menubar.add_cascade(label=t('file', self.lang), menu=file_menu)

        # Language menu
        language_menu = Menu(menubar, tearoff=0)
        language_menu.add_radiobutton(label='English', command=lambda: self.set_language('en'))
        language_menu.add_radiobutton(label='Español', command=lambda: self.set_language('es'))
        language_menu.add_radiobutton(label='Français', command=lambda: self.set_language('fr'))
        language_menu.add_radiobutton(label='Deutsch', command=lambda: self.set_language('de'))
        language_menu.add_radiobutton(label='Português', command=lambda: self.set_language('pt'))
        language_menu.add_radiobutton(label='Italiano', command=lambda: self.set_language('it'))
        menubar.add_cascade(label=t('language', self.lang), menu=language_menu)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label=t('check_for_updates', self.lang), command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label=t('help', self.lang), command=lambda: Help.show_help(self.root))
        help_menu.add_command(label=t('about', self.lang), command=self.show_about)
        help_menu.add_command(label=t('sponsor', self.lang), command=self.open_sponsor)
        menubar.add_cascade(label=t('help', self.lang), menu=help_menu)

    def open_sponsor(self):
        sponsor = Sponsor(self.root)
        sponsor.show_sponsor()

    def check_for_updates(self, force_check=False):
        """Check for updates and show a dialog if an update is available."""
        try:
            update_available, update_info = self.update_checker.check_for_updates(
                parent=self.root,
                force_check=force_check
            )
            if update_available and update_info:
                self.update_checker.show_update_dialog(self.root, update_info)
        except Exception as e:
            messagebox.showerror(
                t('error', self.lang),
                f"{t('update_check_failed', self.lang)}: {str(e)}",
                parent=self.root
            )
    
    def check_for_updates_on_startup(self):
        """Check for updates on application startup."""
        try:
            self.update_checker.check_for_updates(
                parent=self.root,
                force_check=False
            )
        except Exception:
            # Don't show errors during startup to avoid annoying the user
            pass
    
    def show_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title(t('about', self.lang))
        about_dialog.geometry('500x400')
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        about_dialog.resizable(False, False)

        # Main container
        main_frame = ttk.Frame(about_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App title and version
        title = ttk.Label(
            main_frame,
            text='Image Deduplicator',
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(pady=(0, 10))

        version = ttk.Label(
            main_frame,
            text=f"{t('version', self.lang)}: {get_version()}"
        )
        version.pack()

        # Description
        description = ttk.Label(
            main_frame,
            text=t('about_description', self.lang),
            wraplength=450,
            justify=tk.CENTER
        )
        description.pack(pady=20)

        # Features
        features_frame = ttk.LabelFrame(main_frame, text=t('features', self.lang))
        features_frame.pack(fill=tk.X, padx=20, pady=10)

        features = [
            t('feature_1', self.lang),
            t('feature_2', self.lang),
            t('feature_3', self.lang),
            t('feature_4', self.lang)
        ]

        for feature in features:
            ttk.Label(
                features_frame,
                text=f"• {feature}",
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=2)

        # Copyright
        copyright_frame = ttk.Frame(main_frame)
        copyright_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        ttk.Label(
            copyright_frame,
            text=f"© 2025 Nsfr750"
        ).pack()

        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        ttk.Button(
            button_frame,
            text=t('close', self.lang),
            command=about_dialog.destroy
        ).pack()

        # Center the dialog
        about_dialog.update_idletasks()
        width = about_dialog.winfo_width()
        height = about_dialog.winfo_height()
        x = (about_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (height // 2)
        about_dialog.geometry(f'{width}x{height}+{x}+{y}')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            messagebox.showinfo(t('folder_selected', self.lang), t('selected_folder', self.lang, folder=folder_selected))

    def compare_images(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning(t('warning', self.lang), t('please_select_folder', self.lang))
            return

        if self.comparison_in_progress:
            messagebox.showwarning(t('warning', self.lang), t('comparison_in_progress', self.lang))
            return

        self.comparison_in_progress = True
        if self.compare_button:
            self.compare_button.config(state=tk.DISABLED)
        self.progress_label.config(text=t('processing_images', self.lang))
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
                error_msg = t('found_images', self.lang, count=total_files)
                if total_files == 1:
                    error_msg += '\n' + t('found_image', self.lang, image=os.path.basename(image_files[0]))
                elif total_files == 0:
                    error_msg += '\n' + t('no_images_found', self.lang, exts=', '.join(supported_extensions))
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

            self.root.after(0, self._comparison_complete, t('found_duplicates', self.lang, count=len(duplicates)))
            self.root.after(0, self._update_duplicates, duplicates)

        except Exception as e:
            self.root.after(0, self._comparison_error, t('error_comparison', self.lang, error=str(e)))
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
            self.duplicates_listbox.insert(tk.END, f"{t('duplicate', self.lang)}: {duplicate} | {t('original', self.lang)}: {original}")
        
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
                error_msg = t('error_loading_image', self.lang, error=str(e), trace=traceback.format_exc())
                messagebox.showerror(t('error', self.lang), error_msg)
                return

    def select_all_duplicates(self):
        """Select all duplicates in the listbox"""
        self.duplicates_listbox.selection_set(0, tk.END)
        self.delete_selected_button.config(state=tk.NORMAL)  # Enable delete selected button

    def delete_all_duplicates(self):
        """Delete all duplicates at once"""
        if not self.duplicates:
            messagebox.showwarning(t('warning', self.lang), t('no_duplicates_found', self.lang))
            return

        if messagebox.askyesno(t('confirm_delete_all', self.lang), t('confirm_delete_all', self.lang)):
            failed_deletions = []
            for duplicate in self.duplicates.keys():
                try:
                    os.remove(duplicate)
                except Exception as e:
                    failed_deletions.append(f"{duplicate}: {str(e)}")
            
            if failed_deletions:
                error_msg = "\n".join(failed_deletions)
                messagebox.showerror(t('error', self.lang), t('failed_to_delete', self.lang, error=error_msg))
            
            # Clear duplicates and update UI
            self.duplicates = {}
            self.display_duplicates()
            self.delete_selected_button.config(state=tk.DISABLED)
            self.delete_all_button.config(state=tk.DISABLED)
            
            success_count = len(self.duplicates_listbox.get(0, tk.END))
            if success_count > 0:
                messagebox.showinfo(t('info', self.lang), t('successfully_deleted', self.lang, count=success_count))
            else:
                messagebox.showinfo(t('info', self.lang), t('all_deleted', self.lang))

    def delete_selected(self):
        selected_indices = self.duplicates_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(t('warning', self.lang), t('no_items_selected', self.lang))
            return

        num_selected = len(selected_indices)
        if num_selected > 1:
            message = t('confirm_delete_selected', self.lang, count=num_selected)
        else:
            message = t('confirm_delete_one', self.lang)

        if messagebox.askyesno(t('confirm_delete_all', self.lang), message):
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
                messagebox.showerror(t('error', self.lang), t('failed_to_delete_items', self.lang, count=failed_count, error=error_message))
            else:
                if deleted_count > 1:
                    messagebox.showinfo(t('info', self.lang), t('successfully_deleted', self.lang, count=deleted_count))
                else:
                    messagebox.showinfo(t('info', self.lang), t('successfully_deleted_one', self.lang))

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
