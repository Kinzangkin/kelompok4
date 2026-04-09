import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from datetime import datetime
from components.selectors import CameraSelector

class CameraPanel:
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.camera = None
        self.camera_running = False
        self.captured_image = None
        
    def show_selection(self):
        """Show camera source selection dialog"""
        selector = CameraSelector(
            self.root, 
            "Pilih Sumber Kamera (Ambil Foto)", 
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        """Open the actual camera panel UI"""
        self.akuisisi_window = tk.Toplevel(self.root)
        self.akuisisi_window.title("Ambil Foto")
        self.akuisisi_window.geometry("1100x650")
        self.akuisisi_window.configure(bg="#2c3e50")
        self.akuisisi_window.resizable(False, False)
        
        tk.Label(self.akuisisi_window, text=f"📷 Ambil Foto", font=("Helvetica", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=10)
        
        content_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left: Live View
        self.left_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(self.left_frame, text="🎥 Kamera Live", font=("Helvetica", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
        self.camera_canvas = tk.Canvas(self.left_frame, bg="#1a252f", width=480, height=360)
        self.camera_canvas.pack(padx=10, pady=10)
        
        # Right: Preview
        self.right_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        tk.Label(self.right_frame, text="🖼️ Preview Hasil", font=("Helvetica", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
        self.preview_canvas = tk.Canvas(self.right_frame, bg="#1a252f", width=480, height=360)
        self.preview_canvas.pack(padx=10, pady=10)
        
        self.preview_canvas.create_text(240, 180, text="Belum ada foto\n\nKlik 'Capture' untuk\nmengambil foto", fill="gray", font=("Helvetica", 12), justify=tk.CENTER)
        
        # Buttons
        btn_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, pady=15)
        btn_style = {"font": ("Helvetica", 12, "bold"), "width": 14, "height": 2}
        
        self.capture_btn = tk.Button(btn_frame, text="📷 Capture", command=self.capture_image, bg="#2ecc71", fg="white", **btn_style)
        self.capture_btn.pack(side=tk.LEFT, padx=15, expand=True)
        
        self.save_btn = tk.Button(btn_frame, text="💾 Simpan", command=self.save_captured_image, bg="#3498db", fg="white", state=tk.DISABLED, **btn_style)
        self.save_btn.pack(side=tk.LEFT, padx=15, expand=True)
        
        self.delete_btn = tk.Button(btn_frame, text="🗑️ Hapus", command=self.delete_captured_image, bg="#e74c3c", fg="white", state=tk.DISABLED, **btn_style)
        self.delete_btn.pack(side=tk.LEFT, padx=15, expand=True)
        
        self.back_btn = tk.Button(btn_frame, text="↩️ Kembali", command=self.close_panel, bg="#95a5a6", fg="white", **btn_style)
        self.back_btn.pack(side=tk.LEFT, padx=15, expand=True)
        
        self.start_camera(source)
        self.akuisisi_window.protocol("WM_DELETE_WINDOW", self.close_panel)

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                self.akuisisi_window.destroy()
                return
            self.camera_running = True
            self.app.update_status("Kamera aktif")
            self.update_camera_loop()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.akuisisi_window.destroy()

    def update_camera_loop(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2.resize(frame_rgb, (480, 360)))
                self.tk_img = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(240, 180, image=self.tk_img)
            self.akuisisi_window.after(30, self.update_camera_loop)

    def capture_image(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.captured_image = frame.copy()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2.resize(frame_rgb, (480, 360)))
                self.tk_preview = ImageTk.PhotoImage(img)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(240, 180, image=self.tk_preview)
                self.save_btn.config(state=tk.NORMAL)
                self.delete_btn.config(state=tk.NORMAL)
                self.app.update_status("Foto Captured")

    def save_captured_image(self):
        if self.captured_image is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = os.path.join(self.app.gallery_folder, filename)
            cv2.imwrite(filepath, self.captured_image)
            self.app.update_status(f"Tersimpan: {filename}")
            messagebox.showinfo("Sukses", f"Foto disimpan as {filename}")

    def delete_captured_image(self):
        self.captured_image = None
        self.preview_canvas.delete("all")
        self.save_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.app.update_status("Capture dibatalkan")

    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.akuisisi_window.destroy()
        self.app.show_gallery_page()
