import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
from datetime import datetime
from components.selectors import CameraSelector

class RGBToGrayPanel:
    def __init__(self, main_app):
        self.main_app = main_app
        self.root = main_app.root
        self.camera = None
        self.camera_running = False
        self.captured_frame = None
        self.converted_frame = None
        self.is_converted = False

    def show_selection(self):
        """Show camera selection for RGB to Gray"""
        selector = CameraSelector(
            self.root, 
            "Pilih Sumber Kamera (RGB to Gray)", 
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        """Initialize conversion panel"""
        self.main_app.clear_main_content()
        
        # UI Setup
        self.panel_container = tk.Frame(self.root, bg="#2c3e50")
        self.panel_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(self.panel_container, bg="#2c3e50")
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header, 
            text="🌓 RGB to Grayscale", 
            font=("Helvetica", 24, "bold"), 
            bg="#2c3e50", fg="white"
        ).pack(side=tk.LEFT)
        
        # Main content area (Left: Camera, Right: Info & Result)
        content_frame = tk.Frame(self.panel_container, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- LEFT: CAMERA VIEW ---
        left_frame = tk.Frame(content_frame, bg="#34495e", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Live Camera (RGB)", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=5)
        
        self.camera_canvas = tk.Canvas(left_frame, width=480, height=360, bg="black", highlightthickness=2, highlightbackground="#2980b9")
        self.camera_canvas.pack(pady=5)
        
        # Buttons under camera
        btn_camera_frame = tk.Frame(left_frame, bg="#34495e")
        btn_camera_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_camera_frame, text="📸 Capture", command=self.capture_frame,
            font=("Helvetica", 10, "bold"), bg="#2ecc71", fg="white", height=2
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        tk.Button(
            btn_camera_frame, text="📂 Gallery", command=self.load_from_gallery,
            font=("Helvetica", 10, "bold"), bg="#3498db", fg="white", height=2
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # --- RIGHT: INFO & CONVERSION ---
        right_frame = tk.Frame(content_frame, bg="#34495e", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Preview & Informasi", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=5)
        
        self.preview_canvas = tk.Canvas(right_frame, width=480, height=360, bg="black", highlightthickness=2, highlightbackground="#27ae60")
        self.preview_canvas.pack(pady=5)
        
        # Info Panel (similar to image detail)
        self.info_frame = tk.Frame(right_frame, bg="#2c3e50", padx=15, pady=15)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.info_labels = {}
        for i, (key, label) in enumerate([("name", "Filename: -"), ("size", "Res: -"), ("type", "Mode: RGB")]):
            lbl = tk.Label(self.info_frame, text=label, font=("Helvetica", 10), bg="#2c3e50", fg="#bdc3c7", anchor=tk.W)
            lbl.pack(fill=tk.X)
            self.info_labels[key] = lbl
            
        # Action Buttons
        btn_action_frame = tk.Frame(right_frame, bg="#34495e")
        btn_action_frame.pack(fill=tk.X, pady=10)
        
        self.convert_btn = tk.Button(
            btn_action_frame, text="⚙️ Convert to Gray", command=self.convert_to_gray,
            font=("Helvetica", 12, "bold"), bg="#f1c40f", fg="#2c3e50", state=tk.DISABLED
        )
        self.convert_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.save_btn = tk.Button(
            btn_action_frame, text="💾 Simpan", command=self.save_image,
            font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(
            btn_action_frame, text="↩️ Kembali", command=self.close_panel,
            font=("Helvetica", 12, "bold"), bg="#e74c3c", fg="white"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Start Camera
        self.start_camera(source)

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                self.close_panel()
                return
                
            self.camera_running = True
            self.main_app.update_status("Kamera aktif (RGB Mode)")
            self.update_camera_loop()
        except Exception as e:
            messagebox.showerror("Error", f"Error camera: {str(e)}")
            self.close_panel()

    def update_camera_loop(self):
        if self.camera_running and self.camera:
            if not self.camera_canvas.winfo_exists():
                self.close_panel()
                return
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2.resize(frame_rgb, (480, 360)))
                self.tk_img = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(240, 180, image=self.tk_img)
            self.root.after(30, self.update_camera_loop)

    def load_from_gallery(self):
        """Open image from gallery folder and stop camera"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            initialdir=self.main_app.gallery_folder,
            title="Pilih Gambar",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.bmp"), ("all files", "*.*"))
        )
        
        if file_path:
            # Stop camera first
            self.camera_running = False
            if self.camera:
                self.camera.release()
                self.camera = None
            
            img_bgr = cv2.imread(file_path)
            if img_bgr is not None:
                self.captured_frame = img_bgr
                self.is_converted = False
                
                # Show in PRIMARY (left) canvas
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, (480, 360))
                self.tk_img = ImageTk.PhotoImage(Image.fromarray(img_resized))
                self.camera_canvas.delete("all")
                self.camera_canvas.create_image(240, 180, image=self.tk_img)
                
                # Clear right preview until convert is clicked
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(240, 180, text="Klik 'Convert' untuk\nmelihat hasil", fill="gray", font=("Helvetica", 12), justify=tk.CENTER)
                
                # Update Info
                h, w, _ = img_bgr.shape
                self.info_labels["name"].config(text=f"Filename: {os.path.basename(file_path)}")
                self.info_labels["size"].config(text=f"Res: {w}x{h}")
                self.info_labels["type"].config(text="Mode: RGB (Imported)")
                
                # Enable buttons
                self.convert_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
                self.main_app.update_status(f"Berhasil memuat: {os.path.basename(file_path)}")

    def capture_frame(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.captured_frame = frame.copy()
                self.is_converted = False
                
                # Show in preview
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2.resize(frame_rgb, (480, 360)))
                self.tk_preview = ImageTk.PhotoImage(img)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(240, 180, image=self.tk_preview)
                
                # Update Info
                h, w, _ = frame.shape
                self.info_labels["name"].config(text=f"Filename: capture_{datetime.now().strftime('%H%M%S')}.png")
                self.info_labels["size"].config(text=f"Res: {w}x{h}")
                self.info_labels["type"].config(text="Mode: RGB")
                
                # Enable buttons
                self.convert_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
                self.main_app.update_status("Gambar tercapture. Klik Convert untuk mengubah ke Gray.")

    def convert_to_gray(self):
        if self.captured_frame is not None:
            # Convert to gray
            self.converted_frame = cv2.cvtColor(self.captured_frame, cv2.COLOR_BGR2GRAY)
            self.is_converted = True
            
            # Show gray image in preview
            img_gray = Image.fromarray(cv2.resize(self.converted_frame, (480, 360)))
            self.tk_preview = ImageTk.PhotoImage(img_gray)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(240, 180, image=self.tk_preview)
            
            # Update mode info
            self.info_labels["type"].config(text="Mode: Grayscale")
            self.main_app.update_status("Berhasil dikonversi ke Grayscale.")

    def save_image(self):
        target_frame = self.converted_frame if self.is_converted else self.captured_frame
        if target_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = "gray" if self.is_converted else "rgb"
            filename = f"{mode}_{timestamp}.png"
            filepath = os.path.join(self.main_app.gallery_folder, filename)
            
            cv2.imwrite(filepath, target_frame)
            messagebox.showinfo("Sukses", f"Gambar disimpan ke gallery!\n{filename}")
            self.main_app.update_status(f"Tersimpan: {filename}")

    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.main_app.show_gallery_page()
