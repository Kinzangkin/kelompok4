import tkinter as tk
from tkinter import messagebox

class CameraSelector:
    def __init__(self, parent_root, title, on_selected):
        self.root = parent_root
        self.title = title
        self.on_selected = on_selected
        self.camera_source = None
        self.camera_source_url = None

    def show(self):
        """Show camera source selection dialog"""
        # Create selection dialog
        self.source_dialog = tk.Toplevel(self.root)
        self.source_dialog.title(self.title)
        self.source_dialog.geometry("520x580")
        self.source_dialog.configure(bg="#2c3e50")
        self.source_dialog.resizable(False, False)
        self.source_dialog.transient(self.root)
        self.source_dialog.grab_set()
        
        # Center dialog
        self.source_dialog.update_idletasks()
        x = (self.source_dialog.winfo_screenwidth() // 2) - 260
        y = (self.source_dialog.winfo_screenheight() // 2) - 290
        self.source_dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(
            self.source_dialog,
            text=f"📷 {self.title}",
            font=("Helvetica", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)
        
        # Option frame
        option_frame = tk.Frame(self.source_dialog, bg="#2c3e50")
        option_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Radio variable
        self.camera_choice = tk.StringVar(value="internal")
        
        # === INTERNAL CAMERA OPTION ===
        internal_frame = tk.Frame(option_frame, bg="#34495e", relief=tk.RAISED, bd=2)
        internal_frame.pack(fill=tk.X, pady=10)
        
        tk.Radiobutton(
            internal_frame,
            text="🖥️ Internal (Webcam / USB Debugging)",
            variable=self.camera_choice,
            value="internal",
            font=("Helvetica", 12, "bold"),
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            command=self.toggle_camera_options
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        self.internal_options_frame = tk.Frame(internal_frame, bg="#34495e")
        self.internal_options_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        tk.Label(self.internal_options_frame, text="Pilih Camera Index:", font=("Helvetica", 10), bg="#34495e", fg="#bdc3c7").pack(anchor=tk.W)
        
        self.camera_index_var = tk.StringVar(value="0")
        index_frame = tk.Frame(self.internal_options_frame, bg="#34495e")
        index_frame.pack(anchor=tk.W, pady=5)
        
        for i, label in enumerate(["0 (Default)", "1 (Webcam 2)", "2 (USB Camera)"]):
            tk.Radiobutton(index_frame, text=label, variable=self.camera_index_var, value=str(i), font=("Helvetica", 10), bg="#34495e", fg="white", selectcolor="#2c3e50").pack(anchor=tk.W)
        
        # === EXTERNAL CAMERA OPTION ===
        external_frame = tk.Frame(option_frame, bg="#34495e", relief=tk.RAISED, bd=2)
        external_frame.pack(fill=tk.X, pady=10)
        
        tk.Radiobutton(
            external_frame,
            text="📱 External (IP Camera dari HP)",
            variable=self.camera_choice,
            value="external",
            font=("Helvetica", 12, "bold"),
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            command=self.toggle_camera_options
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        self.external_options_frame = tk.Frame(external_frame, bg="#34495e")
        self.external_options_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # IP Address input
        ip_row = tk.Frame(self.external_options_frame, bg="#34495e")
        ip_row.pack(fill=tk.X, pady=5)
        tk.Label(ip_row, text="IP Address:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="white", width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.ip_address_entry = tk.Entry(ip_row, font=("Helvetica", 12), width=18)
        self.ip_address_entry.pack(side=tk.LEFT, padx=5)
        self.ip_address_entry.insert(0, "192.168.1.100")
        self.ip_address_entry.config(state=tk.DISABLED)
        
        # Port input
        port_row = tk.Frame(self.external_options_frame, bg="#34495e")
        port_row.pack(fill=tk.X, pady=5)
        tk.Label(port_row, text="Port:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="white", width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.ip_port_entry = tk.Entry(port_row, font=("Helvetica", 12), width=8)
        self.ip_port_entry.pack(side=tk.LEFT, padx=5)
        self.ip_port_entry.insert(0, "8080")
        self.ip_port_entry.config(state=tk.DISABLED)
        
        # Buttons
        btn_frame = tk.Frame(self.source_dialog, bg="#2c3e50")
        btn_frame.pack(fill=tk.X, pady=20, padx=30)
        tk.Button(btn_frame, text="✅ Lanjutkan", command=self.proceed, font=("Helvetica", 12, "bold"), bg="#2ecc71", fg="white", width=15, height=2).pack(side=tk.LEFT, padx=10, expand=True)
        tk.Button(btn_frame, text="❌ Batal", command=self.source_dialog.destroy, font=("Helvetica", 12, "bold"), bg="#e74c3c", fg="white", width=15, height=2).pack(side=tk.RIGHT, padx=10, expand=True)

    def toggle_camera_options(self):
        state = tk.NORMAL if self.camera_choice.get() == "external" else tk.DISABLED
        self.ip_address_entry.config(state=state)
        self.ip_port_entry.config(state=state)

    def proceed(self):
        if self.camera_choice.get() == "internal":
            source = int(self.camera_index_var.get())
        else:
            ip = self.ip_address_entry.get().strip()
            port = self.ip_port_entry.get().strip()
            if not ip or ip == "192.168.1.100":
                messagebox.showwarning("Peringatan", "Cek IP Address Anda!")
                return
            source = f"http://{ip}:{port}/video"
        
        self.source_dialog.destroy()
        self.on_selected(source)
