import datetime

import numpy as np


class DataManager:
    def __init__(self,):
        # filename given by current timestamp
        self.file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.data_dir = './records/' + self.file_name + '.csv'
        # create file
        self.file = open(self.data_dir, 'w')
        self.file.write('sensor_1,sensor_2,sensor_3,sensor_4,delay\n')
        self.local_data = np.array([])
        self.MAX_NO_SENQ = 100
        self.LOCAL_SIZE_LIMIT = pow(2, 12) * 4 * 100
    
    def record_data(self, data):
        self.local_data = np.append(self.local_data, data)
        for line in data:
            line_str_cv = [str(i) for i in line]
            self.file.write(','.join(line_str_cv) + '\n')
        if self.local_data.size > self.LOCAL_SIZE_LIMIT:
            self.local_data = self.local_data[len(self.local_data)-self.MAX_NO_SENQ:]