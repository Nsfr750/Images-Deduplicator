import os
import tkinter as tk
from tkinter import filedialog, messagebox, Button, Tk, Label, Menu
from PIL import Image, ImageTk
import imagehash

class Sponsor:
    root = Tk()
    root.geometry("300x150")
    root.title("Sponsor")

    title_label = Label(root, text="Socials", font=("Arial", 16))
    title_label.pack(pady=10)

    def open_patreon():
        import webbrowser
        webbrowser.open("https://www.patreon.com/Nsfr750")

    def open_github():
        import webbrowser
        webbrowser.open("https://github.com/sponsors/Nsfr750")

    def open_discord():    
        import webbrowser
        webbrowser.open("https://discord.gg/q5Pcgrju")
        
    # Create and place buttons
    patreon_button = Button(root, text="Join the Patreon!", command=open_patreon)
    patreon_button.pack(pady=10)

    github_button = Button(root, text="GitHub", command=open_github)
    github_button.pack(pady=10)

    discord_button = Button(root, text="Discord", command=open_discord)
    discord_button.pack(pady=10)

    root.mainloop()

class ImageDeduplicatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Deduplicator")
        self.root.geometry("1000x800")

        self.folder_path = tk.StringVar()

        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        # Folder selection
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10)
        
        folder_label = tk.Label(folder_frame, text="Select Folder:")
        folder_label.pack(side=tk.LEFT, padx=5)
        
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5)
        
        browse_button = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(side=tk.LEFT, padx=5)

        # Buttons for actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        
        compare_button = tk.Button(action_frame, text="Compare Images", command=self.compare_images)
        compare_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(action_frame, text="Delete Selected", command=self.delete_selected)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Listbox for displaying duplicates
        self.duplicates_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, width=100, height=20)
        self.duplicates_listbox.pack(pady=10)
        self.duplicates_listbox.bind('<<ListboxSelect>>', self.preview_image)

        # Image preview area
        self.preview_label = tk.Label(self.root, text="Image Preview")
        self.preview_label.pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=400, height=300)
        self.canvas.pack()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        messagebox.showinfo("About", "Image Deduplicator v1.0\nDeveloped by Nsfr750")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
    
    def compare_images(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        
        # Compare images and find duplicates
        self.duplicates = self.find_duplicates(folder)
        self.display_duplicates()

    def find_duplicates(self, folder):
        images = {}
        duplicates = {}
        
        for filename in os.listdir(folder):
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif')):
                filepath = os.path.join(folder, filename)
                image = Image.open(filepath)
                hash_value = imagehash.average_hash(image)
                
                if hash_value in images:
                    duplicates[filepath] = images[hash_value]
                else:
                    images[hash_value] = filepath
        
        return duplicates
    
    def display_duplicates(self):
        self.duplicates_listbox.delete(0, tk.END)
        
        for duplicate, original in self.duplicates.items():
            self.duplicates_listbox.insert(tk.END, f"Duplicate: {duplicate} | Original: {original}")
    
    def preview_image(self, event):
        selected_index = self.duplicates_listbox.curselection()
        if selected_index:
            item = self.duplicates_listbox.get(selected_index)
            duplicate_path = item.split(" | ")[0].replace("Duplicate: ", "")
            image = Image.open(duplicate_path)
            image.thumbnail((400, 300))
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

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