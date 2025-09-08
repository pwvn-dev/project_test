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

class BaseConvertTab:
    # Lớp base cho Convert_AFP và Convert_PWI
    JOB_CONVERT_LABELS = ["Root data", "F2", "Log"]  # Ghi đè ở các lớp con

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.jobs = {}
        self.selected_brand = None

        # Thiết lập config folders
        config_frame = ttk.Labelframe(self.frame, text="Cấu hình thư mục")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        self.entries = []
        for i, label_text in enumerate(self.JOB_CONVERT_LABELS):
            ttk.Label(config_frame, text=label_text + ":").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(config_frame, width=50)
            entry.grid(row=i, column=1, padx=5)
            ttk.Button(config_frame, text="...", command=lambda e=entry: self.browse_folder(e)).grid(row=i, column=2)
            self.entries.append(entry)

        # Thiết lập checkbox thương hiệu
        brand_frame = ttk.Labelframe(self.frame, text="Chọn chức năng chuyển đổi")
        brand_frame.pack(fill=tk.X, padx=10, pady=5)
        self.brand_vars = {}
        for brand in BRANDS:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(brand_frame, text=brand + " function", variable=var)
            cb.pack(side=tk.LEFT, padx=10)
            self.brand_vars[brand] = var

        # Thiết lập Treeview trạng thái
        columns = ("status", "progress")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=8)
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("progress", text="Tiến trình")
        self.tree.column("status", width=150)
        self.tree.column("progress", width=150)
        self.tree.pack(fill=tk.X, padx=10, pady=5)

        self.tree.tag_configure("Running", background="lightgreen")
        self.tree.tag_configure("Paused", background="lightyellow")
        self.tree.tag_configure("Stopped", background="lightgray")
        self.tree.tag_configure("Completed", background="lightblue")

        self.tree.bind("<<TreeviewSelect>>", self.on_job_selected)

        # Panel log chuyển đổi
        ttk.Label(self.frame, text="Log chuyển đổi:").pack(anchor=tk.W, padx=10)
        self.log_text = tk.Text(self.frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Nút điều khiển
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=5)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

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

    def show_action_log(self, message):
        # Hiển thị log chuyển đổi không phụ thuộc chọn dòng
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start(self):
        # Override trong lớp con
        pass

    def pause(self):
        if not self.selected_brand:
            self.show_action_log("No job selected to pause.")
            return
        job = self.jobs.get(self.selected_brand)
        if job and job.status == "Running":
            job.pause()
            self.update_tree_ui(job)
            self.show_action_log(f"{job.brand} conversion paused.")
            self.update_log()
        else:
            self.show_action_log("No running job selected or already paused.")

    def stop(self):
        if not self.selected_brand:
            self.show_action_log("No job selected to stop.")
            return
        job = self.jobs.get(self.selected_brand)
        if job and job.status in ("Running", "Paused"):
            job.stop()
            self.update_tree_ui(job)
            self.show_action_log(f"{job.brand} conversion stopped.")
            self.update_log()
        else:
            self.show_action_log("No running/paused job selected to stop.")

    def update_tree_ui(self, job):
        self.tree.set(job.brand, "status", job.status)
        self.tree.set(job.brand, "progress", f"{job.progress}%")
        self.tree.item(job.brand, tags=(job.status,))
        if self.selected_brand == job.brand:
            self.update_log()

    def save_config(self):
        # Override trong lớp con nếu cần
        pass

    def load_config(self):
        # Override trong lớp con nếu cần
        pass

class Convert_AFP(BaseConvertTab):
    JOB_CONVERT_LABELS = ["Root data", "AFP to DL", "Log"]

    def __init__(self, parent):
        super().__init__(parent)
        self.load_default_config()

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
                self.tree.insert("", tk.END, iid=brand, values=(job.status, f"{job.progress}%"), tags=(job.status,))
                self.show_action_log(f"{brand} conversion started.")
                if self.selected_brand == brand:
                    self.update_log()
                self.jobs[brand].start(self.update_tree_ui)

    def save_config(self):
        save_config_ui(self.entries, self.frame, self.show_action_log, "Convert_AFP")
        import os, json
        default_path = os.path.join(os.getcwd(), "config_convert_afp.json")
        config = {
            "root_data": self.entries[0].get(),
            "dest_folder": self.entries[1].get(),
            "log_folder": self.entries[2].get()
        }
        try:
            with open(default_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.show_action_log(f"Config saved as default: {default_path}")
        except Exception as e:
            self.show_action_log(f"Failed to save default config: {e}")

    def load_config(self):
        load_config_ui(self.entries, self.frame, self.show_action_log, "Convert_AFP")

    def load_default_config(self):
        from config_manager import load_default_config
        load_default_config(self.entries, self.show_action_log, "Convert_AFP")

class Convert_PWI(BaseConvertTab):
    JOB_CONVERT_LABELS = ["Root data", "PWI to DL", "Log"]

    def __init__(self, parent):
        super().__init__(parent)
        self.load_default_config()

    def start(self):
        root_data = self.entries[0].get()
        pwi_to_dl = self.entries[1].get()
        log_dir = self.entries[2].get()
        if not all([root_data, pwi_to_dl, log_dir]):
            messagebox.showwarning("Thiếu dữ liệu", "Hãy điền đầy đủ các thư mục trước khi bắt đầu.")
            return
        selected_brands = [b for b, v in self.brand_vars.items() if v.get()]
        if not selected_brands:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn ít nhất một thương hiệu để chuyển đổi.")
            return
        for brand in selected_brands:
            if brand not in self.jobs or self.jobs[brand].status == "Stopped":
                job = ConvertJob(brand, root_data, pwi_to_dl, log_dir)
                self.jobs[brand] = job
                self.tree.insert("", tk.END, iid=brand, values=(job.status, f"{job.progress}%"), tags=(job.status,))
                self.show_action_log(f"{brand} conversion started.")
                if self.selected_brand == brand:
                    self.update_log()
                self.jobs[brand].start(self.update_tree_ui)

    def save_config(self):
        save_config_ui(self.entries, self.frame, self.show_action_log, "Convert_PWI")
        import os, json
        default_path = os.path.join(os.getcwd(), "config_convert_pwi.json")
        config = {
            "root_data": self.entries[0].get(),
            "dest_folder": self.entries[1].get(),
            "log_folder": self.entries[2].get()
        }
        try:
            with open(default_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.show_action_log(f"Config saved as default: {default_path}")
        except Exception as e:
            self.show_action_log(f"Failed to save default config: {e}")

    def load_config(self):
        load_config_ui(self.entries, self.frame, self.show_action_log, "Convert_PWI")

    def load_default_config(self):
        from config_manager import load_default_config
        load_default_config(self.entries, self.show_action_log, "Convert_PWI")
