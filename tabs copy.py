import tkinter as tk
from tkinter import ttk
from converter import TxtToCsvConverter
import config_manager

def open_path(entry_widget):
    from tkinter import filedialog
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)

class BaseConvertTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="TFrame")

        labels = ["Root data", "AFP to DL", "Log"]
        self.entries = []

        ypos = [40, 100, 160]

        for i, label_text in enumerate(labels):
            label = ttk.Label(self.frame, text=label_text, style="label.TLabel")
            label.place(x=50, y=ypos[i], width=120, height=32)
            entry = ttk.Entry(self.frame, style="entry.TEntry")
            entry.place(x=180, y=ypos[i], width=520, height=32)
            self.entries.append(entry)
            button = ttk.Button(self.frame, text="...", style="button.TButton",
                                command=lambda e=entry: open_path(e))
            button.place(x=720, y=ypos[i], width=50, height=32)

        self.log_text = tk.Text(self.frame, width=96, height=18, state='disabled')
        self.log_text.place(x=32, y=220, width=820, height=320)

        style = ttk.Style()
        style.configure("button_green.TButton", background="#00ff0d", foreground="#000")
        style.map("button_green.TButton", background=[("active", "#00ff0d")])
        style.configure("button_yellow.TButton", background="#fffb00", foreground="#000")
        style.map("button_yellow.TButton", background=[("active", "#fffb00")])
        style.configure("button_red.TButton", background="#ec0000", foreground="#000")
        style.map("button_red.TButton", background=[("active", "#ec0000")])
        style.configure("button_blue.TButton", background="#0078d7", foreground="#fff")
        style.map("button_blue.TButton", background=[("active", "#005a9e")])

        self.start_btn = ttk.Button(self.frame, text="Start", style="button_green.TButton", width=15,
                                   command=self.start_conversion)
        self.start_btn.place(x=130, y=570, width=180, height=50)

        self.pause_btn = ttk.Button(self.frame, text="Pause", style="button_yellow.TButton", width=15,
                                   command=self.pause_conversion)
        self.pause_btn.place(x=360, y=570, width=180, height=50)

        self.stop_btn = ttk.Button(self.frame, text="Stop", style="button_red.TButton", width=15,
                                  command=self.stop_conversion)
        self.stop_btn.place(x=590, y=570, width=180, height=50)

        self.save_btn = ttk.Button(self.frame, text="Save Config", style="button_blue.TButton", width=15,
                                   command=self.save_config)
        self.save_btn.place(x=240, y=635, width=180, height=45)

        self.load_btn = ttk.Button(self.frame, text="Load Config", style="button_blue.TButton", width=15,
                                   command=self.load_config)
        self.load_btn.place(x=480, y=635, width=180, height=45)

        self.converter = None

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_conversion(self):
        source = self.entries[0].get().strip()
        dest = self.entries[1].get().strip()
        log_dir = self.entries[2].get().strip()
        if not all([source, dest, log_dir]):
            self.log("Please fill all folder paths before starting.\n")
            return
        if self.converter and self.converter.thread and self.converter.thread.is_alive():
            self.log("Already running\n")
            return
        self.converter = TxtToCsvConverter(source, dest, log_dir, self.log)
        self.converter.start()

    def pause_conversion(self):
        if self.converter:
            self.converter.pause()

    def stop_conversion(self):
        if self.converter:
            self.converter.stop()

    def save_config(self):
        config_manager.save_config_ui(self.entries, self.frame, self.log, self.__class__.__name__)

    def load_config(self):
        config_manager.load_config_ui(self.entries, self.frame, self.log, self.__class__.__name__)

class ConvertText2CSVTab(BaseConvertTab):
    pass

class ConvertText2OtherTab(BaseConvertTab):
    pass
