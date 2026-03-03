import os
import sys
import time
import subprocess
from threading import Timer

class AutoReloader:
    def __init__(self, target_script):
        self.target_script = target_script
        self.process = None
        self.last_mtime = {}
        self.files_to_watch = []
        self.scan_files()

    def scan_files(self):
        """Scan all .py files to monitor"""
        self.files_to_watch = []
        for root, dirs, files in os.walk("."):
            if "env" in root or "venv" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py") and file != os.path.basename(__file__):
                    path = os.path.join(root, file)
                    self.files_to_watch.append(path)
                    if path not in self.last_mtime:
                        self.last_mtime[path] = os.path.getmtime(path)

    def start_process(self):
        """Start the target script"""
        print(f"\n[Launcher] Memulai aplikasi: {self.target_script}...")
        if sys.platform == "win32":
            # Creationflags to allow clean killing of process tree if needed
            self.process = subprocess.Popen([sys.executable, self.target_script])
        else:
            self.process = subprocess.Popen([sys.executable, self.target_script])

    def stop_process(self):
        """Stop the current process"""
        if self.process:
            print("[Launcher] Mendeteksi dan menutup aplikasi lama...")
            self.process.kill()
            self.process.wait()
            self.process = None

    def check_changes(self):
        """Check if any file has changed"""
        changed = False
        # Re-scan for new files occasionally could be added here, 
        # but for now let's just check known files + simpler logic
        
        # Check existing monitored files
        for path in self.files_to_watch:
            try:
                mtime = os.path.getmtime(path)
                if mtime > self.last_mtime.get(path, 0):
                    self.last_mtime[path] = mtime
                    changed = True
            except OSError:
                pass # File might have been deleted

        return changed

    def run(self):
        self.start_process()
        try:
            while True:
                time.sleep(1)
                # Simple file scanner to detect new files too
                current_files = []
                for root, dirs, files in os.walk("."):
                    if "env" in root or "venv" in root or "__pycache__" in root:
                        continue
                    for file in files:
                        if file.endswith(".py") and file != os.path.basename(__file__):
                            current_files.append(os.path.join(root, file))
                
                # Check for changes
                restart = False
                for path in current_files:
                    try:
                        mtime = os.path.getmtime(path)
                        if path not in self.last_mtime:
                            self.last_mtime[path] = mtime
                            restart = True # New file found
                        elif mtime > self.last_mtime[path]:
                            self.last_mtime[path] = mtime
                            restart = True # Modified
                    except OSError:
                        pass
                
                self.files_to_watch = current_files

                if restart:
                    self.stop_process()
                    self.start_process()

        except KeyboardInterrupt:
            self.stop_process()
            print("\n[Launcher] Berhenti.")

if __name__ == "__main__":
    script = "main.py"
    if len(sys.argv) > 1:
        script = sys.argv[1]
    
    reloader = AutoReloader(script)
    reloader.run()
