import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tabs import Convert_AFP, Convert_PWI
from utils import resource_path

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

        tab_csv = Convert_AFP(tab_control)
        tab_other = Convert_PWI(tab_control)

        tab_control.add(tab_csv.frame, text="Convert text2csv")
        tab_control.add(tab_other.frame, text="Convert text2other")

def main():
    root = tk.Tk()
    app = ConvertApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
