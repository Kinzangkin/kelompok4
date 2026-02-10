import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from components.utils import get_color_name
from components.selectors import CameraSelector

class ScanPanel:
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.camera = None
        self.camera_running = False

    def show_selection(self):
        """Show camera selection for Scan Object"""
        selector = CameraSelector(
            self.root, 
            "Pilih Sumber Kamera (Scan Object)", 
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        """Show color scanning panel"""
        self.akuisisi_window = tk.Toplevel(self.root)
        self.akuisisi_window.title("Scan Object (Warna)")
        self.akuisisi_window.geometry("1100x650")
        self.akuisisi_window.configure(bg="#2c3e50")
        self.akuisisi_window.resizable(False, False)
        
        tk.Label(self.akuisisi_window, text="🔍 Scan Deteksi Warna", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=10)
        
        content_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left: Camera view
        left_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(left_frame, text="Area Scan (Kotak Tengah)", font=("Helvetica", 12, "bold"), bg="#34495e", fg="white").pack(pady=5)
        self.camera_canvas = tk.Canvas(left_frame, bg="#1a252f", width=480, height=360)
        self.camera_canvas.pack(padx=10, pady=10)
        
        # Right: Result view
        right_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        tk.Label(right_frame, text="Hasil Deteksi", font=("Helvetica", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
        
        self.color_preview = tk.Label(right_frame, bg="#1a252f", width=30, height=8, relief=tk.RAISED)
        self.color_preview.pack(pady=20)
        
        self.result_label = tk.Label(right_frame, text="Siap Scan...", font=("Helvetica", 18, "bold"), bg="#34495e", fg="#bdc3c7")
        self.result_label.pack(pady=10)
        
        self.rgb_label = tk.Label(right_frame, text="", font=("Helvetica", 10), bg="#34495e", fg="white")
        self.rgb_label.pack()
        
        # Buttons
        btn_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, pady=15)
        btn_style = {"font": ("Helvetica", 12, "bold"), "width": 14, "height": 2}
        
        tk.Button(btn_frame, text="🔍 Scan Warna", command=self.scan_object_color, bg="#f1c40f", fg="#2c3e50", **btn_style).pack(side=tk.LEFT, padx=20, expand=True)
        tk.Button(btn_frame, text="↩️ Kembali", command=self.close_panel, bg="#95a5a6", fg="white", **btn_style).pack(side=tk.LEFT, padx=20, expand=True)
        
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
            self.app.update_status("Kamera Aktif (Scan Mode)")
            self.update_camera_loop()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.akuisisi_window.destroy()

    def update_camera_loop(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_disp = cv2.resize(frame_rgb, (480, 360))
                
                # Draw Target Box on display frame
                cx, cy = 240, 180
                size = 50
                cv2.rectangle(frame_disp, (cx-size, cy-size), (cx+size, cy+size), (241, 196, 15), 2)
                
                img = Image.fromarray(frame_disp)
                self.tk_img = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(240, 180, image=self.tk_img)
                
            self.akuisisi_window.after(30, self.update_camera_loop)

    def scan_object_color(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2
                roi = frame[cy-50:cy+50, cx-50:cx+50]
                avg_color = np.average(np.average(roi, axis=0), axis=0)
                b, g, r = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
                color_name, hex_color = get_color_name(r, g, b)
                
                self.color_preview.config(bg=hex_color)
                self.result_label.config(text=color_name, fg="white")
                self.rgb_label.config(text=f"R:{r} G:{g} B:{b}")
                self.app.update_status(f"Deteksi: {color_name}")

    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.akuisisi_window.destroy()
        self.app.show_gallery_page()
