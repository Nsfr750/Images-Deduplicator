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
        self.create_menu()
        self.setup_styles()

    def create_widgets(self):
        # Progress frame
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_label = tk.Label(self.progress_frame, text="")
        self.progress_label.pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5)
        self.progress_bar['maximum'] = 1000

        # Preview frames
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Duplicate preview
        duplicate_preview_frame = tk.LabelFrame(preview_frame, text="Duplicate Image Preview")
        duplicate_preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.duplicate_preview = tk.Canvas(duplicate_preview_frame, width=400, height=300)
        self.duplicate_preview.pack(pady=10)

        # Original preview
        original_preview_frame = tk.LabelFrame(preview_frame, text="Original Image Preview")
        original_preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_preview = tk.Canvas(original_preview_frame, width=400, height=300)
        self.original_preview.pack(pady=10)

        # Folder selection
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(fill=tk.X, pady=(0, 10))

        folder_label = tk.Label(folder_frame, text="Select Folder:")
        folder_label.pack(side=tk.LEFT, padx=5)

        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Recursive search option
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(folder_frame, text="Search subfolders", variable=self.recursive_var)
        recursive_check.pack(side=tk.LEFT, padx=5)

        # Buttons for actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)

        # Initialize buttons
        self.compare_button = None
        self.delete_button = None
        self.delete_all_button = None
        self.quality_slider = None

        # Create buttons
        self.compare_button = tk.Button(action_frame, text="Compare Images", command=self.compare_images)
        self.compare_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(action_frame, text="Delete Selected", command=self.delete_selected, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.delete_all_button = tk.Button(action_frame, text="Delete All Duplicates", command=self.delete_all_duplicates, state=tk.DISABLED)
        self.delete_all_button.pack(side=tk.LEFT, padx=5)

        # Quality threshold slider
        quality_frame = tk.Frame(self.root)
        quality_frame.pack(fill=tk.X, pady=(10, 0))
        
        quality_label = tk.Label(quality_frame, text="Quality Threshold (0.95):")
        quality_label.pack(side=tk.LEFT, padx=5)
        
        self.quality_slider = ttk.Scale(quality_frame, from_=0.8, to=1.0, value=0.95, orient=tk.HORIZONTAL)
        self.quality_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.quality_slider.bind("<ButtonRelease-1>", self.update_quality_threshold)

        # Listbox for displaying duplicates with multiple selection
        results_frame = tk.Frame(self.root)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.duplicates_listbox = tk.Listbox(results_frame, width=100, height=20, selectmode=tk.EXTENDED)
        self.duplicates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.duplicates_listbox.bind('<<ListboxSelect>>', self.preview_image)
        
        # Add delete selected button above the listbox
        delete_frame = tk.Frame(results_frame)
        delete_frame.pack(fill=tk.X, pady=5)
        
        self.delete_selected_button = tk.Button(delete_frame, text="Delete Selected", 
                                               command=self.delete_selected, 
                                               state=tk.DISABLED)
        self.delete_selected_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_all_button = tk.Button(delete_frame, text="Delete All Duplicates", 
                                          command=self.delete_all_duplicates, 
                                          state=tk.DISABLED)
        self.delete_all_button.pack(side=tk.LEFT, padx=5)

        # Image preview area
        self.preview_label = tk.Label(self.root, text="Image Preview")
        self.preview_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=400, height=300)
        self.canvas.pack()

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

        # Options menu
        options_menu = Menu(menubar, tearoff=0)
        options_menu.add_command(label="Set Quality Threshold", command=self.show_quality_dialog)
        menubar.add_cascade(label="Options", menu=options_menu)

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
            supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')
            image_files = []
            
            if recursive:
                # Use glob to find all image files recursively
                for ext in supported_extensions:
                    pattern = os.path.join(folder, '**', f'*{ext}')
                    image_files.extend(glob.glob(pattern, recursive=True))
            else:
                # Get files from current directory only
                image_files = [os.path.join(folder, f) for f in os.listdir(folder)
                             if f.lower().endswith(supported_extensions)]

            total_files = len(image_files)
            if total_files < 2:
                self.root.after(0, self._comparison_complete, "Not enough images to compare.")
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
                            
                            # Compare quality if threshold is set
                            if self.image_quality_threshold < 1.0:
                                quality = self.compare_image_quality(image, Image.open(original_path))
                                if quality >= self.image_quality_threshold:
                                    duplicates[filepath] = original_path
                            else:
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

                # Calculate and show quality comparison
                quality = self.compare_image_quality(duplicate_img, original_img)
                self.progress_label.config(text=f"Quality: {quality:.2f}")

            except Exception as e:
                error_msg = f"Error loading image: {str(e)}\n\nDetailed error:\n{traceback.format_exc()}"
                messagebox.showerror("Error", error_msg)
                return

    def preview_image(self, event):
        selected_index = self.duplicates_listbox.curselection()
        if selected_index:
            item = self.duplicates_listbox.get(selected_index[0])
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

                # Calculate and show quality comparison
                quality = self.compare_image_quality(duplicate_img, original_img)
                self.progress_label.config(text=f"Quality: {quality:.2f}")

            except Exception as e:
                error_msg = f"Error loading image: {str(e)}\n\nDetailed error:\n{traceback.format_exc()}"
                messagebox.showerror("Error", error_msg)
                return

    def compare_image_quality(self, img1, img2):
        """Compare image quality between two images using mean squared error"""
        img1 = img1.convert('RGB')
        img2 = img2.convert('RGB')
        
        # Resize images to same size if needed
        if img1.size != img2.size:
            img1 = img1.resize(img2.size)
        
        # Calculate mean squared error
        mse = 0
        for band_index in range(len(img1.getbands())):
            band1 = img1.getdata(band_index)
            band2 = img2.getdata(band_index)
            mse += sum((a - b) ** 2 for a, b in zip(band1, band2))
        
        mse /= (img1.size[0] * img1.size[1] * len(img1.getbands()))
        
        # Convert MSE to quality score (0-1)
        quality = 1 - (mse / (255**2))
        return quality

    def update_quality_threshold(self, event):
        self.image_quality_threshold = self.quality_slider.get()
        self.progress_label.config(text=f"Quality Threshold: {self.image_quality_threshold:.2f}")

    def show_quality_dialog(self):
        """Show dialog to set quality threshold"""
        quality = simpledialog.askfloat("Set Quality Threshold",
                                      "Enter quality threshold (0.8 - 1.0):",
                                      minvalue=0.8,
                                      maxvalue=1.0,
                                      initialvalue=self.image_quality_threshold)
        if quality is not None:
            self.quality_slider.set(quality)
            self.image_quality_threshold = quality
            self.progress_label.config(text=f"Quality Threshold: {quality:.2f}")

    def delete_all_duplicates(self):
        """Delete all duplicates at once"""
        if not self.duplicates:
            messagebox.showwarning("Warning", "No duplicates found.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL duplicates?"):
            for duplicate in self.duplicates.keys():
                try:
                    os.remove(duplicate)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete {duplicate}: {str(e)}")
            self.duplicates = {}
            self.display_duplicates()
            self.delete_button.config(state=tk.DISABLED)
            self.delete_all_button.config(state=tk.DISABLED)
            messagebox.showinfo("Info", "All duplicates have been deleted.")

    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat")
        style.configure("TProgressbar", thickness=20)
        style.configure("TScale", sliderlength=20)

    def delete_selected(self):
        selected_indices = self.duplicates_listbox.curselection()
        for index in selected_indices:
            item = self.duplicates_listbox.get(index)
            duplicate_path = item.split(" | ")[0].replace("Duplicate: ", "")
            os.remove(duplicate_path)

        self.compare_images()
        messagebox.showinfo("Info", "Selected duplicates have been deleted.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDeduplicatorApp(root)
    root.mainloop()
