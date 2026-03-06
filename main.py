import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import subprocess
from datetime import datetime

# Import components
from components.gallery_page import GalleryPage
from components.image_detail import ImageDetailPage
from components.camera_panel import CameraPanel
from components.scan_panel import ScanPanel
from components.rgb_to_gray import RGBToGrayPanel
from components.gray_to_biner import GrayToBinerPanel
from components.histogram_panel import HistogramPanel
from components.edge_detection_panel import EdgeDetectionPanel
from components.shape_analysis_panel import ShapeAnalysisPanel
from components.utils import get_color_name, format_file_size, open_file_location


class AplikasiPengolahanCitra:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengolahan Citra Digital")
        self.root.geometry("1100x750")
        self.root.configure(bg="#2c3e50")
        
        # Shared Variables required by some components or state tracking
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.gallery_folder = os.path.join(self.app_dir, "gallery")
        self.ensure_gallery_folder()
        
        # Initialize components
        self.gallery_component = GalleryPage(self)
        self.detail_component = ImageDetailPage(self)
        self.camera_component = CameraPanel(self)
        self.scan_component = ScanPanel(self)
        self.rgb_gray_component = RGBToGrayPanel(self)
        self.gray_biner_component = GrayToBinerPanel(self)
        self.histogram_component = HistogramPanel(self)
        self.edge_detection_component = EdgeDetectionPanel(self)
        self.shape_analysis_component = ShapeAnalysisPanel(self)
        
        # Setup UI
        self.setup_menu()
        self.setup_status_bar()
        self.show_gallery_page()
        
    def ensure_gallery_folder(self):
        """Create gallery folder if not exists"""
        if not os.path.exists(self.gallery_folder):
            os.makedirs(self.gallery_folder)
    
    def setup_menu(self):
        """Setup menu bar navigasi"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Menu File
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Gallery", command=self.show_gallery_page)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Menu Akuisisi Citra
        akuisisi_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Akuisisi Citra", menu=akuisisi_menu)
        akuisisi_menu.add_command(label="Ambil Foto", command=self.show_akuisisi_panel)
        akuisisi_menu.add_command(label="Scan Object (Warna)", command=self.show_scan_object_selection)
        
        # Menu Konversi Citra
        konversi_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Konversi Citra", menu=konversi_menu)
        konversi_menu.add_command(label="RGB to Gray", command=self.show_rgb_gray_selection)
        konversi_menu.add_command(label="Gray to Biner", command=self.show_gray_biner_selection)
        
        # Menu Analisis Citra
        analisis_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Analisis Citra", menu=analisis_menu)
        analisis_menu.add_command(label="Histogram", command=self.show_histogram_selection)
        analisis_menu.add_command(label="Deteksi Tepi", command=self.show_edge_detection_selection)
        analisis_menu.add_command(label="Analisis Bentuk", command=self.show_shape_analysis_selection)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = tk.Label(
            self.root,
            text="Siap",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#1a252f",
            fg="white",
            font=("Helvetica", 10)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.root.winfo_children():
            if widget != self.status_bar and not isinstance(widget, tk.Menu):
                widget.destroy()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # --- Navigation Helpers (Delegation to components) ---
    
    def show_gallery_page(self):
        self.gallery_component.show()
    
    def show_image_detail(self, img_path):
        self.detail_component.show(img_path)

    def show_akuisisi_panel(self):
        self.camera_component.show_selection()
    
    def show_scan_object_selection(self):
        self.scan_component.show_selection()

    def show_rgb_gray_selection(self):
        self.rgb_gray_component.show_selection()

    def show_gray_biner_selection(self):
        self.gray_biner_component.show_selection()

    def show_histogram_selection(self):
        self.histogram_component.show_selection()

    def show_edge_detection_selection(self):
        self.edge_detection_component.show_selection()

    def show_shape_analysis_selection(self):
        self.shape_analysis_component.show_selection()


def main():
    root = tk.Tk()
    app = AplikasiPengolahanCitra(root)
    root.mainloop()


if __name__ == "__main__":
    main()
