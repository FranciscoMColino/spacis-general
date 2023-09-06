
class GpsModule:
    def __init__(self, delay_module):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.track = 0
        self.speed = 0
        self.climb = 0
        self.error = 0
        self.delay_module = delay_module

    def update_gps_data(self, data):

        try:
            
            self.latitude = data["lat"]
            self.longitude = data["lon"]
            self.altitude = data["alt"]
            self.track = data["track"]
            self.speed = data["speed"]
            self.climb = data["climb"]
            self.error = data["error"]

            if (not self.delay_module.manual_target_var.get()):
                try:
                    self.delay_module.balloon_lla_pos["lat"] = float(self.latitude)
                    self.delay_module.balloon_lla_pos["lon"] = float(self.longitude)
                    self.delay_module.balloon_lla_pos["alt"] = float(self.altitude)
                except ValueError as e:
                    print("LOG: ", e)

        except Exception as e:
            print("LOG: Exception while updating gps data ", e)