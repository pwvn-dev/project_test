# zeiss-AFP.py
import time

class BaseConverterAFP:
    def __init__(self, root_data, afp_to_dl, log_dir):
        self.root_data = root_data
        self.afp_to_dl = afp_to_dl
        self.log_dir = log_dir

    def read_input(self):
        raise NotImplementedError("read_input phải được triển khai trong class con")

    def process(self):
        raise NotImplementedError("process phải được triển khai trong class con")

    def write_output(self):
        raise NotImplementedError("write_output phải được triển khai trong class con")

    def run(self, progress_callback=None, log_callback=None):
        if log_callback:
            log_callback("Bắt đầu đọc dữ liệu đầu vào...")
        self.read_input()
        if log_callback:
            log_callback("Xử lý dữ liệu...")
        self.process()
        if log_callback:
            log_callback("Ghi kết quả đầu ra...")
        self.write_output()
        if log_callback:
            log_callback("Hoàn tất chuyển đổi.")

class ZeissConverterAFP(BaseConverterAFP):
    def __init__(self, root_data, afp_to_dl, log_dir):
        super().__init__(root_data, afp_to_dl, log_dir)
        self.progress = 0

    def read_input(self):
        # Ví dụ mô phỏng đọc 5 file mất 1 giây mỗi file
        for i in range(5):
            time.sleep(1)
            self.progress = (i + 1) * 10
        # Thực tế ở đây bạn đọc và xử lý file dữ liệu
        pass

    def process(self):
        # Mô phỏng xử lý mất 3 giây từng phần
        for i in range(3):
            time.sleep(1)
            self.progress += 10
        pass

    def write_output(self):
        # Mô phỏng ghi file mất 2 giây
        for i in range(2):
            time.sleep(1)
            self.progress += 10
        pass

    def run(self, progress_callback=None, log_callback=None):
        if log_callback:
            log_callback("ZeissConverter started.")
        self.progress = 0
        self.read_input()
        if progress_callback:
            progress_callback(self.progress)
        self.process()
        if progress_callback:
            progress_callback(self.progress)
        self.write_output()
        if progress_callback:
            progress_callback(self.progress)
        if log_callback:
            log_callback("ZeissConverter finished.")
