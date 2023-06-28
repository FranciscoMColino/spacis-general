class TemperatureStatus:
    def __init__(self):
        self.current_temperature = 0
        self.fan_speed = [0, 0]
        self.override_mode = False
        self.fan_active = [False, False]

class CommandActionsState:
    def __init__(self):
        self.override_button_state = False
        self.fan_button_state = False
        self.fan_speed = None
        self.cpu_clock = 2200

class GpsStatus:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
