import tkinter as tk
from functools import partial
from tkinter import *
from tkinter.ttk import *

from gps_steering import *


def save_and_exit(top, delay_control):
    delay_control.update_raw_pos_data()
    calculate_ned_positions(delay_control.subwoofer_array)
    top.destroy()

def update_tk_vars(delay_control):
    for sub in delay_control.subwoofer_array:
        for key in delay_control.subwoofer_array[sub]["raw_pos_data"]:
            if not key.endswith("_tk"):
                delay_control.subwoofer_array[sub]["raw_pos_data"][key + "_tk"].set(delay_control.subwoofer_array[sub]["raw_pos_data"][key])

    for key in delay_control.subarray_lla_pos:
        if not key.endswith("_tk"):
            delay_control.subarray_lla_pos[key + "_tk"].set(delay_control.subarray_lla_pos[key])

def open_position_def(root, delay_control):

    update_tk_vars(delay_control)
    top= Toplevel(root)

    main_frame = tk.Frame(top, bd=1, relief=tk.FLAT)
    main_frame.grid(row=0, column=0, padx=10, pady=10)

    tk.Label(main_frame, text="Subwoofer Array Position Definition").grid(row=0, column=0, pady=10)

    pos_frame = tk.Frame(main_frame, bd=1, relief=tk.FLAT)
    pos_frame.grid(row=1, column=0, padx=10, pady=10)

    i = 0
    sub_pos_frame = tk.Frame(pos_frame, bd=1, relief=tk.SUNKEN)
    sub_pos_frame.grid(row=i//2, column=i%2, padx=10, pady=10)

    tk.Label(sub_pos_frame, text="Subwoofer {}".format(i)).grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    tk.Label(sub_pos_frame, text="Latitude").grid(row=1, column=0, padx=10, pady=10)

    latitude_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subarray_lla_pos["lat_tk"])
    latitude_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(sub_pos_frame, text="Longitude").grid(row=2, column=0, padx=10, pady=10)

    longitude_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subarray_lla_pos["lon_tk"])
    longitude_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(sub_pos_frame, text="Altitude").grid(row=3, column=0, padx=10, pady=10)

    altitude_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subarray_lla_pos["alt_tk"])
    altitude_entry.grid(row=3, column=1, padx=10, pady=10)
    
    for i in range(1,6):

        sub_pos_frame = tk.Frame(pos_frame, bd=1, relief=tk.FLAT)
        sub_pos_frame.grid(row=i//2, column=i%2, padx=10, pady=10)

        tk.Label(sub_pos_frame, text="Subwoofer {}".format(i)).grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        tk.Label(sub_pos_frame, text="Orientation").grid(row=1, column=0, padx=10, pady=10)

        orientation_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subwoofer_array["sub{}".format(i)]["raw_pos_data"]["orientation_tk"])
        orientation_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(sub_pos_frame, text="Height").grid(row=2, column=0, padx=10, pady=10)

        height_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subwoofer_array["sub{}".format(i)]["raw_pos_data"]["height_tk"])
        height_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(sub_pos_frame, text="Distance").grid(row=3, column=0, padx=10, pady=10)

        distance_entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subwoofer_array["sub{}".format(i)]["raw_pos_data"]["distance_tk"])
        distance_entry.grid(row=3, column=1, padx=10, pady=10)

    # save and exit config button

    tk.Button(main_frame, text="Save and Exit", command=partial(save_and_exit, top, delay_control)).grid(row=2, column=0, padx=10, pady=10)



