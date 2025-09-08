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

class ConvertText2CSVTab:
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
            self.selected_brand = selected[0]
            self.update_log()

    def update_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        if self.selected_brand and self.selected_brand in self.jobs:
            self.log_text.insert(tk.END, self.jobs[self.selected_brand].log)
        self.log_text.config(state=tk.DISABLED)

    def start(self):
        root_data = self.entries[0].get()
        afp_to_dl = self.entries[1].get()
        log_dir = self.entries[2].get()
        if not all([root_data, afp_to_dl, log_dir]):
            messagebox.showwarning("Thiếu dữ liệu", "Hãy điền đầy đủ các thư mục trước khi bắt đầu.")
            return
        selected_brands = [b for b, v in self.brand_vars.items() if v.get()]
        if not selected_brands:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn ít nhất một thương hiệu để chuyển đổi.")
            return
        for brand in selected_brands:
            if brand not in self.jobs or self.jobs[brand].status == "Stopped":
                job = ConvertJob(brand, root_data, afp_to_dl, log_dir)
                self.jobs[brand] = job
                self.tree.insert("", tk.END, iid=brand, values=(job.status, f"{job.progress}%"))
            self.jobs[brand].start(self.update_tree_ui)

    def pause(self):
        if not self.selected_brand:
            return
        job = self.jobs.get(self.selected_brand)
        if job:
            job.pause()
            self.update_tree_ui(job)

    def stop(self):
        if not self.selected_brand:
            return
        job = self.jobs.get(self.selected_brand)
        if job:
            job.stop()
            self.update_tree_ui(job)

    def update_tree_ui(self, job):
        self.tree.set(job.brand, "status", job.status)
        self.tree.set(job.brand, "progress", f"{job.progress}%")
        if self.selected_brand == job.brand:
            self.update_log()

    def save_config(self):
        save_config_ui(self.entries, self.frame, self.log, "Convert text2csv")

    def load_config(self):
        load_config_ui(self.entries, self.frame, self.log, "Convert text2csv")

# Other tab can stay simple as placeholder or implemented similarly
class ConvertText2OtherTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Tab Convert text2other chưa được xây dựng").pack(fill=tk.BOTH, expand=True)
