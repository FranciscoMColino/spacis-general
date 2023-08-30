import tkinter as tk
from functools import partial
from tkinter import *
from tkinter.ttk import *


def save_and_exit(top, delay_control):
    delay_control.update_target()
    top.destroy()

def update_tk_vars(delay_control):
    for key in delay_control.balloon_lla_pos:
        if not key.endswith("_tk"):
            delay_control.balloon_lla_pos[key + "_tk"].set(delay_control.balloon_lla_pos[key])


def open_target_def(root, delay_control):

    update_tk_vars(delay_control)

    top= Toplevel(root)

    main_frame = tk.Frame(top, bd=1, relief=tk.FLAT)
    main_frame.grid(row=0, column=0, padx=10, pady=10)

    tk.Label(main_frame, text="Subwoofer Array Position Definition").grid(row=0, column=0, pady=10)

    pos_frame = tk.Frame(main_frame, bd=1, relief=tk.FLAT)
    pos_frame.grid(row=1, column=0, padx=10, pady=10)

    tk.Label(pos_frame, text="Latitude").grid(row=1, column=0, padx=10, pady=10)

    latitude_entry = tk.Entry(pos_frame, textvariable=delay_control.balloon_lla_pos["lat_tk"])
    latitude_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(pos_frame, text="Longitude").grid(row=2, column=0, padx=10, pady=10)

    longitude_entry = tk.Entry(pos_frame, textvariable=delay_control.balloon_lla_pos["lon_tk"])
    longitude_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(pos_frame, text="Altitude").grid(row=3, column=0, padx=10, pady=10)

    altitude_entry = tk.Entry(pos_frame, textvariable=delay_control.balloon_lla_pos["alt_tk"])
    altitude_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Button(main_frame, text="Save and Exit", command=partial(save_and_exit, top, delay_control)).grid(row=2, column=0, padx=10, pady=10)
