import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from components.utils import get_color_name
from components.selectors import CameraSelector
import serial
import time

class ScanPanel:
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.camera = None
        self.camera_running = False
        self.current_rgb = (0, 0, 0)

        # 🔥 untuk anti spam kirim data
        self.last_sent_color = None

        
        # 🔌 KONEKSI ESP32

        # ✅ SOLUSI 5: hindari double connect
        if hasattr(self, 'ser') and self.ser and self.ser.is_open:
            self.ser.close()

        try:
            self.ser = serial.Serial('COM3', 115200)  # ganti COM
            time.sleep(2)
            print("ESP32 Terhubung")

        # ✅ SOLUSI 4: tampilkan error detail
        except Exception as e:
            self.ser = None
            print("ESP32 Tidak Terhubung:", e)

    def show_selection(self):
        selector = CameraSelector(
            self.root, 
            "Pilih Sumber Kamera (Scan Object)", 
            self.open_panel
        )
        selector.show()

    def open_panel(self, source):
        self.akuisisi_window = tk.Toplevel(self.root)
        self.akuisisi_window.title("Scan Object (Warna)")
        self.akuisisi_window.geometry("1100x650")
        self.akuisisi_window.configure(bg="#2c3e50")
        self.akuisisi_window.resizable(False, False)

        tk.Label(self.akuisisi_window, text="🔍 Scan Deteksi Warna",
                 font=("Helvetica", 20, "bold"),
                 bg="#2c3e50", fg="white").pack(pady=10)

        content_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Camera view
        left_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_frame, text="Area Scan (Kotak Tengah)",
                 font=("Helvetica", 12, "bold"),
                 bg="#34495e", fg="white").pack(pady=5)

        self.camera_canvas = tk.Canvas(left_frame, bg="#1a252f", width=480, height=360)
        self.camera_canvas.pack(padx=10, pady=10)

        # Result view
        right_frame = tk.Frame(content_frame, bg="#34495e", relief=tk.SUNKEN, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(right_frame, text="Hasil Deteksi",
                 font=("Helvetica", 14, "bold"),
                 bg="#34495e", fg="white").pack(pady=10)

        self.color_preview = tk.Label(right_frame, bg="#1a252f", width=30, height=8)
        self.color_preview.pack(pady=20)

        self.result_label = tk.Label(right_frame, text="Siap Scan...",
                                     font=("Helvetica", 18, "bold"),
                                     bg="#34495e", fg="#bdc3c7")
        self.result_label.pack(pady=10)

        self.rgb_label = tk.Label(right_frame, text="",
                                  font=("Helvetica", 10),
                                  bg="#34495e", fg="white")
        self.rgb_label.pack()

        # Buttons
        btn_frame = tk.Frame(self.akuisisi_window, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, pady=15)

        tk.Button(btn_frame, text="🔍 Scan Warna",
                  command=self.scan_object_color,
                  bg="#f1c40f").pack(side=tk.LEFT, padx=20, expand=True)

        tk.Button(btn_frame, text="↩️ Kembali",
                  command=self.close_panel,
                  bg="#95a5a6").pack(side=tk.LEFT, padx=20, expand=True)

        self.start_camera(source)
        self.akuisisi_window.protocol("WM_DELETE_WINDOW", self.close_panel)

    def start_camera(self, source):
        try:
            self.camera = cv2.VideoCapture(source)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Gagal membuka kamera!")
                return
            self.camera_running = True
            self.update_camera_loop()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_camera_loop(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_disp = cv2.resize(frame_rgb, (480, 360))

                cx, cy = 240, 180
                size = 50
                cv2.rectangle(frame_disp,
                              (cx-size, cy-size),
                              (cx+size, cy+size),
                              (241, 196, 15), 2)

                # 🔥 DETEKSI WARNA OTOMATIS
                h, w, _ = frame.shape
                cx2, cy2 = w // 2, h // 2
                roi = frame[cy2-50:cy2+50, cx2-50:cx2+50]

                avg_color = np.average(np.average(roi, axis=0), axis=0)
                b, g, r = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])

                color_name, hex_color = get_color_name(r, g, b)

                # update UI
                self.color_preview.config(bg=hex_color)
                self.result_label.config(text=color_name, fg="white")
                self.rgb_label.config(text=f"R:{r} G:{g} B:{b}")
                self.current_rgb = (r, g, b)

                # 🔥 kirim ke ESP32
                self.detect_color_and_send(r, g, b)

                # tampilkan kamera
                img = Image.fromarray(frame_disp)
                self.tk_img = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(240, 180, image=self.tk_img)

            self.akuisisi_window.after(30, self.update_camera_loop)

    def scan_object_color(self):
        r, g, b = self.current_rgb

        print("Scan klik:", r, g, b)

        # kirim ke ESP32
        self.detect_color_and_send(r, g, b)

    def detect_color_and_send(self, r, g, b):
    # 1. Konversi RGB ke format yang dipahami OpenCV (BGR) lalu ke HSV
        pixel = np.uint8([[[b, g, r]]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    
        h, s, v = hsv[0], hsv[1], hsv[2]
        detected_color = "NONE"

        # 2. Logika Deteksi berdasarkan Hue (Warna) dan Saturation (Kepekatan)
        # Saturation < 50 biasanya berarti warna terlalu abu-abu/putih/hitam
        if s > 50 and v > 50:
            if (h >= 0 and h <= 10) or (h >= 160 and h <= 180):
                detected_color = "RED"
            elif h >= 35 and h <= 85:
                detected_color = "GREEN"
            elif h >= 100 and h <= 130:
                detected_color = "BLUE"
            elif h >= 20 and h <= 34:
                detected_color = "YELLOW"

        # 3. Filter Anti-Spam & Pengiriman Serial
        if detected_color != "NONE" and detected_color != self.last_sent_color:
            if self.ser and self.ser.is_open:
                try:
                    # Tambahkan terminator yang jelas seperti '#' atau '\n'
                    data_to_send = f"{detected_color}\n"
                    self.ser.write(data_to_send.encode())
                    self.ser.flush() # Pastikan data terkirim dari buffer
                    print(f"Berhasil Terkirim: {detected_color}")
                    self.last_sent_color = detected_color
                except Exception as e:
                    print(f"Gagal kirim: {e}")
                    
    def close_panel(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.akuisisi_window.destroy()