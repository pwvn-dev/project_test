import tkinter as tk
from tkinter import ttk, messagebox

from license_window import LicenseWindow
from app_gui import ConvertApp

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập")
        self.root.geometry("350x180")
        self.root.resizable(False, False)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TLabel", font=(None, 12))
        style.configure("TEntry", font=(None, 12))

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="User:").grid(row=0, column=0, sticky="w", pady=10)
        self.user_entry = ttk.Entry(frame)
        self.user_entry.grid(row=0, column=1, pady=10)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w", pady=10)
        self.pass_entry = ttk.Entry(frame, show="*")
        self.pass_entry.grid(row=1, column=1, pady=10)

        submit_btn = ttk.Button(frame, text="Submit", command=self.check_login)
        submit_btn.grid(row=2, column=0, columnspan=2, pady=15)

        # Bind phím Enter
        self.pass_entry.bind("<Return>", lambda e: self.check_login())

    def check_login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()

        # Ví dụ kiểm tra cứng:
        if user == "admin" and password == "1234":
            self.root.destroy()  # Đóng cửa sổ login

            # Sau khi login, mở LicenseWindow kiểm tra license
            def open_app_after_license(user):
                main_root = tk.Tk()
                app = ConvertApp(main_root)
                main_root.mainloop()

            license_root = tk.Tk()
            license_win = LicenseWindow(license_root, open_app_after_license)
            license_root.mainloop()
        else:
            messagebox.showerror("Lỗi đăng nhập", "User hoặc Password không đúng, vui lòng thử lại.")
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()
