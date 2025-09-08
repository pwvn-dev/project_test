class BaseConverterPWI:
    def __init__(self, root_data, afp_to_dl, log_dir):
        self.root_data = root_data
        self.afp_to_dl = afp_to_dl
        self.log_dir = log_dir

    def read_input(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError

    def write_output(self):
        raise NotImplementedError

    def run(self, progress_callback=None, log_callback=None):
        if log_callback: log_callback("Start conversion PWI")
        self.read_input()
        self.process()
        self.write_output()
        if log_callback: log_callback("End conversion PWI")
