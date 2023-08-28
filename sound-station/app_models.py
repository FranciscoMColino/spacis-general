import tkinter as tk


class GpsStatus:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.track = 0
        self.speed = 0
        self.climb = 0
        self.error = 0

class DelayControl:
    def __init__(self):
        self.manual_delays_var = tk.BooleanVar()
        self.manual_send_var = tk.BooleanVar()
        self.entry_boxes = []
        self.subwoofer_array = {
            "sub0": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub1": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub2": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub3": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub4": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub5": {
                "ned_pos": [0, 0, 0],
                "delay": 0
            }
        }