import json
import os
from tkinter import filedialog, messagebox

def save_config_ui(entries, parent, log_func, tab_name="Config"):
    default_filename = f"config_{tab_name.lower()}.json"
    path = filedialog.asksaveasfilename(
        parent=parent,
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=default_filename,
        title=f"Save configuration for {tab_name}..."
    )
    if not path:
        return

    config = {
        "root_data": entries[0].get().strip(),
        "dest_folder": entries[1].get().strip(),
        "log_folder": entries[2].get().strip()
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        log_func(f"Config saved successfully:\n{path}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save config: {e}")

def load_config_ui(entries, parent, log_func, tab_name="Config"):
    default_filename = f"config_{tab_name.lower()}.json"
    path = filedialog.askopenfilename(
        parent=parent,
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=default_filename,
        title=f"Load configuration for {tab_name}..."
    )
    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        entries[0].delete(0, "end")
        entries[0].insert(0, config.get("root_data", ""))
        entries[1].delete(0, "end")
        entries[1].insert(0, config.get("dest_folder", ""))
        entries[2].delete(0, "end")
        entries[2].insert(0, config.get("log_folder", ""))
        log_func(f"Config loaded successfully:\n{path}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load config: {e}")

def load_default_config(entries, log_func, tab_name="Config"):
    """ Hàm load config mặc định theo file tên định sẵn trong folder chạy """
    default_path = os.path.join(os.getcwd(), f"config_{tab_name.lower()}.json")
    if os.path.exists(default_path):
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            entries[0].delete(0, "end")
            entries[0].insert(0, config.get("root_data", ""))
            entries[1].delete(0, "end")
            entries[1].insert(0, config.get("dest_folder", ""))
            entries[2].delete(0, "end")
            entries[2].insert(0, config.get("log_folder", ""))
            log_func(f"Loaded default config: {default_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default config: {e}")
