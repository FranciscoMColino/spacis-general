import numpy as np
import pandas as pd


class SingleSequence:
    def __init__(self, file_path):
        self.sample_freq = 1600
        self.signal = (np.array([0]).repeat(100) + np.array([1]).repeat(100)).repeat(6)
        self.signal = np.array(pd.read_csv(file_path)['values'].to_list())
        self.signal = np.append(self.signal, np.zeros(100))
        self.signal = np.repeat(self.signal, 4)
        self.vmin = -20
        self.vmax = -10
