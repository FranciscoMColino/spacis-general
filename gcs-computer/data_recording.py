import datetime

BASE_DIR = './records/'
SENSOR_RECORD_SUFFIX = 'sensor_records'
TEMPERATURE_RECORD_SUFFIX = 'temperature_records'
GPS_RECORD_SUFFIX = 'gps_records'
PPS_RECORD_SUFFIX = 'pps_records'
BATCH_RECORD_SUFFIX = 'batch_records'


class DataRecorder:
    def __init__(self,):
        # filename given by current timestamp
        self.time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        self.sensor_record_path = BASE_DIR + '/' + SENSOR_RECORD_SUFFIX + \
            '/' + SENSOR_RECORD_SUFFIX + self.time_stamp + '.csv'
        self.temperature_record_path = BASE_DIR + '/' + TEMPERATURE_RECORD_SUFFIX + \
            '/' + TEMPERATURE_RECORD_SUFFIX + self.time_stamp + '.csv'
        self.gps_record_path = BASE_DIR + '/' + GPS_RECORD_SUFFIX + \
            '/' + GPS_RECORD_SUFFIX + self.time_stamp + '.csv'
        self.pps_record_path = BASE_DIR + '/' + PPS_RECORD_SUFFIX + \
            '/' + PPS_RECORD_SUFFIX + self.time_stamp + '.csv'
        self.batch_record_path = BASE_DIR + '/' + BATCH_RECORD_SUFFIX + \
            '/' + BATCH_RECORD_SUFFIX + self.time_stamp + '.csv'

        self.setup_sensor_record()
        self.setup_temperature_record()
        self.setup_gps_record()
        self.setup_pps_record()
        self.setup_batch_record()

    def setup_sensor_record(self):
        self.sensor_record_file = open(self.sensor_record_path, 'a')
        self.sensor_record_file.write(
            'sensor_1,sensor_2,sensor_3,sensor_4,delay\n')
        self.local_data = []
        # self.MAX_NO_SENQ = 100
        # self.LOCAL_SIZE_LIMIT = pow(2, 12) * 4 * 100

    def setup_temperature_record(self):
        self.temperature_record_file = open(self.temperature_record_path, 'a')
        self.temperature_record_file.write('box_temp,cpu_temp\n')

    def setup_gps_record(self):
        self.gps_record_file = open(self.gps_record_path, 'a')
        self.gps_record_file.write(
            'lat,lon,alt,speed,climb,track,time,error\n')

    def setup_pps_record(self):
        self.pps_record_file = open(self.pps_record_path, 'a')
        self.pps_record_file.write('id, time\n')
        self.pps_record_file.flush()

    def setup_batch_record(self):
        self.batch_record_file = open(self.batch_record_path, 'a')
        self.batch_record_file.write('id, size\n')
        self.batch_record_file.flush()

    def stop(self):
        self.sensor_record_file.close()
        self.temperature_record_file.close()
        self.gps_record_file.close()

    def record_sensor_data(self, data, elapsed, pps_id, batch_id=0):
        transformed_data = [str(x) for x in data]
        transformed_data.extend([str(elapsed), str(pps_id), str(batch_id)])
        self.sensor_record_file.write(','.join(transformed_data) + '\n')

    def record_multiple_sensor_data(self, data, elapsed, pps_id, batch_id=0):
        # self.local_data.extend(data)
        for line in data:
            try:
                self.record_sensor_data(
                    line, elapsed.pop(0), pps_id.pop(0), batch_id)
            except Exception as e:
                print('Error recording sensor data: {} on {} {} {}'.format(
                    e, line, elapsed, pps_id))
        # if len(self.local_data) > self.LOCAL_SIZE_LIMIT:
        #    self.local_data = self.local_data[len(self.local_data)-self.MAX_NO_SENQ:]
        self.sensor_record_file.flush()

    def record_gps_data(self, data):
        transformed_data = [str(x) for x in data]
        self.gps_record_file.write(','.join(transformed_data) + '\n')
        self.gps_record_file.flush()

    def record_pps_data(self, data):
        transformed_data = [str(x) for x in data]
        self.pps_record_file.write(','.join(transformed_data) + '\n')
        self.pps_record_file.flush()

    def record_temperature_data(self, data):
        transformed_data = [str(round(x, 2)) for x in data]
        current_time = datetime.datetime.now()
        transformed_data.append(current_time.strftime(
            "%H-%M-%S") + f".{current_time.microsecond // 1000:03d}")
        self.temperature_record_file.write(','.join(transformed_data) + '\n')
        self.temperature_record_file.flush()

    def record_batch_data(self, batch_id, batch_size):
        transformed_data = [str(x) for x in [batch_id, batch_size]]
        self.batch_record_file.write(','.join(transformed_data) + '\n')
        self.batch_record_file.flush()
