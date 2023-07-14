class TemperatureStatus:
    def __init__(self):
        self.box_temperature = 0
        self.cpu_temperature = 0
        
        self.box_fan = False
        self.rpi_fan = False

class SystemControlData:
    def __init__(self):
        self.override_mode = False
        self.config_cpu_clock = 1500 #TODO change this and join with temperaturestatus
        self.clock_on_boot = 1500
        self.clock_config = 1500
        self.current_cpu_clock = 0

class GpsStatus:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
