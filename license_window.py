import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime

# Thư viện mã hóa AES
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import os

def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_license(token_str, password):
    try:
        token_bytes = base64.b64decode(token_str)
        salt = token_bytes[:16]
        token = token_bytes[16:]
        key = derive_key(password, salt)
        f = Fernet(key)
        decrypted = f.decrypt(token)
        return json.loads(decrypted.decode())
    except Exception as e:
        raise ValueError(f"Giải mã license lỗi: {e}")

class LicenseWindow:
    def __init__(self, root, on_valid_license_callback):
        self.root = root
        self.on_valid_license_callback = on_valid_license_callback

        self.root.title("Nhập License")
        self.root.geometry("420x220")
        self.root.resizable(False, False)

        style = ttk.Style(root)
        style.theme_use("clam")

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Chọn file license:").grid(row=0, column=0, sticky="w")
        self.license_path_var = tk.StringVar()
        license_entry = ttk.Entry(frame, textvariable=self.license_path_var, width=40)
        license_entry.grid(row=0, column=1)
        browse_btn = ttk.Button(frame, text="Chọn file", command=self.browse_license_file)
        browse_btn.grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="Mật khẩu giải mã:").grid(row=1, column=0, sticky="w", pady=15)
        self.password_entry = ttk.Entry(frame, show="*", width=42)
        self.password_entry.grid(row=1, column=1, columnspan=2)

        submit_btn = ttk.Button(frame, text="Kiểm tra license", command=self.check_license)
        submit_btn.grid(row=2, column=0, columnspan=3, pady=15)

        self.password_entry.bind("<Return>", lambda e: self.check_license())

    def browse_license_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file license",
            filetypes=[("License files", "*.lic *.json"), ("All files", "*.*")]
        )
        if path:
            self.license_path_var.set(path)

    def check_license(self):
        path = self.license_path_var.get()
        password = self.password_entry.get()

        if not path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file license.")
            return

        if not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu giải mã.")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                token_str = f.read()
            license_data = decrypt_license(token_str, password)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không giải mã được license:\n{e}")
            return

        user = license_data.get("user")
        expiry = license_data.get("expiry")  # "YYYY-MM-DD"

        if not user or not expiry:
            messagebox.showerror("Lỗi", "Dữ liệu license không hợp lệ.")
            return

        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        except:
            messagebox.showerror("Lỗi", "Ngày hết hạn license không đúng định dạng.")
            return

        today = datetime.today().date()
        if today > expiry_date:
            messagebox.showerror("Lỗi", "License đã hết hạn.")
            return

        messagebox.showinfo("Thành công", f"License hợp lệ cho user: {user}")
        self.root.destroy()
        self.on_valid_license_callback(user)
