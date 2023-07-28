class PerformanceRecordings:
    def __init__(self):
        self.measure_to_path = {
            "root_update": "./performance/root_update.csv",
            "update_sensor_data": "./performance/update_sensor_data.csv",
            "update_spectogram": "./performance/update_spectogram.csv",
        }
        self.measure_to_file = {}
        self.clear_files()
        self.setup()

    def setup(self):

        for measure, path in self.measure_to_path.items():
            self.measure_to_file[measure] = open(path, "a")
            self.measure_to_file[measure].write("time\n")

    def clear_files(self):
        for measure, path in self.measure_to_path.items():
            self.measure_to_file[measure] = open(path, "w")
            self.measure_to_file[measure].write("time\n")
            self.measure_to_file[measure].close()

    def record(self, measure, time):
        self.measure_to_file[measure].write(f"{time}\n")
        self.measure_to_file[measure].flush()


