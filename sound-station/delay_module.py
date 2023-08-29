import tkinter as tk

UPDATE_DELAYS_WAIT_TIME = 1/10

class DelayModule:
    def __init__(self):
        self.manual_delays_var = tk.BooleanVar()
        self.manual_send_var = tk.BooleanVar()
        self.manual_target_var = tk.BooleanVar()
        self.entry_boxes = []
        self.balloon_lla_pos = {
            "lat": 0,
            "lat_tk": tk.DoubleVar(),
            "lon": 0,
            "lon_tk": tk.DoubleVar(),
            "alt": 0,
            "alt_tk": tk.DoubleVar(),
        }
        self.subarray_lla_pos = {
            "lat": 0.00,
            "lat_tk": tk.DoubleVar(),
            "lon": 0.00,
            "lon_tk": tk.DoubleVar(),
            "alt": 0.00,
            "alt_tk": tk.DoubleVar(),
        }
        self.subwoofer_array = {
            "sub0": {
                "raw_pos_data": {
                    "orientation": 0, #degrees
                    "orientation_tk": tk.IntVar(),
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
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
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
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
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
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
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
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
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
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
                    "height": 0, #meters
                    "height_tk": tk.IntVar(),
                    "distance": 0, #meters
                    "distance_tk": tk.IntVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay": 0
            }
        }
    
    def update_raw_pos_data(self):

        self.subarray_lla_pos["lat"] = self.subarray_lla_pos["lat_tk"].get()
        self.subarray_lla_pos["lon"] = self.subarray_lla_pos["lon_tk"].get()
        self.subarray_lla_pos["alt"] = self.subarray_lla_pos["alt_tk"].get()

        for i in range(1,6):
            sub = self.subwoofer_array["sub{}".format(i)]
            sub["raw_pos_data"]["orientation"] = sub["raw_pos_data"]["orientation_tk"].get()
            sub["raw_pos_data"]["height"] = sub["raw_pos_data"]["height_tk"].get()
            sub["raw_pos_data"]["distance"] = sub["raw_pos_data"]["distance_tk"].get()

    #def update_delays(self):
        