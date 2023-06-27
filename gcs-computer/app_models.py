class TemperatureStatus:
    def __init__(self):
        self.current_temperature = 0
        self.fan_speed = [0, 0]
        self.override_mode = False
        self.fan_active = [False, False]

class CommandButtonsState:
    def __init__(self):
        self.override_button_state = False
        self.fan_button_state = False
