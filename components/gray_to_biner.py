import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
from datetime import datetime
from components.selectors import CameraSelector

class GrayToBinerPanel:
    def __init__(self, main_app):
        self.main_app = main_app
        self.root = main_app.root
        self.camera = None
        self.camera_running = False
        self.captured_frame = None # This will be grayscale
        self.biner_frame = None
        self.threshold_val = 127
        self.is_inverted = False
        self.filter_largest = False

    def show_selection(self):
        """Show camera selection for Gray to Biner"""
        selector = CameraSelector(
            self.root, 
            "Pilih Sumber Kamera (Gray to Biner)", 
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
            text="🔳 Gray to Biner (Hitam/Putih)", 
            font=("Helvetica", 24, "bold"), 
            bg="#2c3e50", fg="white"
        ).pack(side=tk.LEFT)
        
        # Main content area
        content_frame = tk.Frame(self.panel_container, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- LEFT: CAMERA VIEW (Always Grayscale) ---
        left_frame = tk.Frame(content_frame, bg="#34495e", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Live Camera (Grayscale Auto)", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=5)
        
        self.camera_canvas = tk.Canvas(left_frame, width=480, height=360, bg="black", highlightthickness=2, highlightbackground="#9b59b6")
        self.camera_canvas.pack(pady=5)
        
        # Buttons under camera
        btn_camera_frame = tk.Frame(left_frame, bg="#34495e")
        btn_camera_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_camera_frame, text="📸 Capture Gray", command=self.capture_frame,
            font=("Helvetica", 10, "bold"), bg="#2ecc71", fg="white", height=2
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        tk.Button(
            btn_camera_frame, text="📂 Gallery", command=self.load_from_gallery,
            font=("Helvetica", 10, "bold"), bg="#3498db", fg="white", height=2
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # --- RIGHT: INFO & SLIDER & RESULT ---
        right_frame = tk.Frame(content_frame, bg="#34495e", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Threshold Slider Area
        slider_frame = tk.Frame(right_frame, bg="#34495e")
        slider_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(slider_frame, text="Threshold Intensity (0 - 255):", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#f1c40f").pack(side=tk.LEFT)
        self.threshold_label = tk.Label(slider_frame, text="127", font=("Helvetica", 10, "bold"), bg="#34495e", fg="white", width=5)
        self.threshold_label.pack(side=tk.RIGHT)
        
        self.threshold_slider = ttk.Scale(
            right_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
            command=self.update_threshold
        )
        self.threshold_slider.set(127)
        self.threshold_slider.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(right_frame, text="Binary Preview", font=("Helvetica", 12, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=5)
        
        self.preview_canvas = tk.Canvas(right_frame, width=480, height=360, bg="black", highlightthickness=2, highlightbackground="#f1c40f")
        self.preview_canvas.pack(pady=5)
        
        # Info Panel
        self.info_frame = tk.Frame(right_frame, bg="#2c3e50", padx=15, pady=10)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.info_labels = {}
        for i, (key, label) in enumerate([("name", "Filename: -"), ("size", "Res: -"), ("type", "Mode: Binary"), ("area", "Area: -")]):
            lbl = tk.Label(self.info_frame, text=label, font=("Helvetica", 10), bg="#2c3e50", fg="#bdc3c7", anchor=tk.W)
            lbl.pack(fill=tk.X)
            self.info_labels[key] = lbl
            
        # Action Buttons
        btn_action_frame = tk.Frame(right_frame, bg="#34495e")
        btn_action_frame.pack(fill=tk.X, pady=10)
        
        self.invert_btn = tk.Button(
            btn_action_frame, text="🔄 Invert: OFF", command=self.toggle_invert,
            font=("Helvetica", 9, "bold"), bg="#9b59b6", fg="white", state=tk.DISABLED
        )
        self.invert_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.filter_btn = tk.Button(
            btn_action_frame, text="🔝 Filter: OFF", command=self.toggle_filter_largest,
            font=("Helvetica", 9, "bold"), bg="#1abc9c", fg="white", state=tk.DISABLED
        )
        self.filter_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.save_btn = tk.Button(
            btn_action_frame, text="💾 Simpan Hasil", command=self.save_image,
            font=("Helvetica", 9, "bold"), bg="#f1c40f", fg="#2c3e50", state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        tk.Button(
            btn_action_frame, text="↩️ Kembali", command=self.close_panel,
            font=("Helvetica", 9, "bold"), bg="#e74c3c", fg="white"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Start Camera
        self.start_camera(source)

    def update_threshold(self, val):
        self.threshold_val = int(float(val))
        self.threshold_label.config(text=str(self.threshold_val))
        if self.captured_frame is not None:
            self.apply_threshold()

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                self.close_panel()
                return
                
            self.camera_running = True
            self.main_app.update_status("Kamera aktif (Grayscale Mode)")
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
                # Convert to gray for display
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img = Image.fromarray(cv2.resize(frame_gray, (480, 360)))
                self.tk_camera = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(240, 180, image=self.tk_camera)
            self.root.after(30, self.update_camera_loop)

    def load_from_gallery(self):
        """Open image from gallery folder and stop camera"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            initialdir=self.main_app.gallery_folder,
            title="Pilih Gambar untuk Biner",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.bmp"), ("all files", "*.*"))
        )
        
        if file_path:
            # Stop camera
            self.camera_running = False
            if self.camera:
                self.camera.release()
                self.camera = None
            
            img_bgr = cv2.imread(file_path)
            if img_bgr is not None:
                # Convert to gray immediately as this is primary state for biner tool
                self.captured_frame = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                
                # Show in PRIMARY (left) canvas
                img_resized = cv2.resize(self.captured_frame, (480, 360))
                self.tk_camera = ImageTk.PhotoImage(Image.fromarray(img_resized))
                self.camera_canvas.delete("all")
                self.camera_canvas.create_image(240, 180, image=self.tk_camera)
                
                # Apply current threshold to show in preview
                self.apply_threshold()
                
                # Update Info
                h, w = self.captured_frame.shape
                self.info_labels["name"].config(text=f"Filename: {os.path.basename(file_path)}")
                self.info_labels["size"].config(text=f"Res: {w}x{h}")
                self.info_labels["type"].config(text="Mode: Binary (Imported)")
                
                # Enable buttons
                self.save_btn.config(state=tk.NORMAL)
                self.invert_btn.config(state=tk.NORMAL)
                self.filter_btn.config(state=tk.NORMAL)
                self.main_app.update_status(f"Berhasil memuat: {os.path.basename(file_path)}")

    def capture_frame(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                # Capture as grayscale
                self.captured_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold immediately
                self.apply_threshold()
                
                # Update Info
                h, w = self.captured_frame.shape
                self.info_labels["name"].config(text=f"Filename: binary_{datetime.now().strftime('%H%M%S')}.png")
                self.info_labels["size"].config(text=f"Res: {w}x{h}")
                
                # Enable buttons
                self.save_btn.config(state=tk.NORMAL)
                self.invert_btn.config(state=tk.NORMAL)
                self.filter_btn.config(state=tk.NORMAL)
                self.main_app.update_status("Gambar tercapture. Geser slider untuk mengatur intensitas.")

    def toggle_invert(self):
        self.is_inverted = not self.is_inverted
        status = "ON" if self.is_inverted else "OFF"
        self.invert_btn.config(text=f"🔄 Invert: {status}")
        self.apply_threshold()

    def toggle_filter_largest(self):
        self.filter_largest = not self.filter_largest
        status = "ON" if self.filter_largest else "OFF"
        self.filter_btn.config(text=f"🔝 Filter: {status}")
        self.apply_threshold()

    def apply_threshold(self):
        if self.captured_frame is not None:
            mode = cv2.THRESH_BINARY_INV if self.is_inverted else cv2.THRESH_BINARY
            _, biner = cv2.threshold(
                self.captured_frame, self.threshold_val, 255, mode
            )

            # --- FILTER LARGEST OBJECT LOGIC ---
            if self.filter_largest:
                # Find all contours
                contours, _ = cv2.findContours(biner, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # Find the contour with the largest area
                    largest_contour = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(largest_contour)
                    
                    # Create a black mask of the same size
                    mask = np.zeros_like(biner)
                    
                    # Draw only the largest contour on the mask with white color
                    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
                    
                    self.biner_frame = mask
                    self.info_labels["area"].config(text=f"Area: {int(area)} px")
                else:
                    self.biner_frame = biner # Fallback if no contours found
                    self.info_labels["area"].config(text="Area: 0 px")
            else:
                self.biner_frame = biner
                self.info_labels["area"].config(text="Area: (Filter Off)")
            
            # Show in preview
            img_bin = Image.fromarray(cv2.resize(self.biner_frame, (480, 360)))
            self.tk_preview = ImageTk.PhotoImage(img_bin)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(240, 180, image=self.tk_preview)

    def save_image(self):
        if self.biner_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"binary_th{self.threshold_val}_{timestamp}.png"
            filepath = os.path.join(self.main_app.gallery_folder, filename)
            
            # Save the binary result
            cv2.imwrite(filepath, self.biner_frame)
            messagebox.showinfo("Sukses", f"Gambar biner disimpan ke gallery!\n{filename}")
            self.main_app.update_status(f"Tersimpan: {filename}")

    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.main_app.show_gallery_page()
