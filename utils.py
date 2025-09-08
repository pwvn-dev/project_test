import sys
import os

def resource_path(relative_path):
    """ Trả về đường dẫn tuyệt đối tới tài nguyên,
        tương thích khi chạy script hoặc exe PyInstaller """
    try:
        base_path = sys._MEIPASS  # Folder tạm khi chạy exe đóng gói PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
