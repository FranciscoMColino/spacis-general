import tkinter as tk


class DataVizControl:
    def __init__(self):

        self.select_spec_options = [
            "Sensor 0",
            "Sensor 1",
            "Sensor 2",
            "Sensor 3",
            "All Sensors",
        ]
        #self.all_sensors_mode = False

        self.selected_spec_mode = tk.StringVar()
        self.selected_spec_mode.set(self.select_spec_options[0])

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