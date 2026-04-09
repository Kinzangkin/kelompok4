import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from .utils import format_file_size, open_file_location

class ImageDetailPage:
    def __init__(self, parent_app):
        self.app = parent_app
        
    def show(self, img_path):
        """Show image detail page"""
        self.app.clear_main_content()
        
        # Main container
        detail_container = tk.Frame(self.app.root, bg="#2c3e50")
        detail_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Back button
        back_btn = tk.Button(
            detail_container,
            text="← Kembali ke Gallery",
            command=self.app.show_gallery_page,
            font=("Helvetica", 11),
            bg="#95a5a6",
            fg="white",
            width=20
        )
        back_btn.pack(anchor=tk.W, pady=10)
        
        # Content frame
        content_frame = tk.Frame(detail_container, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Image display
        img_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        img_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Load and display image
        try:
            self.app.current_image = cv2.imread(img_path)
            img_rgb = cv2.cvtColor(self.app.current_image, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            max_size = 500
            h, w = img_rgb.shape[:2]
            ratio = min(max_size / w, max_size / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img_resized = cv2.resize(img_rgb, (new_w, new_h))
            
            pil_img = Image.fromarray(img_resized)
            self.app.photo_image = ImageTk.PhotoImage(pil_img)
            
            img_label = tk.Label(img_frame, image=self.app.photo_image, bg="#34495e")
            img_label.pack(padx=20, pady=20)
            
        except Exception as e:
            error_label = tk.Label(img_frame, text=f"Error: {e}", bg="#34495e", fg="red")
            error_label.pack(pady=50)
        
        # Right: Image info
        info_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2, width=300)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        info_frame.pack_propagate(False)
        
        # Title
        info_title = tk.Label(
            info_frame,
            text="📋 Informasi Gambar",
            font=("Helvetica", 16, "bold"),
            bg="#34495e",
            fg="white"
        )
        info_title.pack(pady=20)
        
        # Get file info
        file_stat = os.stat(img_path)
        filename = os.path.basename(img_path)
        file_ext = os.path.splitext(filename)[1].upper()
        file_size = file_stat.st_size
        
        # Format file size using utility
        size_str = format_file_size(file_size)
        
        # Image dimensions
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                mode = img.mode
        except:
            width, height = 0, 0
            mode = "Unknown"
        
        # File type description
        type_desc = {
            ".PNG": "Portable Network Graphics",
            ".JPG": "JPEG Image",
            ".JPEG": "JPEG Image", 
            ".BMP": "Bitmap Image",
            ".GIF": "Graphics Interchange Format"
        }
        
        # Info items
        info_items = [
            ("Nama File", filename),
            ("Ukuran File", size_str),
            ("Tipe File", file_ext.replace(".", "")),
            ("Jenis File", type_desc.get(file_ext, "Image File")),
            ("Dimensi", f"{width} x {height} px"),
            ("Mode Warna", mode)
        ]
        
        for label, value in info_items:
            item_frame = tk.Frame(info_frame, bg="#34495e")
            item_frame.pack(fill=tk.X, padx=20, pady=8)
            
            tk.Label(
                item_frame,
                text=label,
                font=("Helvetica", 10),
                bg="#34495e",
                fg="#bdc3c7"
            ).pack(anchor=tk.W)
            
            tk.Label(
                item_frame,
                text=value,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="white",
                wraplength=250
            ).pack(anchor=tk.W)
        
        # Button frame for actions
        btn_action_frame = tk.Frame(info_frame, bg="#34495e")
        btn_action_frame.pack(pady=20)
        
        # Open location button
        open_loc_btn = tk.Button(
            btn_action_frame,
            text="📂 Buka Lokasi File",
            command=lambda: open_file_location(img_path),
            font=("Helvetica", 11),
            bg="#3498db",
            fg="white",
            width=18
        )
        open_loc_btn.pack(pady=5)
        
        # Delete button
        delete_btn = tk.Button(
            btn_action_frame,
            text="🗑️ Hapus Gambar",
            command=lambda: self.delete_gallery_image(img_path),
            font=("Helvetica", 11),
            bg="#e74c3c",
            fg="white",
            width=18
        )
        delete_btn.pack(pady=5)
        
        self.app.update_status(f"Detail: {filename}")

    def delete_gallery_image(self, img_path):
        """Delete image from gallery"""
        filename = os.path.basename(img_path)
        confirm = messagebox.askyesno("Konfirmasi", f"Hapus gambar '{filename}'?")
        if confirm:
            try:
                os.remove(img_path)
                self.app.update_status(f"Gambar dihapus: {filename}")
                self.app.show_gallery_page()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")
