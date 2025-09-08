import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from config_manager import save_config_ui, load_config_ui

BRANDS = ["Zeiss", "Mitutoyo", "Mahr"]

class ConvertJob:
    def __init__(self, brand, root_data, afp_to_dl, log_dir):
        self.brand = brand
        self.root_data = root_data
        self.afp_to_dl = afp_to_dl
        self.log_dir = log_dir
        self.status = "Stopped"
        self.progress = 0
        self.log = ""
        self._thread = None
        self._running = False
        self._paused = False

    def start(self, update_ui_callback):
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._run, args=(update_ui_callback,), daemon=True)
        self._thread.start()

    def _run(self, update_ui_callback):
        self.status = "Running"
        self.progress = 0
        self.log += f"{self.brand} conversion started.\n"
        update_ui_callback(self)
        while self.progress < 100 and self._running:
            if self._paused:
                time.sleep(0.5)
                continue
            time.sleep(0.2)
            self.progress += 5
            self.log += f"{self.brand} progress: {self.progress}%\n"
            update_ui_callback(self)
        if self.progress >= 100:
            self.status = "Completed"
            self.log += f"{self.brand} conversion completed.\n"
        elif not self._running:
            self.status = "Stopped"
            self.log += f"{self.brand} conversion stopped.\n"
        update_ui_callback(self)

    def pause(self):
        if self.status == "Running":
            self._paused = True
            self.status = "Paused"
            self.log += f"{self.brand} conversion paused.\n"

    def resume(self):
        if self.status == "Paused":
            self._paused = False
            self.status = "Running"
            self.log += f"{self.brand} conversion resumed.\n"

    def stop(self):
        if self._running:
            self._running = False
            self.status = "Stopped"
            self.log += f"{self.brand} conversion stopped by user.\n"

class Convert_AFP:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.jobs = {}
        self.selected_brand = None

        # Config folder entries
        config_frame = ttk.Labelframe(self.frame, text="Cấu hình thư mục")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        labels = ["Root data", "AFP to DL", "Log"]
        self.entries = []

        for i, label_text in enumerate(labels):
            ttk.Label(config_frame, text=label_text+":").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(config_frame, width=50)
            entry.grid(row=i, column=1, padx=5)
            ttk.Button(config_frame, text="...", command=lambda e=entry: self.browse_folder(e)).grid(row=i, column=2)
            self.entries.append(entry)

        # Brand selector
        brand_frame = ttk.Labelframe(self.frame, text="Chọn chức năng chuyển đổi")
        brand_frame.pack(fill=tk.X, padx=10, pady=5)

        self.brand_vars = {}
        for brand in BRANDS:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(brand_frame, text=brand+" function", variable=var)
            cb.pack(side=tk.LEFT, padx=10)
            self.brand_vars[brand] = var

        # Treeview jobs status
        columns = ("status", "progress")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=8)
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("progress", text="Tiến trình")
        self.tree.column("status", width=150)
        self.tree.column("progress", width=150)
        self.tree.pack(fill=tk.X, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_job_selected)

        # Log panel
        ttk.Label(self.frame, text="Log chuyển đổi:").pack(anchor=tk.W, padx=10)
        self.log_text = tk.Text(self.frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Control buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=5)

    def browse_folder(self, entry):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def on_job_selected(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_brand = selected
