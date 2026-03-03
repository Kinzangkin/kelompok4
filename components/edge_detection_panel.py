import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
from datetime import datetime
from components.selectors import CameraSelector

# Matplotlib for histogram
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class EdgeDetectionPanel:
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.camera = None
        self.camera_running = False
        self.captured_image = None
        self.current_frame = None
        self.result_image = None
        self.active_filter = None
        self.threshold_val = 127

    def show_selection(self):
        """Show camera source selection dialog"""
        selector = CameraSelector(
            self.root,
            "Pilih Sumber Kamera (Deteksi Tepi)",
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        """Open the edge detection panel"""
        self.edge_window = tk.Toplevel(self.root)
        self.edge_window.title("Deteksi Tepi - Analisis Citra")
        self.edge_window.geometry("1366x768")
        self.edge_window.configure(bg="#2c3e50")
        self.edge_window.state('zoomed')
        self.edge_window.resizable(True, True)

        # =============== MAIN HORIZONTAL LAYOUT ===============
        main_hbox = tk.Frame(self.edge_window, bg="#2c3e50")
        main_hbox.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # =============== SIDEBAR ===============
        self._build_sidebar(main_hbox)

        # =============== CONTENT AREA ===============
        content_area = tk.Frame(main_hbox, bg="#2c3e50")
        content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- TOP ROW: Camera | Result | Histogram ---
        top_frame = tk.Frame(content_area, bg="#2c3e50")
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # Camera panel
        camera_frame = tk.Frame(top_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(camera_frame, text="📷 Camera", font=("Helvetica", 12, "bold"),
                 bg="#34495e", fg="white").pack(pady=5)
        self.camera_canvas = tk.Canvas(camera_frame, bg="#1a252f", width=380, height=300)
        self.camera_canvas.pack(padx=8, pady=(0, 8), fill=tk.BOTH, expand=True)

        # Result panel
        result_frame = tk.Frame(top_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(result_frame, text="📋 Hasil", font=("Helvetica", 12, "bold"),
                 bg="#34495e", fg="white").pack(pady=5)
        self.result_canvas = tk.Canvas(result_frame, bg="#1a252f", width=380, height=300)
        self.result_canvas.pack(padx=8, pady=(0, 8), fill=tk.BOTH, expand=True)

        # Histogram panel
        hist_frame = tk.Frame(top_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        hist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(hist_frame, text="📊 Histogram", font=("Helvetica", 12, "bold"),
                 bg="#34495e", fg="white").pack(pady=5)

        self.fig = Figure(figsize=(4, 3), dpi=80)
        self.fig.patch.set_facecolor('#1a252f')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a252f')
        self.ax.tick_params(colors='white', labelsize=7)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.set_xlabel('Intensitas', color='white', fontsize=8)
        self.ax.set_ylabel('Frekuensi', color='white', fontsize=8)
        self.ax.text(0.5, 0.5, 'Histogram akan muncul\nsetelah filter diterapkan',
                     transform=self.ax.transAxes, ha='center', va='center',
                     color='gray', fontsize=9)

        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=hist_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(padx=8, pady=(0, 8), fill=tk.BOTH, expand=True)

        # --- THRESHOLD SLIDER ---
        slider_container = tk.Frame(content_area, bg="#34495e", relief=tk.SUNKEN, bd=2)
        slider_container.pack(fill=tk.X, padx=10, pady=5)

        slider_inner = tk.Frame(slider_container, bg="#34495e")
        slider_inner.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(slider_inner, text="Threshold:", font=("Helvetica", 11, "bold"),
                 bg="#34495e", fg="#f1c40f").pack(side=tk.LEFT)

        self.threshold_label = tk.Label(slider_inner, text="127", font=("Helvetica", 11, "bold"),
                                        bg="#34495e", fg="white", width=5)
        self.threshold_label.pack(side=tk.RIGHT)

        self.threshold_slider = ttk.Scale(
            slider_inner, from_=0, to=255, orient=tk.HORIZONTAL,
            command=self._on_threshold_change
        )
        self.threshold_slider.set(127)
        self.threshold_slider.pack(fill=tk.X, padx=(10, 10), expand=True)

        # --- BOTTOM BUTTONS ---
        btn_frame = tk.Frame(content_area, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 12))

        btn_style = {"font": ("Helvetica", 14, "bold"), "width": 14, "height": 2, "cursor": "hand2"}

        self.capture_btn = tk.Button(btn_frame, text="📷 Capture",
                                     command=self.capture_image,
                                     bg="#2ecc71", fg="white", **btn_style)
        self.capture_btn.pack(side=tk.LEFT, padx=10, expand=True)

        self.save_btn = tk.Button(btn_frame, text="💾 Simpan",
                                  command=self.save_result,
                                  bg="#3498db", fg="white",
                                  state=tk.DISABLED, **btn_style)
        self.save_btn.pack(side=tk.LEFT, padx=10, expand=True)

        self.clear_btn = tk.Button(btn_frame, text="🗑️ Hapus",
                                   command=self.clear_result,
                                   bg="#e74c3c", fg="white", **btn_style)
        self.clear_btn.pack(side=tk.LEFT, padx=10, expand=True)

        self.close_btn = tk.Button(btn_frame, text="❌ Tutup",
                                   command=self.close_panel,
                                   bg="#95a5a6", fg="white", **btn_style)
        self.close_btn.pack(side=tk.LEFT, padx=10, expand=True)

        # Start camera
        self.start_camera(source)
        self.edge_window.protocol("WM_DELETE_WINDOW", self.close_panel)

    # =============== SIDEBAR ===============

    def _build_sidebar(self, parent):
        """Build the sidebar with dashboard and filter buttons"""
        sidebar = tk.Frame(parent, bg="#1a252f", width=180, relief=tk.RAISED, bd=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Dashboard header
        header = tk.Frame(sidebar, bg="#0d1821", pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="📌 Dashboard", font=("Helvetica", 14, "bold"),
                 bg="#0d1821", fg="white").pack()

        # Separator
        tk.Frame(sidebar, bg="#34495e", height=2).pack(fill=tk.X, pady=5)

        # Sidebar button list
        sidebar_buttons = [
            ("📷 Camera",       "#2ecc71", self._sidebar_camera),
            ("📂 Open",         "#3498db", self._sidebar_open),
            ("🔲 Filter Robert",  "#9b59b6", lambda: self._apply_filter("robert")),
            ("🔲 Filter Prewitt", "#8e44ad", lambda: self._apply_filter("prewitt")),
            ("🔲 Filter Sobel",   "#2980b9", lambda: self._apply_filter("sobel")),
            ("🔲 Filter Canny",   "#16a085", lambda: self._apply_filter("canny")),
            ("🔲 Frei-Chen",      "#d35400", lambda: self._apply_filter("freichen")),
            ("🔲 Filter Otsu",    "#c0392b", lambda: self._apply_filter("otsu")),
            ("🔲 Filter Kirsch",  "#27ae60", lambda: self._apply_filter("kirsch")),
            ("🔲 Dua Aras",       "#f39c12", lambda: self._apply_filter("duaaras")),
        ]

        self.sidebar_btns = {}
        for text, color, cmd in sidebar_buttons:
            btn = tk.Button(sidebar, text=text, command=cmd,
                            font=("Helvetica", 10, "bold"),
                            bg=color, fg="white",
                            activebackground=color,
                            relief=tk.FLAT, cursor="hand2",
                            anchor=tk.W, padx=15, pady=8)
            btn.pack(fill=tk.X, padx=8, pady=3)
            self.sidebar_btns[text] = btn

    # =============== SIDEBAR ACTIONS ===============

    def _sidebar_camera(self):
        """Switch back to live camera view"""
        if not self.camera_running and self.camera:
            self.camera_running = True
            self.captured_image = None
            self.capture_btn.config(text="📷 Capture", bg="#2ecc71")
            self._update_camera_loop()
            self.app.update_status("Kamera live view - Deteksi Tepi")

    def _sidebar_open(self):
        """Open image from file"""
        filepath = filedialog.askopenfilename(
            initialdir=self.app.gallery_folder,
            title="Pilih Gambar",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filepath:
            # Stop camera
            self.camera_running = False
            img_bgr = cv2.imread(filepath)
            if img_bgr is not None:
                self.captured_image = img_bgr.copy()
                self._show_on_canvas(self.camera_canvas, self.captured_image)
                self.capture_btn.config(text="🔄 Ambil Ulang", bg="#f39c12")
                self.app.update_status(f"Gambar dimuat: {os.path.basename(filepath)}")

    # =============== CAMERA ===============

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                self.edge_window.destroy()
                return
            self.camera_running = True
            self.app.update_status("Kamera aktif - Mode Deteksi Tepi")
            self._update_camera_loop()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.edge_window.destroy()

    def _update_camera_loop(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()
                self._show_on_canvas(self.camera_canvas, frame)
            try:
                self.edge_window.after(30, self._update_camera_loop)
            except tk.TclError:
                pass

    # =============== CAPTURE ===============

    def capture_image(self):
        """Capture or retake"""
        if not self.camera_running:
            # RETAKE
            self.camera_running = True
            self.captured_image = None
            self.capture_btn.config(text="📷 Capture", bg="#2ecc71")
            self.save_btn.config(state=tk.DISABLED)
            self._update_camera_loop()
            self.app.update_status("Kamera live view")
        else:
            # CAPTURE
            if self.camera and self.current_frame is not None:
                self.captured_image = self.current_frame.copy()
                self.camera_running = False
                self._show_on_canvas(self.camera_canvas, self.captured_image)
                self.capture_btn.config(text="🔄 Ambil Ulang", bg="#f39c12")
                self.app.update_status("Gambar berhasil di-capture! Pilih filter di sidebar.")
            else:
                messagebox.showwarning("Peringatan", "Tidak ada frame kamera!")

    # =============== EDGE DETECTION FILTERS ===============

    def _apply_filter(self, filter_name):
        """Apply the selected edge detection filter"""
        if self.captured_image is None:
            messagebox.showwarning("Peringatan", "Capture gambar terlebih dahulu!")
            return

        self.active_filter = filter_name
        gray = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)
        threshold = self.threshold_val

        if filter_name == "robert":
            result = self._filter_robert(gray, threshold)
        elif filter_name == "prewitt":
            result = self._filter_prewitt(gray, threshold)
        elif filter_name == "sobel":
            result = self._filter_sobel(gray, threshold)
        elif filter_name == "canny":
            result = self._filter_canny(gray, threshold)
        elif filter_name == "freichen":
            result = self._filter_freichen(gray, threshold)
        elif filter_name == "otsu":
            result = self._filter_otsu(gray)
        elif filter_name == "kirsch":
            result = self._filter_kirsch(gray, threshold)
        elif filter_name == "duaaras":
            result = self._filter_dua_aras(gray, threshold)
        else:
            return

        self.result_image = result
        self._show_on_canvas(self.result_canvas, result, is_gray=True)
        self._update_histogram(result)
        self.save_btn.config(state=tk.NORMAL)
        self.app.update_status(f"Filter {filter_name.capitalize()} diterapkan (threshold={threshold})")

    def _filter_robert(self, gray, threshold):
        """Roberts Cross operator"""
        kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float64)
        kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float64)
        gx = cv2.filter2D(gray.astype(np.float64), -1, kernel_x)
        gy = cv2.filter2D(gray.astype(np.float64), -1, kernel_y)
        magnitude = np.sqrt(gx**2 + gy**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
        _, result = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)
        return result

    def _filter_prewitt(self, gray, threshold):
        """Prewitt operator"""
        kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
        kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)
        gx = cv2.filter2D(gray.astype(np.float64), -1, kernel_x)
        gy = cv2.filter2D(gray.astype(np.float64), -1, kernel_y)
        magnitude = np.sqrt(gx**2 + gy**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
        _, result = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)
        return result

    def _filter_sobel(self, gray, threshold):
        """Sobel operator"""
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(gx**2 + gy**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
        _, result = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)
        return result

    def _filter_canny(self, gray, threshold):
        """Canny edge detection"""
        low = max(threshold, 1)
        high = min(low * 2, 255)
        result = cv2.Canny(gray, low, high)
        return result

    def _filter_freichen(self, gray, threshold):
        """Frei-Chen operator"""
        sqrt2 = np.sqrt(2)
        k1 = np.array([[1, sqrt2, 1], [0, 0, 0], [-1, -sqrt2, -1]], dtype=np.float64) / (2 + sqrt2)
        k2 = np.array([[1, 0, -1], [sqrt2, 0, -sqrt2], [1, 0, -1]], dtype=np.float64) / (2 + sqrt2)
        g1 = cv2.filter2D(gray.astype(np.float64), -1, k1)
        g2 = cv2.filter2D(gray.astype(np.float64), -1, k2)
        magnitude = np.sqrt(g1**2 + g2**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
        _, result = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)
        return result

    def _filter_otsu(self, gray):
        """Otsu thresholding"""
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return result

    def _filter_kirsch(self, gray, threshold):
        """Kirsch compass masks (8 directions)"""
        kernels = [
            np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float64),
            np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float64),
            np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float64),
            np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float64),
            np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float64),
            np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float64),
            np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float64),
            np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float64),
        ]
        max_grad = np.zeros_like(gray, dtype=np.float64)
        for k in kernels:
            filtered = cv2.filter2D(gray.astype(np.float64), -1, k)
            max_grad = np.maximum(max_grad, np.abs(filtered))
        max_grad = np.clip(max_grad, 0, 255).astype(np.uint8)
        _, result = cv2.threshold(max_grad, threshold, 255, cv2.THRESH_BINARY)
        return result

    def _filter_dua_aras(self, gray, threshold):
        """Two-level (Dua Aras) thresholding"""
        low = max(threshold - 40, 0)
        high = min(threshold + 40, 255)
        result = np.zeros_like(gray)
        result[gray >= high] = 255
        result[(gray >= low) & (gray < high)] = 128
        return result

    # =============== THRESHOLD ===============

    def _on_threshold_change(self, val):
        self.threshold_val = int(float(val))
        self.threshold_label.config(text=str(self.threshold_val))
        # Re-apply active filter if exists
        if self.active_filter and self.captured_image is not None:
            self._apply_filter(self.active_filter)

    # =============== HISTOGRAM ===============

    def _update_histogram(self, gray_img):
        """Update histogram chart with result image"""
        self.ax.clear()
        self.ax.set_facecolor('#1a252f')
        self.ax.tick_params(colors='white', labelsize=7)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.set_xlabel('Intensitas', color='white', fontsize=8)
        self.ax.set_ylabel('Frekuensi', color='white', fontsize=8)

        self.ax.hist(gray_img.ravel(), bins=256, range=(0, 256),
                     color='#3498db', alpha=0.7, histtype='stepfilled')
        self.ax.legend(['Hasil'], loc='upper right', fontsize=7,
                       facecolor='#34495e', edgecolor='white', labelcolor='white')
        self.fig.tight_layout()
        self.chart_canvas.draw()

    # =============== UTILITY ===============

    def _show_on_canvas(self, canvas, img, is_gray=False):
        """Display an image on a tk.Canvas, fitting to canvas size"""
        try:
            canvas.update_idletasks()
            cw = canvas.winfo_width() or 380
            ch = canvas.winfo_height() or 300
        except tk.TclError:
            cw, ch = 380, 300

        if is_gray:
            img_rgb = img
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(cv2.resize(img_rgb, (cw, ch)))
        tk_img = ImageTk.PhotoImage(pil_img)

        canvas.delete("all")
        canvas.create_image(cw // 2, ch // 2, image=tk_img)
        canvas._tk_img_ref = tk_img  # prevent GC

    # =============== BOTTOM BUTTONS ===============

    def save_result(self):
        """Save result image to gallery"""
        if self.result_image is None:
            messagebox.showwarning("Peringatan", "Tidak ada hasil untuk disimpan!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_name = self.active_filter or "edge"
        filename = f"edge_{filter_name}_{timestamp}.png"
        filepath = os.path.join(self.app.gallery_folder, filename)
        cv2.imwrite(filepath, self.result_image)
        messagebox.showinfo("Sukses", f"Hasil disimpan ke gallery!\n{filename}")
        self.app.update_status(f"Tersimpan: {filename}")

    def clear_result(self):
        """Clear result canvas and histogram"""
        self.result_image = None
        self.active_filter = None
        self.result_canvas.delete("all")
        self.save_btn.config(state=tk.DISABLED)

        # Reset histogram
        self.ax.clear()
        self.ax.set_facecolor('#1a252f')
        self.ax.tick_params(colors='white', labelsize=7)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.text(0.5, 0.5, 'Histogram akan muncul\nsetelah filter diterapkan',
                     transform=self.ax.transAxes, ha='center', va='center',
                     color='gray', fontsize=9)
        self.chart_canvas.draw()
        self.app.update_status("Hasil dihapus")

    def close_panel(self):
        """Close the edge detection panel"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.edge_window.destroy()
        self.app.show_gallery_page()
