class TemperatureStatus:
    def __init__(self):
        self.box_temperature = 0
        self.cpu_temperature = 0
        self.override_mode = False
        self.box_fan = False
        self.rpi_fan = False

class CommandActionsState:
    def __init__(self):
        self.cpu_clock = 2200

class GpsStatus:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
