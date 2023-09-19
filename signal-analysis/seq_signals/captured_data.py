import pandas as pd


class CapturedData:
    def __init__(self, file_path, sampling_rate=800):
        self.file_path = file_path
        self.sampling_rate = sampling_rate
        self.data = self.load_data()

    def load_data(self):
        return pd.read_csv(self.file_path)
