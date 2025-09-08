#Handles conversion logic and threading.
import os
import threading
import time
import shutil
import pandas as pd

class TxtToCsvConverter:
    def __init__(self, source_dir, dest_dir, log_dir, log_function):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.log_dir = log_dir
        self.log = log_function
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self.thread = None

    def convert_file(self, txt_path):
        csv_path = os.path.join(self.dest_dir, os.path.basename(txt_path).rsplit('.', 1)[0] + '.csv')
        backup_path = os.path.join(self.log_dir, os.path.basename(txt_path))
        try:
            try:
                df = pd.read_csv(txt_path, sep='\t', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(txt_path, sep='\t', encoding='latin1')
            df.to_csv(csv_path, index=False)
            self.log(f"Converted: {txt_path} -> {csv_path}\n")
            shutil.move(txt_path, backup_path)
            self.log(f"Moved original to log folder: {backup_path}\n")
        except Exception as e:
            self.log(f"Failed to convert {txt_path}: {str(e)}\n")

    def run(self):
        self._stop_event.clear()
        self._pause_event.set()

        while not self._stop_event.is_set():
            self._pause_event.wait()

            txt_files = [f for f in os.listdir(self.source_dir) if f.endswith('.txt')]
            if not txt_files:
                time.sleep(1)
                continue
            for filename in txt_files:
                full_path = os.path.join(self.source_dir, filename)
                self.convert_file(full_path)
            time.sleep(2)

    def start(self):
        if self.thread and self.thread.is_alive():
            self.log("Already running\n")
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.log("Conversion started\n")

    def pause(self):
        self._pause_event.clear()
        self.log("Conversion paused\n")

    def resume(self):
        self._pause_event.set()
        self.log("Conversion resumed\n")

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()
        if self.thread:
            self.thread.join()
        self.log("Conversion stopped\n")
