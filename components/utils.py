import cv2
import numpy as np
import os
import subprocess
from tkinter import messagebox

def get_color_name(r, g, b):
    """Simple RGB to Color Name converter"""
    # Convert RGB to HSV for better detection
    hsv_layer = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)
    h, s, v = hsv_layer[0][0]
    
    # Format Hex untuk UI
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    
    # Logic Deteksi (H: 0-179, S: 0-255, V: 0-255)
    # Low saturation = Putih / Abu / Hitam
    if s < 30 and v > 200: return "Putih", hex_color
    if v < 40: return "Hitam", hex_color
    if s < 30: return "Abu-abu", hex_color
    
    # Hue based detection
    if h < 5 or h > 170: return "Merah", hex_color
    elif h < 22: return "Oranye", hex_color
    elif h < 35: return "Kuning", hex_color
    elif h < 85: return "Hijau", hex_color
    elif h < 130: return "Biru", hex_color
    elif h < 160: return "Ungu/Violet", hex_color
    elif h < 170: return "Pink", hex_color
    
    return "Tidak Teridentifikasi", hex_color

def format_file_size(file_size):
    """Format file size into human readable string"""
    if file_size < 1024:
        return f"{file_size} B"
    elif file_size < 1024 * 1024:
        return f"{file_size / 1024:.2f} KB"
    else:
        return f"{file_size / (1024 * 1024):.2f} MB"

def open_file_location(img_path):
    """Open file location in Windows Explorer"""
    try:
        # Use Windows explorer to select the file
        subprocess.run(['explorer', '/select,', img_path])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuka lokasi: {e}")
        return False
