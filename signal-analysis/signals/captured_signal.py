import numpy as np
import pandas as pd


class CapturedSignal:
    def __init__(self, path):
        df = pd.read_csv(path)
        self.sample_freq = 1600
        self.signal = np.array(df["sensor_1"].to_list())
        self.vmin = -5
        self.vmax = 30        
