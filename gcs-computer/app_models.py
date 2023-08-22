import tkinter as tk


class TemperatureStatus:
    def __init__(self):
        self.box_temperature = 0
        self.cpu_temperature = 0
        
        self.box_fan = False
        self.rpi_fan = False

class SystemControlData:
    def __init__(self):
        self.override_mode = False
        self.config_cpu_clock = 1500
        self.clock_on_boot = 1500
        self.clock_config = 1500
        self.current_cpu_clock = 0

class GpsStatus:
    def __init__(self):
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.speed = 0
        self.climb = 0
        self.track = 0
        self.time = 0
        self.error = 0
        self.satellites = []

class DataVizControl:
    def __init__(self):
        self.max_upper_freq_bound = 400
        self.min_lower_freq_bound = 0

        self.lower_freq_bound = tk.IntVar()
        self.lower_freq_bound.set(0)
        self.upper_freq_bound = tk.IntVar()
        self.upper_freq_bound.set(200)

        self.min_vmin = -100
        self.max_vmax = 300

        self.vmin = tk.IntVar()
        self.vmin.set(-10)
        self.vmax = tk.IntVar()
        self.vmax.set(10)

        self.max_max_sample_size = 65536 # pow(2, 12) * 16
        self.min_max_sample_size = 4096 # pow(2, 12) * 1
        self.sample_size_step = 1024 # pow(2, 12) / 4

        self.sample_size = tk.IntVar()
        self.sample_size.set(16384)

        self.timeline_offset = tk.IntVar()
        self.timeline_offset.set(0)



