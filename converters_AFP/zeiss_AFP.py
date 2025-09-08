import os
import threading
import time
import shutil
import pandas as pd

class ZeissTxtToCsvConverter:
    """
    Chuyển đổi TXT -> CSV cho thư mục Zeiss.
    Duyệt trong từng subfolder Zeiss (tên chính xác).
    Hỗ trợ start, pause, resume, stop bằng threading.
    """
    def __init__(self, root_dir, dest_dir, log_dir, log_function):
        self.root_dir = os.path.join(root_dir, "Zeiss")
        self.dest_dir = os.path.join(dest_dir, "Zeiss")
        self.log_dir  = os.path.join(log_dir,  "Zeiss")
        self.log = log_function
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self.thread = None

        # Đảm bảo các thư mục tồn tại
        for folder in [self.root_dir, self.dest_dir, self.log_dir]:
            os.makedirs(folder, exist_ok=True)

    def convert_file(self, txt_path):
        csv_path = os.path.join(self.dest_dir, os.path.basename(txt_path).rsplit('.', 1)[0] + '.csv')
        backup_path = os.path.join(self.log_dir, os.path.basename(txt_path))
        try:
            try:
                df = pd.read_csv(txt_path, sep='\t', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(txt_path, sep='\t', encoding='latin1')
            df.to_csv(csv_path, index=False)
            self.log(f"Converted: {txt_path} -> {csv_path}")
            shutil.move(txt_path, backup_path)
            self.log(f"Moved original to log folder: {backup_path}")
        except Exception as e:
            self.log(f"Failed to convert {txt_path}: {str(e)}")

    def run(self):
        self._stop_event.clear()
        self._pause_event.set()
        self.log("Zeiss/AFP Conversion started.")
        while not self._stop_event.is_set():
            self._pause_event.wait()
            txt_files = [f for f in os.listdir(self.root_dir) if f.endswith('.txt')]
            if not txt_files:
                time.sleep(1)
                continue
            for filename in txt_files:
                if self._stop_event.is_set():
                    self.log("Stop event received. Breaking conversion loop.")
                    return
                full_path = os.path.join(self.root_dir, filename)
                self.convert_file(full_path)
            time.sleep(2)
        self.log("Zeiss/AFP Conversion thread exited.")

    def start(self):
        if self.thread and self.thread.is_alive():
            self.log("Already running.")
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.log("Thread started.")

    def pause(self):
        self._pause_event.clear()
        self.log("Conversion paused.")

    def resume(self):
        self._pause_event.set()
        self.log("Conversion resumed.")

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()
        if self.thread:
            self.thread.join(timeout=2)
        self.log("Conversion stopped.")
