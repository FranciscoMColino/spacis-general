import asyncio
import tkinter as tk

import navpy
import numpy as np
from gps_steering import calculate_ned_positions

UPDATE_DELAYS_WAIT_TIME = 1/2

DELAY_OFFSET = 25


class DelayModule:
    def __init__(self, settings):
        self.manual_delays_var = tk.BooleanVar()
        self.manual_send_var = tk.BooleanVar()
        self.manual_target_var = tk.BooleanVar()

        self.azimuth = 0
        self.elevation = 0

        self.delay_entries = []
        self.balloon_lla_pos = {
            "lat": settings["balloon_target_lla"][0],
            "lat_tk": tk.DoubleVar(),
            "lon": settings["balloon_target_lla"][1],
            "lon_tk": tk.DoubleVar(),
            "alt": settings["balloon_target_lla"][2],
            "alt_tk": tk.DoubleVar(),
        }
        self.subarray_lla_pos = {
            "lat": settings["sound_station_lla"][0],
            "lat_tk": tk.DoubleVar(),
            "lon": settings["sound_station_lla"][1],
            "lon_tk": tk.DoubleVar(),
            "alt": settings["sound_station_lla"][2],
            "alt_tk": tk.DoubleVar(),
        }
        self.subwoofer_array = {
            "sub0": {
                "raw_pos_data": {
                    "orientation": 0,  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": 0,  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": 0,  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            },
            "sub1": {
                "raw_pos_data": {
                    "orientation": settings["sub1_orientation"],  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": settings["sub1_height"],  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": settings["sub1_distance"],  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            },
            "sub2": {
                "raw_pos_data": {
                    "orientation": settings["sub2_orientation"],  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": settings["sub2_height"],  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": settings["sub2_distance"],  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            },
            "sub3": {
                "raw_pos_data": {
                    "orientation": settings["sub3_orientation"],  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": settings["sub3_height"],  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": settings["sub3_distance"],  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            },
            "sub4": {
                "raw_pos_data": {
                    "orientation": settings["sub4_orientation"],  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": settings["sub4_height"],  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": settings["sub4_distance"],  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            },
            "sub5": {
                "raw_pos_data": {
                    "orientation": settings["sub5_orientation"],  # degrees
                    "orientation_tk": tk.DoubleVar(),
                    "height": settings["sub5_height"],  # meters
                    "height_tk": tk.DoubleVar(),
                    "distance": settings["sub5_distance"],  # meters
                    "distance_tk": tk.DoubleVar(),
                },
                "ned_pos": [0, 0, 0],
                "delay_tk": tk.IntVar(value=0),
                "delay": 0
            }
        }

        self.update_azi_ele()
        calculate_ned_positions(self.subwoofer_array)

    async def calculate_delays(self):

        SOUND_SPEED = 343  # m/s
        TRANSMISSION_FREQ = 1600

        while True:

            if self.manual_delays_var.get():
                await asyncio.sleep(UPDATE_DELAYS_WAIT_TIME)
                continue

            balloon_lat, balloon_lon, balloon_alt = self.balloon_lla_pos[
                "lat"], self.balloon_lla_pos["lon"], self.balloon_lla_pos["alt"]
            tx_center_lat, tx_center_lon, tx_center_alt = self.subarray_lla_pos[
                "lat"], self.subarray_lla_pos["lon"], self.subarray_lla_pos["alt"]

            if balloon_lat == tx_center_lat and balloon_lon == tx_center_lon and balloon_alt == tx_center_alt:
                await asyncio.sleep(UPDATE_DELAYS_WAIT_TIME)
                continue

            balloon_ned = navpy.lla2ned(
                balloon_lat, balloon_lon, balloon_alt, tx_center_lat, tx_center_lon, tx_center_alt)

            direction_versor = balloon_ned / np.linalg.norm(balloon_ned)

            delays = [0, 0, 0, 0, 0, 0]

            delays[0] = DELAY_OFFSET

            for i in range(1, 6):
                sub_ned_pos = self.subwoofer_array["sub{}".format(
                    i)]["ned_pos"]
                delay_dist = np.dot(sub_ned_pos, direction_versor)
                delay_time = round(
                    (delay_dist / SOUND_SPEED) / (1/TRANSMISSION_FREQ))
                delays[i] = delay_time + DELAY_OFFSET

            delay_min = min(delays)
            if delay_min < 0:
                delays = [delay - delay_min for delay in delays]

            for i in range(6):
                self.subwoofer_array["sub{}".format(i)]["delay"] = delays[i]

            await asyncio.sleep(UPDATE_DELAYS_WAIT_TIME)

    def update_delays(self, *args):

        if not self.manual_delays_var.get():
            return

        for i in range(6):
            self.subwoofer_array["sub{}".format(
                i)]["delay"] = self.subwoofer_array["sub{}".format(i)]["delay_tk"].get()

    def update_target(self):
        if self.manual_target_var.get():
            self.balloon_lla_pos["lat"] = self.balloon_lla_pos["lat_tk"].get()
            self.balloon_lla_pos["lon"] = self.balloon_lla_pos["lon_tk"].get()
            self.balloon_lla_pos["alt"] = self.balloon_lla_pos["alt_tk"].get()

        self.update_azi_ele()

    def update_raw_pos_data(self):

        self.subarray_lla_pos["lat"] = self.subarray_lla_pos["lat_tk"].get()
        self.subarray_lla_pos["lon"] = self.subarray_lla_pos["lon_tk"].get()
        self.subarray_lla_pos["alt"] = self.subarray_lla_pos["alt_tk"].get()

        for i in range(1, 6):
            sub = self.subwoofer_array["sub{}".format(i)]
            sub["raw_pos_data"]["orientation"] = sub["raw_pos_data"]["orientation_tk"].get()
            sub["raw_pos_data"]["height"] = sub["raw_pos_data"]["height_tk"].get()
            sub["raw_pos_data"]["distance"] = sub["raw_pos_data"]["distance_tk"].get()

        self.update_azi_ele()

    def update_azi_ele(self):

        fi1 = np.radians(self.subarray_lla_pos["lat"])
        fi2 = np.radians(self.balloon_lla_pos["lat"])
        delta_lambda = np.radians(
            self.balloon_lla_pos["lon"] - self.subarray_lla_pos["lon"])
        x = np.cos(fi2) * np.sin(delta_lambda)
        y = np.cos(fi1) * np.sin(fi2) - np.sin(fi1) * \
            np.cos(fi2) * np.cos(delta_lambda)
        azimuth = np.arctan2(x, y)

        self.azimuth = ((azimuth * 180 / np.pi) + 360) % 360
        self.elevation = 0
