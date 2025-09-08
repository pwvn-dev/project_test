import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from tabs import Convert_AFP, Convert_PWI
from utils import resource_path

from zeiss_AFP import ZeissTxtToCsvConverter  # import converter bạn đã tạo

BASE_DIR = os.path.abspath(".")

class ConvertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PWTH-Dataloop_Zeiss2AFP")
        window_width = 900
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.config(bg="#E4E2E2")

        icon_path = resource_path("assets/icon_1755948263.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_img = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(False, icon_img)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#E4E2E2")

        tab_control = ttk.Notebook(self.root)
        tab_control.pack(expand=True, fill=tk.BOTH)

        # Khởi tạo tab
        self.tab_csv = Convert_AFP(tab_control)
        self.tab_other = Convert_PWI(tab_control)

        tab_control.add(self.tab_csv.frame, text="PW_Convert_AFP")
        tab_control.add(self.tab_other.frame, text="PW_Convert_PWI")

        # Khởi tạo converter Zeiss, truyền log callback vào tab Convert_AFP
        self.converter = ZeissTxtToCsvConverter(
            self.tab_csv.entries[0].get(),
            self.tab_csv.entries[1].get(),
            self.tab_csv.entries[2].get(),
            self.tab_csv.show_action_log  # dùng hàm log hiển thị của tab CSV
        )

        # Thay thế start/pause/stop nút của tab Convert_AFP để gọi converter thực
        # Lưu giữ cách gọi cũ để tránh trùng lặp (hoặc comment tạm)
        self.tab_csv.start = self.start_conversion
        self.tab_csv.pause = self.pause_conversion
        self.tab_csv.stop = self.stop_conversion

    def start_conversion(self):
        # Cập nhật lại thư mục mới trước khi start
        self.converter.root_dir = os.path.join(self.tab_csv.entries[0].get(), "Zeiss")
        self.converter.dest_dir = os.path.join(self.tab_csv.entries[1].get(), "Zeiss")
        self.converter.log_dir = os.path.join(self.tab_csv.entries[2].get(), "Zeiss")
        self.converter.log(f"Starting conversion in:")
        self.converter.log(f"Root: {self.converter.root_dir}")
        self.converter.log(f"Destination: {self.converter.dest_dir}")
        self.converter.log(f"Log directory: {self.converter.log_dir}")
        self.converter.start()

    def pause_conversion(self):
        self.converter.pause()

    def stop_conversion(self):
        self.converter.stop()

def main():
    root = tk.Tk()
    app = ConvertApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
