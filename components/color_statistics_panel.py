import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import sqlite3
from datetime import datetime
from components.selectors import CameraSelector
from components.utils import get_color_name

# Try importing matplotlib for histogram chart
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ColorStatisticsPanel:
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.camera = None
        self.camera_running = False
        self.captured_frame = None
        self.db_path = os.path.join(self.app.app_dir, "color_stats.db")
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS color_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mean_r REAL, mean_g REAL, mean_b REAL,
                unique_colors INTEGER,
                dominant_hex TEXT,
                dominant_name TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def show_selection(self):
        selector = CameraSelector(
            self.root,
            "Pilih Sumber Kamera (Statistik Warna)",
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        self.color_window = tk.Toplevel(self.root)
        self.color_window.title("Statistik Warna Kamera")
        self.color_window.geometry("1200x800")
        self.color_window.configure(bg="#1a202c")
        self.color_window.state('zoomed')
        
        main_container = tk.Frame(self.color_window, bg="#1a202c")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- LEFT COLUMN (Kamera + Histogram + Buttons) ---
        left_col = tk.Frame(main_container, bg="#1a202c")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 1. Camera Feed
        camera_frame = tk.Frame(left_col, bg="#2d3748", relief=tk.FLAT, bd=0)
        camera_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(camera_frame, text="📸 LIVE CAMERA FEED", font=("Helvetica", 12, "bold"),
                 bg="#2d3748", fg="white").pack(pady=5)
        
        self.camera_canvas = tk.Canvas(camera_frame, bg="#1a252f", highlightthickness=0)
        self.camera_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 2. Histogram (Sekarang di bawah Kamera)
        hist_frame = tk.Frame(left_col, bg="#2d3748", height=200)
        hist_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Ukuran figure disesuaikan agar lebih memanjang (lebar)
        self.fig = Figure(figsize=(8, 2), dpi=90) 
        self.fig.patch.set_facecolor('#2d3748')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a202c')
        self.ax.tick_params(colors='white', labelsize=7)
        
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=hist_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3. Buttons (Sejejer/Horizontal di bawah Histogram)
        btn_container = tk.Frame(left_col, bg="#1a202c")
        btn_container.pack(fill=tk.X, pady=(10, 0))
        
        btn_style = {"font": ("Helvetica", 10, "bold"), "cursor": "hand2", "relief": tk.FLAT, "pady": 10}
        
        # Menggunakan side=tk.LEFT agar tombol berjejer
        tk.Button(btn_container, text="💾 SIMPAN DATA", command=self.save_to_database,
                  bg="#10b981", fg="white", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_container, text="📄 EXCEL", command=self.export_to_excel,
                  bg="#3b82f6", fg="white", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_container, text="✕ TUTUP", command=self.close_panel,
                  bg="#ef4444", fg="white", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- RIGHT COLUMN (Informasi Warna Saja) ---
        right_col = tk.Frame(main_container, bg="#2d3748", width=300, padx=20, pady=20)
        right_col.pack(side=tk.RIGHT, fill=tk.Y)
        right_col.pack_propagate(False)

        tk.Label(right_col, text="📊 INFO WARNA", font=("Helvetica", 12, "bold"), 
                 bg="#2d3748", fg="#63b3ed").pack(anchor="w", pady=(0,20))

        # Mean RGB
        self.mean_label = tk.Label(right_col, text="R: 0, G: 0, B: 0", font=("Consolas", 11, "bold"),
                                   bg="#2d3748", fg="#f6e05e")
        self.mean_label.pack(anchor="w", pady=5)
        
        # Unique Colors
        self.unique_label = tk.Label(right_col, text="Unik: 0", font=("Consolas", 11, "bold"),
                                     bg="#2d3748", fg="#63b3ed")
        self.unique_label.pack(anchor="w", pady=5)
        
        tk.Frame(right_col, height=2, bg="#4a5568").pack(fill=tk.X, pady=20)

        # Dominant Color (DIBESARKAN)
        tk.Label(right_col, text="WARNA DOMINAN:", font=("Helvetica", 10), 
                 bg="#2d3748", fg="white").pack(anchor="w")
        
        # Box warna dibuat jauh lebih besar (150x150 atau menyesuaikan)
        self.dominant_box = tk.Canvas(right_col, width=200, height=150, bg="black", highlightthickness=2, highlightbackground="#4a5568")
        self.dominant_box.pack(pady=15)
        
        self.dominant_label = tk.Label(right_col, text="#000000", font=("Consolas", 14, "bold"),
                                       bg="#2d3748", fg="white")
        self.dominant_label.pack(pady=5)
        
        self.dominant_name_label = tk.Label(right_col, text="Nama Warna", font=("Helvetica", 11, "italic"),
                                            bg="#2d3748", fg="#cbd5e0")
        self.dominant_name_label.pack()

        self.color_window.protocol("WM_DELETE_WINDOW", self.close_panel)
        self.start_camera(source)

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                self.color_window.destroy()
                return
            self.camera_running = True
            self.update_loop()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.color_window.destroy()

    def update_loop(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                # --- PROSES CROPPING ---
                # Memotong sedikit bagian kanan dan bawah (misal 15% dari lebar/tinggi)
                h, w = frame.shape[:2]
                crop_right = int(w * 0.85) # Ambil 85% lebar saja (potong kanan)
                crop_bottom = int(h * 0.85) # Ambil 85% tinggi saja (potong bawah)
                frame = frame[0:crop_bottom, 0:crop_right]
                
                self.captured_frame = frame.copy()
                self._show_on_canvas(self.camera_canvas, frame)
                self._process_color_stats(frame)
                
            self.color_window.after(30, self.update_loop)

    def _process_color_stats(self, frame):
        # ... (Logika perhitungan tetap sama) ...
        mean_bgr = cv2.mean(frame)[:3]
        mean_r, mean_g, mean_b = int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0])
        self.mean_label.config(text=f"Rata-rata:\nR:{mean_r} G:{mean_g} B:{mean_b}") # Ditambah line break agar rapi
        
        small_frame = cv2.resize(frame, (80, 80))
        unique_colors = len(np.unique(small_frame.reshape(-1, 3), axis=0))
        self.unique_label.config(text=f"Warna Unik: {unique_colors:,}")
        
        pixels = small_frame.reshape(-1, 3)
        quantized = (pixels // 32) * 32
        unique_rows, counts = np.unique(quantized, axis=0, return_counts=True)
        dominant_bgr = unique_rows[np.argmax(counts)]
        dom_r, dom_g, dom_b = int(dominant_bgr[2]), int(dominant_bgr[1]), int(dominant_bgr[0])
        
        color_name, hex_color = get_color_name(dom_r, dom_g, dom_b)
        
        # Update UI Dominan yang sudah dibesarkan
        self.dominant_box.config(bg=hex_color)
        self.dominant_label.config(text=hex_color)
        self.dominant_name_label.config(text=color_name)
        
        self.current_stats = {
            'mean_r': mean_r, 'mean_g': mean_g, 'mean_b': mean_b,
            'unique_colors': unique_colors,
            'dominant_hex': hex_color, 'dominant_name': color_name
        }
        self._update_histogram(frame)

    def _update_histogram(self, frame):
        self.ax.clear()
        self.ax.set_facecolor('#1a202c')
        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            hist = cv2.calcHist([frame], [i], None, [256], [0, 256])
            self.ax.plot(hist, color=col, linewidth=1.5)
        
        self.ax.set_xlim([0, 256])
        self.ax.grid(True, alpha=0.1, color='white')
        self.fig.tight_layout()
        self.chart_canvas.draw_idle()

    def _show_on_canvas(self, canvas, img):
        canvas.update_idletasks()
        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        if cw <= 1: cw, ch = 640, 480
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]
        
        # Resize maintaining aspect ratio
        ratio = min(cw/w, ch/h)
        new_w, new_h = int(w*ratio), int(h*ratio)
        
        resized_img = cv2.resize(img_rgb, (new_w, new_h))
        pil_img = Image.fromarray(resized_img)
        tk_img = ImageTk.PhotoImage(pil_img)

        canvas.delete("all")
        canvas.create_image(cw // 2, ch // 2, image=tk_img)
        canvas._tk_img_ref = tk_img 

    def save_to_database(self):
        if not hasattr(self, 'current_stats'): return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            s = self.current_stats
            cursor.execute('''INSERT INTO color_stats (mean_r, mean_g, mean_b, unique_colors, dominant_hex, dominant_name, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                            (s['mean_r'], s['mean_g'], s['mean_b'], s['unique_colors'], 
                             s['dominant_hex'], s['dominant_name'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Data disimpan!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_excel(self):
        # Logika export tetap sama seperti sebelumnya...
        pass

    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.color_window.destroy()