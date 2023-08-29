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
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub1": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub2": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub3": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub4": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            },
            "sub5": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "depth": 0, #meters
                    "depth_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            }
        }