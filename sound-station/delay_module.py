import asyncio
import tkinter as tk

import navpy
import numpy as np

UPDATE_DELAYS_WAIT_TIME = 1/2

class DelayModule:
    def __init__(self):
        self.manual_delays_var = tk.BooleanVar()
        self.manual_send_var = tk.BooleanVar()
        self.manual_target_var = tk.BooleanVar()
        self.delay_entries = []
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

    async def calculate_delays(self):

        SOUND_SPEED = 343 #m/s
        TRANSMISSION_FREQ = 1600

        while True:
            
            balloon_lat, balloon_lon, balloon_alt = self.balloon_lla_pos["lat"], self.balloon_lla_pos["lon"], self.balloon_lla_pos["alt"]
            tx_center_lat, tx_center_lon, tx_center_alt = self.subarray_lla_pos["lat"], self.subarray_lla_pos["lon"], self.subarray_lla_pos["alt"]

            balloon_ned = navpy.lla2ned(balloon_lat, balloon_lon, balloon_alt, tx_center_lat, tx_center_lon, tx_center_alt)

            direction_versor = balloon_ned / np.linalg.norm(balloon_ned)

            delays = [0, 0, 0, 0, 0, 0]

            for i in range(1,6):
                sub_ned_pos = self.subwoofer_array["sub{}".format(i)]["ned_pos"]
                delay_dist = np.dot(sub_ned_pos, direction_versor)
                delay_time = (delay_dist / SOUND_SPEED) // (1/TRANSMISSION_FREQ)
                delays[i] = delay_time

            delay_min = min(delays)
            if delay_min < 0:
                delays = [delay - delay_min for delay in delays]

            for i in range(6):
                self.subwoofer_array["sub{}".format(i)]["delay"] = delays[i]

            await asyncio.sleep(UPDATE_DELAYS_WAIT_TIME)
    
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
        