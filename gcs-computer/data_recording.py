import datetime


class DataRecorder:
    def __init__(self,):
        # filename given by current timestamp
        self.file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.data_dir = './records/' + self.file_name + '.csv'
        # create file
        self.file = open(self.data_dir, 'w')
        self.file.write('sensor_1,sensor_2,sensor_3,sensor_4,delay\n')
    
    def record_data(self, data):
        
        for line in data:
            line_str_cv = [str(i) for i in line]
            self.file.write(','.join(line_str_cv) + '\n')