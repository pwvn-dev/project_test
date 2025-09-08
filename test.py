import tkinter as tk
import os
from utils import resource_path

root = tk.Tk()

icon_path = resource_path("assets/icon_1755948263.ico")  # Đổi tên cho đúng file .ico bạn có
print("Icon path (debug):", icon_path)

if os.path.exists(icon_path):
    try:
        root.iconbitmap(default=icon_path)
        print("Icon set OK")
    except Exception as e:
        print("Không thể đặt icon:", e)
else:
    print("Không tìm thấy icon:", icon_path)

root.mainloop()
