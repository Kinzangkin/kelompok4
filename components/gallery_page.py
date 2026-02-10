import tkinter as tk
from PIL import Image, ImageTk
import os

class GalleryPage:
    def __init__(self, parent_app):
        self.app = parent_app
        self.gallery_thumbnails = []
        
    def show(self):
        """Show gallery page as main content"""
        self.app.clear_main_content()
        
        # Main container
        self.main_container = tk.Frame(self.app.root, bg="#2c3e50")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            self.main_container,
            text="📁 Gallery Gambar",
            font=("Helvetica", 28, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Button frame
        btn_frame = tk.Frame(self.main_container, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_frame,
            text="📷 Ambil Foto",
            command=self.app.show_akuisisi_panel,
            font=("Helvetica", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self.show,
            font=("Helvetica", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        # Gallery frame with scroll
        gallery_frame = tk.Frame(self.main_container, bg="#34495e", relief=tk.SUNKEN, bd=2)
        gallery_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas for scrolling
        self.gallery_canvas = tk.Canvas(gallery_frame, bg="#34495e", highlightthickness=0)
        scrollbar_y = tk.Scrollbar(gallery_frame, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_scrollable_frame = tk.Frame(self.gallery_canvas, bg="#34495e")
        
        self.gallery_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
        )
        
        self.gallery_canvas.create_window((0, 0), window=self.gallery_scrollable_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=scrollbar_y.set)
        
        self.gallery_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        self.gallery_canvas.bind_all("<MouseWheel>", lambda e: self.gallery_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Load gallery images
        self.load_gallery()
    
    def load_gallery(self):
        """Load images from gallery folder"""
        # Clear existing
        for widget in self.gallery_scrollable_frame.winfo_children():
            widget.destroy()
        self.gallery_thumbnails.clear()
        
        # Get image files
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        gallery_images = []
        
        if os.path.exists(self.app.gallery_folder):
            for file in os.listdir(self.app.gallery_folder):
                if file.lower().endswith(image_extensions):
                    gallery_images.append(os.path.join(self.app.gallery_folder, file))
        
        # Sort by modification time (newest first)
        gallery_images.sort(key=os.path.getmtime, reverse=True)
        
        if not gallery_images:
            empty_label = tk.Label(
                self.gallery_scrollable_frame,
                text="📭 Gallery Kosong\n\nKlik 'Ambil Foto' untuk menambah gambar",
                font=("Helvetica", 16),
                bg="#34495e",
                fg="gray",
                justify=tk.CENTER
            )
            empty_label.pack(pady=100, padx=50)
        else:
            # Create grid of thumbnails
            row_frame = None
            for i, img_path in enumerate(gallery_images):
                if i % 4 == 0:
                    row_frame = tk.Frame(self.gallery_scrollable_frame, bg="#34495e")
                    row_frame.pack(fill=tk.X, pady=10, padx=10)
                
                self.create_gallery_item(row_frame, img_path)
        
        self.app.update_status(f"Gallery: {len(gallery_images)} gambar")
    
    def create_gallery_item(self, parent, img_path):
        """Create a gallery item with thumbnail"""
        try:
            # Create frame
            item_frame = tk.Frame(parent, bg="#2c3e50", relief=tk.RAISED, bd=2, cursor="hand2")
            item_frame.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Load thumbnail
            img = Image.open(img_path)
            img.thumbnail((180, 140))
            photo = ImageTk.PhotoImage(img)
            self.gallery_thumbnails.append(photo)
            
            # Image label
            img_label = tk.Label(item_frame, image=photo, bg="#2c3e50")
            img_label.pack(padx=5, pady=5)
            
            # Filename label
            filename = os.path.basename(img_path)
            if len(filename) > 20:
                filename = filename[:17] + "..."
            name_label = tk.Label(
                item_frame,
                text=filename,
                font=("Helvetica", 9),
                bg="#2c3e50",
                fg="white"
            )
            name_label.pack(pady=2)
            
            # Bind click events
            for widget in [item_frame, img_label, name_label]:
                widget.bind("<Button-1>", lambda e, path=img_path: self.app.show_image_detail(path))
            
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
